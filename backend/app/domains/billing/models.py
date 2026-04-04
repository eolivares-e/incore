"""SQLAlchemy models for the Billing domain."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.enums import InvoiceStatus, PaymentMethod, PaymentStatus

if TYPE_CHECKING:
    from app.domains.policies.models import Policy


class Invoice(Base):
    """Invoice model.

    Represents a billing invoice for an insurance policy with support
    for partial payments and overdue tracking.
    """

    __tablename__ = "invoices"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Invoice Identification
    invoice_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Format: INV-YYYYMMDD-XXXX",
    )

    # Foreign Key to Policy
    policy_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Financial Details
    amount_due: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Total amount to be paid",
    )

    amount_paid: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Amount paid so far (supports partial payments)",
    )

    # Dates
    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    paid_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="Date when invoice was fully paid",
    )

    # Status
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, name="invoice_status_enum", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=InvoiceStatus.PENDING,
        index=True,
    )

    # Additional Info
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    policy: Mapped["Policy"] = relationship(
        "Policy",
        back_populates="invoices",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="Payment.payment_date.desc()",
    )

    # Indexes (composite)
    __table_args__ = (
        CheckConstraint("amount_due > 0", name="check_invoice_amount_due_positive"),
        CheckConstraint(
            "amount_paid >= 0", name="check_invoice_amount_paid_non_negative"
        ),
        CheckConstraint(
            "amount_paid <= amount_due",
            name="check_invoice_amount_paid_not_exceeds_due",
        ),
        Index("ix_invoices_policy_status", "policy_id", "status"),
        Index("ix_invoices_status_due_date", "status", "due_date"),
    )

    # Properties
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        if self.status in [
            InvoiceStatus.PAID,
            InvoiceStatus.CANCELLED,
            InvoiceStatus.REFUNDED,
        ]:
            return False
        return self.due_date < date.today()

    @property
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.status == InvoiceStatus.PAID

    @property
    def amount_remaining(self) -> Decimal:
        """Calculate remaining amount to be paid."""
        return self.amount_due - self.amount_paid

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<Invoice(id={self.id}, invoice_number='{self.invoice_number}', "
            f"amount_due={self.amount_due}, status='{self.status.value}')>"
        )


class Payment(Base):
    """Payment model.

    Represents a payment transaction against an invoice, with support
    for Stripe integration and refunds.
    """

    __tablename__ = "payments"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Foreign Key to Invoice
    invoice_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Payment Details
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method_enum", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    payment_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    # Transaction References
    transaction_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="Internal transaction ID",
    )

    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="Stripe PaymentIntent ID (e.g., pi_...)",
    )

    stripe_charge_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Stripe Charge ID (e.g., ch_...)",
    )

    # Status
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status_enum", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PaymentStatus.PENDING,
        index=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for payment failure",
    )

    # Metadata
    payment_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Store Stripe webhook data and additional info",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship(
        "Invoice",
        back_populates="payments",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("amount > 0", name="check_payment_amount_positive"),
    )

    # Properties
    @property
    def is_successful(self) -> bool:
        """Check if payment was successful."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_refundable(self) -> bool:
        """Check if payment can be refunded (within 30 days)."""
        if self.status != PaymentStatus.COMPLETED:
            return False

        days_since_payment = (datetime.utcnow() - self.payment_date).days
        return days_since_payment <= 30

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<Payment(id={self.id}, invoice_id={self.invoice_id}, "
            f"amount={self.amount}, status='{self.status.value}')>"
        )
