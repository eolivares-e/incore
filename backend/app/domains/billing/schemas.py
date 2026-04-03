"""Pydantic schemas for the Billing domain."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.shared.enums import InvoiceStatus, PaymentMethod, PaymentStatus
from app.shared.schemas.base import PaginatedResponse

# ============================================================================
# Invoice Schemas
# ============================================================================


class InvoiceCreate(BaseModel):
    """Schema for creating a new invoice."""

    policy_id: UUID = Field(..., description="Policy ID this invoice belongs to")
    amount_due: Decimal = Field(
        ..., gt=0, description="Total amount to be paid", decimal_places=2
    )
    due_date: date = Field(..., description="Payment due date")
    notes: str | None = Field(None, max_length=1000, description="Optional notes")

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: date) -> date:
        """Validate that due_date is not in the past."""
        if v < date.today():
            raise ValueError("due_date cannot be in the past")
        return v


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""

    amount_due: Decimal | None = Field(
        None, gt=0, description="Total amount to be paid", decimal_places=2
    )
    due_date: date | None = Field(None, description="Payment due date")
    status: InvoiceStatus | None = Field(None, description="Invoice status")
    notes: str | None = Field(None, max_length=1000, description="Optional notes")

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: date | None) -> date | None:
        """Validate that due_date is not in the past."""
        if v is not None and v < date.today():
            raise ValueError("due_date cannot be in the past")
        return v


class InvoiceResponse(BaseModel):
    """Schema for invoice response."""

    id: UUID
    invoice_number: str
    policy_id: UUID
    amount_due: Decimal
    amount_paid: Decimal
    amount_remaining: Decimal
    due_date: date
    paid_date: date | None
    status: InvoiceStatus
    is_overdue: bool
    is_paid: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvoiceListResponse(PaginatedResponse):
    """Paginated response for invoice list."""

    items: list[InvoiceResponse]


class InvoiceFilterParams(BaseModel):
    """Filter parameters for invoice queries."""

    policy_id: UUID | None = Field(None, description="Filter by policy ID")
    status: InvoiceStatus | None = Field(None, description="Filter by status")
    overdue_only: bool = Field(False, description="Show only overdue invoices")
    min_amount: Decimal | None = Field(
        None, ge=0, description="Minimum amount due", decimal_places=2
    )
    max_amount: Decimal | None = Field(
        None, ge=0, description="Maximum amount due", decimal_places=2
    )
    due_before: date | None = Field(None, description="Due date before this date")
    due_after: date | None = Field(None, description="Due date after this date")


# ============================================================================
# Payment Schemas
# ============================================================================


class PaymentCreate(BaseModel):
    """Schema for creating a payment (internal use)."""

    invoice_id: UUID = Field(..., description="Invoice ID this payment is for")
    amount: Decimal = Field(..., gt=0, description="Payment amount", decimal_places=2)
    payment_method: PaymentMethod = Field(..., description="Payment method")
    stripe_payment_intent_id: str | None = Field(
        None, max_length=100, description="Stripe PaymentIntent ID"
    )
    stripe_charge_id: str | None = Field(
        None, max_length=100, description="Stripe Charge ID"
    )
    payment_metadata: dict | None = Field(None, description="Additional metadata")


class PaymentUpdate(BaseModel):
    """Schema for updating a payment."""

    status: PaymentStatus | None = Field(None, description="Payment status")
    failure_reason: str | None = Field(
        None, max_length=500, description="Reason for payment failure"
    )
    stripe_charge_id: str | None = Field(
        None, max_length=100, description="Stripe Charge ID"
    )
    payment_metadata: dict | None = Field(None, description="Additional metadata")


class PaymentResponse(BaseModel):
    """Schema for payment response."""

    id: UUID
    invoice_id: UUID
    amount: Decimal
    payment_method: PaymentMethod
    payment_date: datetime
    transaction_id: str | None
    stripe_payment_intent_id: str | None
    stripe_charge_id: str | None
    status: PaymentStatus
    failure_reason: str | None
    is_successful: bool
    is_refundable: bool
    payment_metadata: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentListResponse(PaginatedResponse):
    """Paginated response for payment list."""

    items: list[PaymentResponse]


# ============================================================================
# Stripe Integration Schemas
# ============================================================================


class StripePaymentIntentCreate(BaseModel):
    """Schema for creating a Stripe PaymentIntent."""

    invoice_id: UUID = Field(..., description="Invoice ID to pay")
    amount: Decimal = Field(..., gt=0, description="Payment amount", decimal_places=2)
    return_url: str | None = Field(
        None, description="URL to redirect after payment completion"
    )

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate amount has max 2 decimal places."""
        if v.as_tuple().exponent < -2:
            raise ValueError("Amount must have at most 2 decimal places")
        return v


class StripePaymentIntentResponse(BaseModel):
    """Schema for Stripe PaymentIntent response."""

    payment_intent_id: str = Field(..., description="Stripe PaymentIntent ID")
    client_secret: str = Field(
        ..., description="Client secret for confirming payment on frontend"
    )
    amount: Decimal = Field(..., description="Payment amount")
    status: str = Field(..., description="PaymentIntent status")
    invoice_id: UUID = Field(..., description="Invoice ID this payment is for")


class RefundRequest(BaseModel):
    """Schema for refund request."""

    reason: str | None = Field(None, max_length=500, description="Reason for refund")
