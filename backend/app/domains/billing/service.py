"""Service layer for Billing domain.

This module implements business logic for billing and payment processing,
including Stripe integration.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

import stripe
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import InsuranceCoreError
from app.domains.billing.models import Invoice, Payment
from app.domains.billing.repository import InvoiceRepository, PaymentRepository
from app.domains.billing.schemas import (
    InvoiceCreate,
    InvoiceFilterParams,
    InvoiceUpdate,
    PaymentCreate,
    PaymentUpdate,
    RefundRequest,
    StripePaymentIntentCreate,
    StripePaymentIntentResponse,
)
from app.shared.enums import InvoiceStatus, PaymentMethod, PaymentStatus

# ============================================================================
# Payment Provider Interface
# ============================================================================


class PaymentProvider(ABC):
    """Abstract interface for payment providers."""

    @abstractmethod
    async def create_payment_intent(
        self, amount: Decimal, currency: str = "usd", metadata: dict | None = None
    ) -> dict:
        """Create a payment intent.

        Args:
            amount: Amount to charge
            currency: Currency code
            metadata: Additional metadata

        Returns:
            Payment intent data
        """
        pass

    @abstractmethod
    async def retrieve_payment_intent(self, payment_intent_id: str) -> dict:
        """Retrieve a payment intent.

        Args:
            payment_intent_id: PaymentIntent ID

        Returns:
            Payment intent data
        """
        pass

    @abstractmethod
    async def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
    ) -> dict:
        """Refund a payment.

        Args:
            payment_intent_id: PaymentIntent ID to refund
            amount: Amount to refund (None for full refund)
            reason: Reason for refund

        Returns:
            Refund data
        """
        pass

    @abstractmethod
    def verify_webhook_signature(
        self, payload: bytes, signature: str, secret: str
    ) -> dict:
        """Verify webhook signature.

        Args:
            payload: Webhook payload
            signature: Webhook signature
            secret: Webhook secret

        Returns:
            Parsed webhook event
        """
        pass


# ============================================================================
# Stripe Provider Implementation
# ============================================================================


class StripeProvider(PaymentProvider):
    """Stripe payment provider implementation."""

    def __init__(self):
        """Initialize Stripe provider."""
        stripe.api_key = settings.STRIPE_SECRET_KEY

    async def create_payment_intent(
        self, amount: Decimal, currency: str = "usd", metadata: dict | None = None
    ) -> dict:
        """Create a Stripe PaymentIntent.

        Args:
            amount: Amount to charge in dollars
            currency: Currency code
            metadata: Additional metadata

        Returns:
            PaymentIntent data
        """
        try:
            # Convert to cents (Stripe uses smallest currency unit)
            amount_cents = int(amount * 100)

            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
            )

            return {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount,
                "status": payment_intent.status,
            }
        except stripe.StripeError as e:
            raise InsuranceCoreError(
                message="Failed to create payment intent",
                status_code=400,
                details={"stripe_error": str(e)},
            )

    async def retrieve_payment_intent(self, payment_intent_id: str) -> dict:
        """Retrieve a Stripe PaymentIntent.

        Args:
            payment_intent_id: PaymentIntent ID

        Returns:
            PaymentIntent data
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            # Extract card type if available
            payment_method = None
            if payment_intent.charges and payment_intent.charges.data:
                charge = payment_intent.charges.data[0]
                if charge.payment_method_details and charge.payment_method_details.card:
                    card_funding = charge.payment_method_details.card.funding
                    # Map Stripe funding type to our enum
                    payment_method = (
                        PaymentMethod.DEBIT_CARD
                        if card_funding == "debit"
                        else PaymentMethod.CREDIT_CARD
                    )

            return {
                "id": payment_intent.id,
                "amount": Decimal(str(payment_intent.amount / 100)),
                "status": payment_intent.status,
                "payment_method": payment_method,
                "charge_id": (
                    payment_intent.charges.data[0].id
                    if payment_intent.charges and payment_intent.charges.data
                    else None
                ),
                "metadata": payment_intent.metadata,
            }
        except stripe.StripeError as e:
            raise InsuranceCoreError(
                message="Failed to retrieve payment intent",
                status_code=400,
                details={"stripe_error": str(e)},
            )

    async def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
    ) -> dict:
        """Refund a Stripe payment.

        Args:
            payment_intent_id: PaymentIntent ID to refund
            amount: Amount to refund in dollars (None for full refund)
            reason: Reason for refund

        Returns:
            Refund data
        """
        try:
            refund_params = {"payment_intent": payment_intent_id}

            if amount is not None:
                refund_params["amount"] = int(amount * 100)

            if reason:
                refund_params["metadata"] = {"reason": reason}

            refund = stripe.Refund.create(**refund_params)

            return {
                "id": refund.id,
                "amount": Decimal(str(refund.amount / 100)),
                "status": refund.status,
                "reason": reason,
            }
        except stripe.StripeError as e:
            raise InsuranceCoreError(
                message="Failed to refund payment",
                status_code=400,
                details={"stripe_error": str(e)},
            )

    def verify_webhook_signature(
        self, payload: bytes, signature: str, secret: str
    ) -> dict:
        """Verify Stripe webhook signature.

        Args:
            payload: Webhook payload
            signature: Webhook signature header
            secret: Webhook secret

        Returns:
            Parsed webhook event

        Raises:
            InsuranceCoreError: If signature verification fails
        """
        try:
            event = stripe.Webhook.construct_event(payload, signature, secret)
            return event
        except stripe.SignatureVerificationError as e:
            raise InsuranceCoreError(
                message="Invalid webhook signature",
                status_code=400,
                details={"error": str(e)},
            )


# ============================================================================
# Billing Service
# ============================================================================


class BillingService:
    """Service for managing invoices."""

    def __init__(self, session: AsyncSession):
        """Initialize billing service.

        Args:
            session: Database session
        """
        self.session = session
        self.invoice_repo = InvoiceRepository(session)

    async def create_invoice(self, data: InvoiceCreate) -> Invoice:
        """Create a new invoice.

        Args:
            data: Invoice creation data

        Returns:
            Created invoice

        Raises:
            InsuranceCoreError: If creation fails
        """
        try:
            invoice = await self.invoice_repo.create(data)
            return invoice
        except Exception as e:
            raise InsuranceCoreError(
                message="Failed to create invoice",
                status_code=400,
                details={"error": str(e)},
            )

    async def get_invoice(self, invoice_id: UUID) -> Invoice:
        """Get invoice by ID.

        Args:
            invoice_id: Invoice ID

        Returns:
            Invoice instance

        Raises:
            InsuranceCoreError: If invoice not found
        """
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise InsuranceCoreError(
                message=f"Invoice not found: {invoice_id}",
                status_code=404,
                details={},
            )
        return invoice

    async def get_invoice_by_number(self, invoice_number: str) -> Invoice:
        """Get invoice by invoice number.

        Args:
            invoice_number: Invoice number

        Returns:
            Invoice instance

        Raises:
            InsuranceCoreError: If invoice not found
        """
        invoice = await self.invoice_repo.get_by_invoice_number(invoice_number)
        if not invoice:
            raise InsuranceCoreError(
                message=f"Invoice not found: {invoice_number}",
                status_code=404,
                details={},
            )
        return invoice

    async def list_invoices(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[InvoiceFilterParams] = None,
    ) -> tuple[list[Invoice], int]:
        """List invoices with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            filters: Filter parameters

        Returns:
            Tuple of (invoices, total count)
        """
        return await self.invoice_repo.get_all(skip=skip, limit=limit, filters=filters)

    async def get_invoices_by_policy(
        self, policy_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Invoice], int]:
        """Get invoices for a specific policy.

        Args:
            policy_id: Policy ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Tuple of (invoices, total count)
        """
        return await self.invoice_repo.get_by_policy_id(
            policy_id, skip=skip, limit=limit
        )

    async def get_overdue_invoices(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Invoice], int]:
        """Get overdue invoices.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Tuple of (invoices, total count)
        """
        return await self.invoice_repo.get_overdue_invoices(skip=skip, limit=limit)

    async def update_invoice(self, invoice_id: UUID, data: InvoiceUpdate) -> Invoice:
        """Update an invoice.

        Args:
            invoice_id: Invoice ID
            data: Update data

        Returns:
            Updated invoice

        Raises:
            InsuranceCoreError: If invoice not found or update fails
        """
        invoice = await self.get_invoice(invoice_id)

        # Prevent updating paid invoices
        if invoice.status == InvoiceStatus.PAID and data.status != InvoiceStatus.PAID:
            raise InsuranceCoreError(
                message="Cannot modify a paid invoice",
                status_code=400,
                details={},
            )

        return await self.invoice_repo.update(invoice, data)

    async def delete_invoice(self, invoice_id: UUID) -> None:
        """Delete an invoice.

        Args:
            invoice_id: Invoice ID

        Raises:
            InsuranceCoreError: If invoice not found or has payments
        """
        invoice = await self.get_invoice(invoice_id)

        # Prevent deleting invoices with payments
        if invoice.amount_paid > Decimal("0.00"):
            raise InsuranceCoreError(
                message="Cannot delete invoice with payments",
                status_code=400,
                details={},
            )

        await self.invoice_repo.delete(invoice)


# ============================================================================
# Payment Service
# ============================================================================


class PaymentService:
    """Service for managing payments and Stripe integration."""

    def __init__(
        self, session: AsyncSession, payment_provider: Optional[PaymentProvider] = None
    ):
        """Initialize payment service.

        Args:
            session: Database session
            payment_provider: Payment provider (defaults to Stripe)
        """
        self.session = session
        self.payment_repo = PaymentRepository(session)
        self.invoice_repo = InvoiceRepository(session)
        self.provider = payment_provider or StripeProvider()

    async def create_payment_intent(
        self, data: StripePaymentIntentCreate
    ) -> StripePaymentIntentResponse:
        """Create a Stripe PaymentIntent for an invoice.

        Args:
            data: Payment intent creation data

        Returns:
            Payment intent response

        Raises:
            InsuranceCoreError: If invoice not found or invalid
        """
        # Get invoice
        invoice = await self.invoice_repo.get_by_id(data.invoice_id)
        if not invoice:
            raise InsuranceCoreError(
                message=f"Invoice not found: {data.invoice_id}",
                status_code=404,
                details={},
            )

        # Validate invoice status
        if invoice.status == InvoiceStatus.PAID:
            raise InsuranceCoreError(
                message="Invoice is already paid",
                status_code=400,
                details={},
            )

        # Validate payment amount
        if data.amount > invoice.amount_remaining:
            raise InsuranceCoreError(
                message="Payment amount exceeds remaining balance",
                status_code=400,
                details={
                    "amount": str(data.amount),
                    "remaining": str(invoice.amount_remaining),
                },
            )

        # Create Stripe PaymentIntent
        payment_intent = await self.provider.create_payment_intent(
            amount=data.amount,
            metadata={
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
            },
        )

        # Create pending payment record
        payment_data = PaymentCreate(
            invoice_id=invoice.id,
            amount=data.amount,
            payment_method=PaymentMethod.CREDIT_CARD,  # Will be updated by webhook
            stripe_payment_intent_id=payment_intent["id"],
        )
        await self.payment_repo.create(payment_data)

        return StripePaymentIntentResponse(
            payment_intent_id=payment_intent["id"],
            client_secret=payment_intent["client_secret"],
            amount=payment_intent["amount"],
            status=payment_intent["status"],
            invoice_id=invoice.id,
        )

    async def handle_payment_webhook(self, event: dict) -> None:
        """Handle Stripe webhook events.

        Args:
            event: Stripe webhook event

        Raises:
            InsuranceCoreError: If processing fails
        """
        event_type = event["type"]
        payment_intent_data = event["data"]["object"]

        # Get payment by PaymentIntent ID
        payment = await self.payment_repo.get_by_stripe_payment_intent_id(
            payment_intent_data["id"]
        )
        if not payment:
            # Payment not found, might be external
            return

        # Get invoice
        invoice = await self.invoice_repo.get_by_id(payment.invoice_id)
        if not invoice:
            raise InsuranceCoreError(
                message=f"Invoice not found: {payment.invoice_id}",
                status_code=404,
                details={},
            )

        # Handle different event types
        if event_type == "payment_intent.succeeded":
            # Retrieve full payment intent to get payment method
            pi_data = await self.provider.retrieve_payment_intent(
                payment_intent_data["id"]
            )

            # Update payment status
            update_data = PaymentUpdate(
                status=PaymentStatus.COMPLETED,
                stripe_charge_id=pi_data.get("charge_id"),
                metadata={"webhook_event": event_type, "event_id": event["id"]},
            )

            # Update payment method if available
            if pi_data.get("payment_method"):
                payment.payment_method = pi_data["payment_method"]

            await self.payment_repo.update(payment, update_data)

            # Update invoice payment status
            total_paid = invoice.amount_paid + payment.amount
            await self.invoice_repo.update_payment_status(invoice, total_paid)

        elif event_type == "payment_intent.payment_failed":
            # Update payment as failed
            failure_message = payment_intent_data.get("last_payment_error", {}).get(
                "message", "Payment failed"
            )
            update_data = PaymentUpdate(
                status=PaymentStatus.FAILED,
                failure_reason=failure_message,
                metadata={"webhook_event": event_type, "event_id": event["id"]},
            )
            await self.payment_repo.update(payment, update_data)

        elif event_type == "payment_intent.canceled":
            # Update payment as cancelled
            update_data = PaymentUpdate(
                status=PaymentStatus.CANCELLED,
                metadata={"webhook_event": event_type, "event_id": event["id"]},
            )
            await self.payment_repo.update(payment, update_data)

    async def refund_payment(
        self, payment_id: UUID, refund_request: RefundRequest
    ) -> Payment:
        """Refund a payment (full refund only in Phase 6).

        Args:
            payment_id: Payment ID to refund
            refund_request: Refund request data

        Returns:
            Updated payment

        Raises:
            InsuranceCoreError: If payment not found or not refundable
        """
        # Get payment
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise InsuranceCoreError(
                message=f"Payment not found: {payment_id}",
                status_code=404,
                details={},
            )

        # Validate refundability
        if not payment.is_refundable:
            raise InsuranceCoreError(
                message="Payment is not refundable",
                status_code=400,
                details={
                    "status": payment.status.value,
                    "days_since_payment": (
                        datetime.utcnow() - payment.payment_date
                    ).days,
                },
            )

        if not payment.stripe_payment_intent_id:
            raise InsuranceCoreError(
                message="Cannot refund non-Stripe payment",
                status_code=400,
                details={},
            )

        # Process refund via Stripe (full refund only)
        await self.provider.refund_payment(
            payment.stripe_payment_intent_id,
            amount=None,  # Full refund
            reason=refund_request.reason,
        )

        # Update payment status
        update_data = PaymentUpdate(
            status=PaymentStatus.REFUNDED,
            metadata={
                "refund_reason": refund_request.reason,
                "refund_date": datetime.utcnow().isoformat(),
            },
        )
        payment = await self.payment_repo.update(payment, update_data)

        # Update invoice
        invoice = await self.invoice_repo.get_by_id(payment.invoice_id)
        if invoice:
            total_paid = invoice.amount_paid - payment.amount
            await self.invoice_repo.update_payment_status(invoice, total_paid)

        return payment

    async def get_payment(self, payment_id: UUID) -> Payment:
        """Get payment by ID.

        Args:
            payment_id: Payment ID

        Returns:
            Payment instance

        Raises:
            InsuranceCoreError: If payment not found
        """
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise InsuranceCoreError(
                message=f"Payment not found: {payment_id}",
                status_code=404,
                details={},
            )
        return payment

    async def list_payments(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Payment], int]:
        """List payments with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Tuple of (payments, total count)
        """
        return await self.payment_repo.get_all(skip=skip, limit=limit)

    async def get_payments_by_invoice(
        self, invoice_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Payment], int]:
        """Get payments for a specific invoice.

        Args:
            invoice_id: Invoice ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Tuple of (payments, total count)
        """
        return await self.payment_repo.get_by_invoice_id(
            invoice_id, skip=skip, limit=limit
        )
