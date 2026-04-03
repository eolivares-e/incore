"""Repository for Billing data access.

This module implements the Repository pattern for the Billing domain,
providing an abstraction layer over database operations.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.billing.models import Invoice, Payment
from app.domains.billing.schemas import (
    InvoiceCreate,
    InvoiceFilterParams,
    InvoiceUpdate,
    PaymentCreate,
    PaymentUpdate,
)
from app.shared.enums import InvoiceStatus


class InvoiceRepository:
    """Repository for Invoice database operations.

    Implements the Repository pattern to abstract database queries
    and provide a clean interface for data access.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def generate_invoice_number(self) -> str:
        """Generate a unique invoice number.

        Format: INV-YYYYMMDD-XXXX
        Example: INV-20260402-0001

        Returns:
            Generated invoice number
        """
        today = date.today()
        date_prefix = today.strftime("%Y%m%d")
        prefix = f"INV-{date_prefix}"

        # Get count of invoices with this date prefix
        stmt = select(func.count(Invoice.id)).where(
            Invoice.invoice_number.like(f"{prefix}%")
        )
        result = await self.session.execute(stmt)
        count = result.scalar() or 0

        # Generate next number
        sequence = str(count + 1).zfill(4)
        return f"{prefix}-{sequence}"

    async def create(self, data: InvoiceCreate) -> Invoice:
        """Create a new invoice.

        Args:
            data: Invoice creation data

        Returns:
            Created Invoice instance
        """
        invoice_number = await self.generate_invoice_number()
        invoice_data = data.model_dump()

        invoice = Invoice(**invoice_data, invoice_number=invoice_number)

        self.session.add(invoice)
        await self.session.commit()
        await self.session.refresh(invoice)
        return invoice

    async def get_by_id(self, invoice_id: UUID) -> Optional[Invoice]:
        """Get an invoice by ID.

        Args:
            invoice_id: UUID of the invoice

        Returns:
            Invoice instance if found, None otherwise
        """
        stmt = select(Invoice).where(Invoice.id == invoice_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_invoice_number(self, invoice_number: str) -> Optional[Invoice]:
        """Get an invoice by invoice number.

        Args:
            invoice_number: Invoice number

        Returns:
            Invoice instance if found, None otherwise
        """
        stmt = select(Invoice).where(Invoice.invoice_number == invoice_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[InvoiceFilterParams] = None,
    ) -> tuple[list[Invoice], int]:
        """Get all invoices with optional filtering and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filter parameters

        Returns:
            Tuple of (list of invoices, total count)
        """
        # Build base query
        stmt = select(Invoice)
        conditions = []

        if filters:
            if filters.policy_id:
                conditions.append(Invoice.policy_id == filters.policy_id)
            if filters.status:
                conditions.append(Invoice.status == filters.status)
            if filters.min_amount:
                conditions.append(Invoice.amount_due >= filters.min_amount)
            if filters.max_amount:
                conditions.append(Invoice.amount_due <= filters.max_amount)
            if filters.due_before:
                conditions.append(Invoice.due_date < filters.due_before)
            if filters.due_after:
                conditions.append(Invoice.due_date > filters.due_after)
            if filters.overdue_only:
                conditions.append(Invoice.due_date < date.today())
                conditions.append(
                    Invoice.status.notin_(
                        [
                            InvoiceStatus.PAID,
                            InvoiceStatus.CANCELLED,
                            InvoiceStatus.REFUNDED,
                        ]
                    )
                )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        stmt = stmt.order_by(Invoice.created_at.desc()).offset(skip).limit(limit)

        # Execute query
        result = await self.session.execute(stmt)
        invoices = list(result.scalars().all())

        return invoices, total

    async def get_by_policy_id(
        self, policy_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Invoice], int]:
        """Get all invoices for a specific policy.

        Args:
            policy_id: UUID of the policy
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of invoices, total count)
        """
        stmt = select(Invoice).where(Invoice.policy_id == policy_id)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Apply pagination
        stmt = stmt.order_by(Invoice.due_date.desc()).offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        invoices = list(result.scalars().all())

        return invoices, total

    async def get_overdue_invoices(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Invoice], int]:
        """Get all overdue invoices.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of invoices, total count)
        """
        today = date.today()
        stmt = select(Invoice).where(
            and_(
                Invoice.due_date < today,
                Invoice.status.notin_(
                    [
                        InvoiceStatus.PAID,
                        InvoiceStatus.CANCELLED,
                        InvoiceStatus.REFUNDED,
                    ]
                ),
            )
        )

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Apply pagination
        stmt = stmt.order_by(Invoice.due_date.asc()).offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        invoices = list(result.scalars().all())

        return invoices, total

    async def update(self, invoice: Invoice, data: InvoiceUpdate) -> Invoice:
        """Update an invoice.

        Args:
            invoice: Invoice instance to update
            data: Update data

        Returns:
            Updated Invoice instance
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(invoice, field, value)

        await self.session.commit()
        await self.session.refresh(invoice)
        return invoice

    async def update_payment_status(
        self, invoice: Invoice, amount_paid: Decimal
    ) -> Invoice:
        """Update invoice payment status based on amount paid.

        Args:
            invoice: Invoice instance to update
            amount_paid: New total amount paid

        Returns:
            Updated Invoice instance
        """
        invoice.amount_paid = amount_paid

        # Update status based on payment
        if amount_paid >= invoice.amount_due:
            invoice.status = InvoiceStatus.PAID
            invoice.paid_date = date.today()
        elif amount_paid > Decimal("0.00"):
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        else:
            invoice.status = InvoiceStatus.PENDING

        await self.session.commit()
        await self.session.refresh(invoice)
        return invoice

    async def delete(self, invoice: Invoice) -> None:
        """Delete an invoice.

        Args:
            invoice: Invoice instance to delete
        """
        await self.session.delete(invoice)
        await self.session.commit()


class PaymentRepository:
    """Repository for Payment database operations.

    Implements the Repository pattern to abstract database queries
    and provide a clean interface for data access.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, data: PaymentCreate) -> Payment:
        """Create a new payment.

        Args:
            data: Payment creation data

        Returns:
            Created Payment instance
        """
        payment_data = data.model_dump()
        payment = Payment(**payment_data)

        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def get_by_id(self, payment_id: UUID) -> Optional[Payment]:
        """Get a payment by ID.

        Args:
            payment_id: UUID of the payment

        Returns:
            Payment instance if found, None otherwise
        """
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_stripe_payment_intent_id(
        self, stripe_payment_intent_id: str
    ) -> Optional[Payment]:
        """Get a payment by Stripe PaymentIntent ID.

        Args:
            stripe_payment_intent_id: Stripe PaymentIntent ID

        Returns:
            Payment instance if found, None otherwise
        """
        stmt = select(Payment).where(
            Payment.stripe_payment_intent_id == stripe_payment_intent_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Payment], int]:
        """Get all payments with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of payments, total count)
        """
        stmt = select(Payment)

        # Get total count
        count_stmt = select(func.count()).select_from(Payment)
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Apply pagination
        stmt = stmt.order_by(Payment.payment_date.desc()).offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        payments = list(result.scalars().all())

        return payments, total

    async def get_by_invoice_id(
        self, invoice_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Payment], int]:
        """Get all payments for a specific invoice.

        Args:
            invoice_id: UUID of the invoice
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of payments, total count)
        """
        stmt = select(Payment).where(Payment.invoice_id == invoice_id)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Apply pagination
        stmt = stmt.order_by(Payment.payment_date.desc()).offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        payments = list(result.scalars().all())

        return payments, total

    async def update(self, payment: Payment, data: PaymentUpdate) -> Payment:
        """Update a payment.

        Args:
            payment: Payment instance to update
            data: Update data

        Returns:
            Updated Payment instance
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)

        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def delete(self, payment: Payment) -> None:
        """Delete a payment.

        Args:
            payment: Payment instance to delete
        """
        await self.session.delete(payment)
        await self.session.commit()
