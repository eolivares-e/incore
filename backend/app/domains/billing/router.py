"""API router for Billing endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.domains.billing.schemas import (
    InvoiceCreate,
    InvoiceFilterParams,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceUpdate,
    PaymentListResponse,
    PaymentResponse,
    RefundRequest,
    StripePaymentIntentCreate,
    StripePaymentIntentResponse,
)
from app.domains.billing.service import BillingService, PaymentService
from app.domains.users.models import User, UserRole
from app.domains.users.router import get_current_user, require_role
from app.shared.schemas.base import MessageResponse, PaginationParams

router = APIRouter(prefix="/billing", tags=["Billing"])


# ============================================================================
# Dependencies
# ============================================================================


async def get_billing_service(
    session: AsyncSession = Depends(get_db),
) -> BillingService:
    """Dependency to get BillingService instance."""
    return BillingService(session)


async def get_payment_service(
    session: AsyncSession = Depends(get_db),
) -> PaymentService:
    """Dependency to get PaymentService instance."""
    return PaymentService(session)


# ============================================================================
# Invoice Endpoints
# ============================================================================


@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new invoice",
    description="Create a new invoice for a policy. Invoice number is auto-generated.",
)
async def create_invoice(
    data: InvoiceCreate,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: BillingService = Depends(get_billing_service),
) -> InvoiceResponse:
    """Create a new invoice.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Invoice number is auto-generated (format: INV-YYYYMMDD-XXXX)
    - Due date must not be in the past
    - Policy must exist
    - Initial status is PENDING
    - Amount paid starts at 0.00

    **Returns:**
    - 201: Invoice created successfully
    - 400: Validation error
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Policy not found
    - 422: Invalid input data
    """
    invoice = await service.create_invoice(data)
    return InvoiceResponse.model_validate(invoice)


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Get an invoice by ID",
    description="Retrieve detailed information about a specific invoice.",
)
async def get_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> InvoiceResponse:
    """Get an invoice by ID.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only view their own invoices.

    **Returns:**
    - 200: Invoice found
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER accessing other's invoice)
    - 404: Invoice not found
    """
    # TODO: Add ownership validation for CUSTOMER role
    invoice = await service.get_invoice(invoice_id)
    return InvoiceResponse.model_validate(invoice)


@router.get(
    "/invoices",
    response_model=InvoiceListResponse,
    summary="List all invoices",
    description="List all invoices with optional filtering and pagination.",
)
async def list_invoices(
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[InvoiceFilterParams, Depends()],
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> InvoiceListResponse:
    """List all invoices with pagination and filtering.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only see their own invoices.

    **Query Parameters:**
    - `skip`: Number of records to skip (pagination)
    - `limit`: Maximum number of records to return (max 100)
    - `policy_id`: Filter by policy ID
    - `status`: Filter by invoice status
    - `overdue_only`: Show only overdue invoices
    - `min_amount`: Minimum amount due
    - `max_amount`: Maximum amount due
    - `due_before`: Due date before this date
    - `due_after`: Due date after this date

    **Returns:**
    - 200: List of invoices with pagination metadata
    - 401: Not authenticated
    """
    # TODO: For CUSTOMER role, filter to only their invoices
    invoices, total = await service.list_invoices(
        skip=pagination.offset, limit=pagination.limit, filters=filters
    )

    return InvoiceListResponse(
        items=[InvoiceResponse.model_validate(inv) for inv in invoices],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0,
    )


@router.get(
    "/invoices/policy/{policy_id}",
    response_model=InvoiceListResponse,
    summary="Get invoices for a policy",
    description="Retrieve all invoices for a specific policy.",
)
async def get_invoices_by_policy(
    policy_id: UUID,
    pagination: Annotated[PaginationParams, Depends()],
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> InvoiceListResponse:
    """Get all invoices for a specific policy.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only view invoices for their policies.

    **Returns:**
    - 200: List of invoices for the policy
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER accessing other's policy)
    """
    # TODO: Add ownership validation for CUSTOMER role
    invoices, total = await service.get_invoices_by_policy(
        policy_id, skip=pagination.offset, limit=pagination.limit
    )

    return InvoiceListResponse(
        items=[InvoiceResponse.model_validate(inv) for inv in invoices],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0,
    )


@router.get(
    "/invoices/overdue/list",
    response_model=InvoiceListResponse,
    summary="Get overdue invoices",
    description="Retrieve all overdue invoices.",
)
async def get_overdue_invoices(
    pagination: Annotated[PaginationParams, Depends()],
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: BillingService = Depends(get_billing_service),
) -> InvoiceListResponse:
    """Get all overdue invoices.

    **Required Role:** AGENT, UNDERWRITER, or ADMIN

    **Returns:**
    - 200: List of overdue invoices
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    """
    invoices, total = await service.get_overdue_invoices(
        skip=pagination.offset, limit=pagination.limit
    )

    return InvoiceListResponse(
        items=[InvoiceResponse.model_validate(inv) for inv in invoices],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0,
    )


@router.patch(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Update an invoice",
    description="Update invoice details. Cannot modify paid invoices.",
)
async def update_invoice(
    invoice_id: UUID,
    data: InvoiceUpdate,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: BillingService = Depends(get_billing_service),
) -> InvoiceResponse:
    """Update an invoice.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Cannot modify paid invoices
    - Due date cannot be in the past

    **Returns:**
    - 200: Invoice updated successfully
    - 400: Validation error or invoice is paid
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Invoice not found
    """
    invoice = await service.update_invoice(invoice_id, data)
    return InvoiceResponse.model_validate(invoice)


@router.delete(
    "/invoices/{invoice_id}",
    response_model=MessageResponse,
    summary="Delete an invoice",
    description="Delete an invoice. Cannot delete invoices with payments.",
)
async def delete_invoice(
    invoice_id: UUID,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: BillingService = Depends(get_billing_service),
) -> MessageResponse:
    """Delete an invoice.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Cannot delete invoices with payments (amount_paid > 0)

    **Returns:**
    - 200: Invoice deleted successfully
    - 400: Invoice has payments
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Invoice not found
    """
    await service.delete_invoice(invoice_id)
    return MessageResponse(message="Invoice deleted successfully")


# ============================================================================
# Payment Endpoints
# ============================================================================


@router.post(
    "/payments/create-intent",
    response_model=StripePaymentIntentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a payment intent",
    description="Create a Stripe PaymentIntent for an invoice payment.",
)
async def create_payment_intent(
    data: StripePaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> StripePaymentIntentResponse:
    """Create a Stripe PaymentIntent.

    **Authentication:** Required
    **Access Control:** CUSTOMER can pay their own invoices, AGENT can pay any.

    **Stripe-First Flow:**
    1. Client calls this endpoint to create PaymentIntent
    2. Server creates PaymentIntent via Stripe API
    3. Server creates pending Payment record in database
    4. Client receives client_secret to confirm payment on frontend
    5. Payment is confirmed via Stripe.js on frontend
    6. Stripe sends webhook to update payment status
    7. Invoice payment status is updated automatically

    **Business Rules:**
    - Invoice must exist and not be fully paid
    - Payment amount cannot exceed remaining balance
    - Payment record created in PENDING status
    - Payment method defaults to CREDIT_CARD (updated by webhook)

    **Returns:**
    - 201: PaymentIntent created successfully
    - 400: Invalid request or invoice already paid
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER paying other's invoice)
    - 404: Invoice not found
    """
    # TODO: Add ownership validation for CUSTOMER role
    return await service.create_payment_intent(data)


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
    summary="Get a payment by ID",
    description="Retrieve detailed information about a specific payment.",
)
async def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    """Get a payment by ID.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only view their own payments.

    **Returns:**
    - 200: Payment found
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER accessing other's payment)
    - 404: Payment not found
    """
    # TODO: Add ownership validation for CUSTOMER role
    payment = await service.get_payment(payment_id)
    return PaymentResponse.model_validate(payment)


@router.get(
    "/payments",
    response_model=PaymentListResponse,
    summary="List all payments",
    description="List all payments with pagination.",
)
async def list_payments(
    pagination: Annotated[PaginationParams, Depends()],
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentListResponse:
    """List all payments with pagination.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only see their own payments.

    **Returns:**
    - 200: List of payments with pagination metadata
    - 401: Not authenticated
    """
    # TODO: For CUSTOMER role, filter to only their payments
    payments, total = await service.list_payments(
        skip=pagination.offset, limit=pagination.limit
    )

    return PaymentListResponse(
        items=[PaymentResponse.model_validate(pmt) for pmt in payments],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0,
    )


@router.get(
    "/payments/invoice/{invoice_id}",
    response_model=PaymentListResponse,
    summary="Get payments for an invoice",
    description="Retrieve all payments for a specific invoice.",
)
async def get_payments_by_invoice(
    invoice_id: UUID,
    pagination: Annotated[PaginationParams, Depends()],
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentListResponse:
    """Get all payments for a specific invoice.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only view payments for their invoices.

    **Returns:**
    - 200: List of payments for the invoice
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER accessing other's invoice)
    """
    # TODO: Add ownership validation for CUSTOMER role
    payments, total = await service.get_payments_by_invoice(
        invoice_id, skip=pagination.offset, limit=pagination.limit
    )

    return PaymentListResponse(
        items=[PaymentResponse.model_validate(pmt) for pmt in payments],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0,
    )


@router.post(
    "/payments/{payment_id}/refund",
    response_model=PaymentResponse,
    summary="Refund a payment",
    description="Refund a completed payment (full refund only, within 30 days).",
)
async def refund_payment(
    payment_id: UUID,
    refund_request: RefundRequest,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    """Refund a payment.

    **Required Role:** AGENT or ADMIN

    **Business Rules (Phase 6):**
    - Only full refunds supported in Phase 6
    - Payment must be in COMPLETED status
    - Payment must be within 30-day refund window
    - Only Stripe payments can be refunded
    - Invoice amount_paid is decreased by refund amount
    - Invoice status updated based on remaining balance

    **Returns:**
    - 200: Payment refunded successfully
    - 400: Payment not refundable
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Payment not found
    """
    payment = await service.refund_payment(payment_id, refund_request)
    return PaymentResponse.model_validate(payment)


# ============================================================================
# Stripe Webhook Endpoint
# ============================================================================


@router.post(
    "/webhooks/stripe",
    status_code=status.HTTP_200_OK,
    summary="Stripe webhook handler",
    description="Handle Stripe webhook events for payment status updates.",
)
async def stripe_webhook(
    request: Request,
    stripe_signature: Annotated[str | None, Header(alias="Stripe-Signature")] = None,
    service: PaymentService = Depends(get_payment_service),
) -> MessageResponse:
    """Handle Stripe webhook events.

    **Supported Events:**
    - `payment_intent.succeeded`: Payment completed successfully
    - `payment_intent.payment_failed`: Payment failed
    - `payment_intent.canceled`: Payment canceled

    **Security:**
    - Webhook signature verification using STRIPE_WEBHOOK_SECRET
    - No IP whitelist (signature verification only)

    **Processing:**
    - Updates payment status based on event
    - Updates invoice amount_paid and status
    - Updates payment method from card details
    - Stores webhook metadata in payment record

    **Returns:**
    - 200: Webhook processed successfully
    - 400: Invalid signature or processing error
    """
    if not stripe_signature:
        return MessageResponse(message="Missing signature")

    # Get raw request body
    payload = await request.body()

    # Verify webhook signature and get event
    from app.domains.billing.service import StripeProvider

    provider = StripeProvider()
    event = provider.verify_webhook_signature(
        payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
    )

    # Process webhook event
    await service.handle_payment_webhook(event)

    return MessageResponse(message="Webhook processed successfully")
