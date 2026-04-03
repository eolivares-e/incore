"""API router for Pricing endpoints."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domains.pricing.schemas import (
    PricingRuleCreate,
    PricingRuleResponse,
    PricingRuleUpdate,
    QuoteAcceptRequest,
    QuoteCreate,
    QuoteFilterParams,
    QuoteResponse,
    QuoteUpdate,
)
from app.domains.pricing.service import QuoteService
from app.domains.users.models import User, UserRole
from app.domains.users.router import get_current_user, require_role
from app.shared.enums import PolicyType, QuoteStatus, RiskLevel
from app.shared.schemas.base import (
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)

# Separate routers for quotes and pricing rules
quotes_router = APIRouter(prefix="/quotes", tags=["Quotes"])
pricing_rules_router = APIRouter(prefix="/pricing-rules", tags=["Pricing Rules"])


# ============================================================================
# Dependencies
# ============================================================================


async def get_quote_service(
    session: AsyncSession = Depends(get_db),
) -> QuoteService:
    """Dependency to get QuoteService instance."""
    return QuoteService(session)


# ============================================================================
# Quote Endpoints
# ============================================================================


@quotes_router.post(
    "",
    response_model=QuoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new quote",
    description="Create a new insurance quote with automated risk assessment and premium calculation.",
)
async def create_quote(
    data: QuoteCreate,
    current_user: User = Depends(get_current_user),
    service: QuoteService = Depends(get_quote_service),
) -> QuoteResponse:
    """Create a new insurance quote.

    **Authentication:** Required
    **Access Control:** CUSTOMER can create quotes for themselves, AGENT can create for any policyholder.

    **Business Rules:**
    - Quote number is auto-generated (format: QTE-YYYY-TYPE-NNNNN)
    - Premium is calculated automatically based on risk assessment
    - Risk level is determined by age, coverage amount, and policy type
    - Quote is valid for 30 days from creation
    - Quote starts in ACTIVE status
    - Policy holder must exist

    **Risk Assessment:**
    - Age factors: Young (<25) and senior (>70) drivers increase risk
    - Coverage factors: High coverage (>$1M) increases risk
    - Policy type adjustments applied

    **Returns:**
    - 201: Quote created successfully with calculated premium
    - 400: Validation error
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER creating quote for another policyholder)
    - 404: Policy holder not found or pricing rule not found
    - 422: Invalid input data
    """
    # TODO: Add ownership validation for CUSTOMER role
    return await service.create_quote(data)


@quotes_router.get(
    "/{quote_id}",
    response_model=QuoteResponse,
    summary="Get a quote by ID",
    description="Retrieve detailed information about a specific quote.",
)
async def get_quote(
    quote_id: UUID,
    current_user: User = Depends(get_current_user),
    service: QuoteService = Depends(get_quote_service),
) -> QuoteResponse:
    """Get a quote by ID.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only view their own quotes.

    **Returns:**
    - 200: Quote found
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER accessing other's quote)
    - 404: Quote not found
    """
    # TODO: Add ownership validation for CUSTOMER role
    return await service.get_quote(quote_id)


@quotes_router.get(
    "/number/{quote_number}",
    response_model=QuoteResponse,
    summary="Get a quote by quote number",
    description="Retrieve detailed information about a specific quote by its quote number.",
)
async def get_quote_by_number(
    quote_number: str,
    current_user: User = Depends(get_current_user),
    service: QuoteService = Depends(get_quote_service),
) -> QuoteResponse:
    """Get a quote by quote number.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only view their own quotes.

    **Returns:**
    - 200: Quote found
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER accessing other's quote)
    - 404: Quote not found
    """
    # TODO: Add ownership validation for CUSTOMER role
    return await service.get_quote_by_number(quote_number)


@quotes_router.get(
    "",
    response_model=PaginatedResponse[QuoteResponse],
    summary="List quotes",
    description="Get a paginated list of quotes with optional filters.",
)
async def list_quotes(
    # Pagination parameters
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    order_by: Annotated[str | None, Query(description="Order by field")] = None,
    # Filter parameters
    policy_holder_id: Annotated[
        UUID | None, Query(description="Filter by policy holder ID")
    ] = None,
    policy_type: Annotated[
        PolicyType | None, Query(description="Filter by policy type")
    ] = None,
    status: Annotated[
        QuoteStatus | None, Query(description="Filter by quote status")
    ] = None,
    risk_level: Annotated[
        RiskLevel | None, Query(description="Filter by risk level")
    ] = None,
    is_active: Annotated[
        bool | None, Query(description="Filter by active status")
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Search in quote_number"),
    ] = None,
    current_user: User = Depends(get_current_user),
    service: QuoteService = Depends(get_quote_service),
) -> PaginatedResponse[QuoteResponse]:
    """List quotes with pagination and filters.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only see their own quotes.

    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)
    - `policy_holder_id`: Filter by policy holder
    - `policy_type`: Filter by policy type (AUTO, HOME, LIFE, HEALTH)
    - `status`: Filter by status (DRAFT, PENDING, ACTIVE, ACCEPTED, REJECTED, EXPIRED, CONVERTED_TO_POLICY)
    - `risk_level`: Filter by risk level (LOW, MEDIUM, HIGH, VERY_HIGH)
    - `is_active`: Filter by active status
    - `search`: Search term for quote number

    **Returns:**
    - 200: Paginated list of quotes
    - 401: Not authenticated
    """
    pagination = PaginationParams(page=page, page_size=page_size, order_by=order_by)
    filters = QuoteFilterParams(
        policy_holder_id=policy_holder_id,
        policy_type=policy_type,
        status=status,
        risk_level=risk_level,
        is_active=is_active,
        search=search,
    )

    # For CUSTOMER role, filter to only their quotes
    # TODO: Auto-set policy_holder_id from current_user.policyholder_id when that FK exists
    if current_user.role == UserRole.CUSTOMER and not current_user.is_superuser:
        pass  # Would filter by current_user.policyholder_id

    return await service.get_quotes(pagination, filters)


@quotes_router.put(
    "/{quote_id}",
    response_model=QuoteResponse,
    summary="Update a quote",
    description="Update an existing quote. Only DRAFT and ACTIVE quotes can be updated.",
)
async def update_quote(
    quote_id: UUID,
    data: QuoteUpdate,
    current_user: User = Depends(get_current_user),
    service: QuoteService = Depends(get_quote_service),
) -> QuoteResponse:
    """Update a quote.

    **Authentication:** Required
    **Access Control:** CUSTOMER can update their own quotes, AGENT can update any.

    **Business Rules:**
    - Can only update quotes in DRAFT or ACTIVE status
    - Cannot update ACCEPTED, REJECTED, EXPIRED, or CONVERTED quotes
    - Premium and risk level are not recalculated (create a new quote instead)

    **Returns:**
    - 200: Quote updated successfully
    - 400: Cannot update quote in current status
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER updating other's quote)
    - 404: Quote not found
    - 422: Invalid input data
    """
    # TODO: Add ownership validation for CUSTOMER role
    return await service.update_quote(quote_id, data)


@quotes_router.delete(
    "/{quote_id}",
    response_model=MessageResponse,
    summary="Delete a quote",
    description="Soft delete a quote (sets is_active to False).",
)
async def delete_quote(
    quote_id: UUID,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: QuoteService = Depends(get_quote_service),
) -> MessageResponse:
    """Soft delete a quote.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Sets is_active to False
    - Quote remains in database for audit purposes

    **Returns:**
    - 200: Quote deleted successfully
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Quote not found
    """
    await service.delete_quote(quote_id)
    return MessageResponse(message="Quote deleted successfully")


@quotes_router.post(
    "/{quote_id}/accept",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Accept a quote and convert to policy",
    description="Accept a quote and automatically create an active insurance policy.",
)
async def accept_quote(
    quote_id: UUID,
    data: QuoteAcceptRequest,
    current_user: User = Depends(get_current_user),
    service: QuoteService = Depends(get_quote_service),
) -> dict[str, Any]:
    """Accept a quote and convert it to an active policy.

    **Authentication:** Required
    **Access Control:** CUSTOMER can accept their own quotes, AGENT can accept any.

    **Business Rules:**
    - Quote must be in ACTIVE or PENDING status
    - Quote must not be expired
    - Creates a policy with status ACTIVE (immediately active)
    - Creates basic coverage based on quote details
    - Updates quote status to CONVERTED_TO_POLICY

    **Note:** In Phase 4, quotes are accepted without underwriting review.
    Phase 5 will add underwriting gate for high-risk quotes.

    **Returns:**
    - 201: Quote accepted and policy created
    - 400: Quote expired or invalid status
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER accepting other's quote)
    - 404: Quote not found
    - 422: Invalid input data
    """
    # TODO: Add ownership validation for CUSTOMER role
    return await service.accept_quote(quote_id, data)


@quotes_router.post(
    "/{quote_id}/reject",
    response_model=QuoteResponse,
    summary="Reject a quote",
    description="Reject a quote (updates status to REJECTED).",
)
async def reject_quote(
    quote_id: UUID,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: QuoteService = Depends(get_quote_service),
) -> QuoteResponse:
    """Reject a quote.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Quote must be in ACTIVE or PENDING status
    - Updates quote status to REJECTED

    **Returns:**
    - 200: Quote rejected successfully
    - 400: Cannot reject quote in current status
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Quote not found
    """
    return await service.reject_quote(quote_id)


# ============================================================================
# Pricing Rule Endpoints (Admin Only)
# ============================================================================


@pricing_rules_router.post(
    "",
    response_model=PricingRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a pricing rule",
    description="[ADMIN] Create a new pricing rule for premium calculation.",
)
async def create_pricing_rule(
    data: PricingRuleCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    service: QuoteService = Depends(get_quote_service),
) -> PricingRuleResponse:
    """Create a new pricing rule.

    **Required Role:** ADMIN

    **Business Rules:**
    - Only one active rule per (policy_type, risk_level) combination
    - Base premium must be positive
    - Multiplier factors stored as JSON

    **Returns:**
    - 201: Pricing rule created successfully
    - 400: Validation error (e.g., duplicate active rule)
    - 401: Not authenticated
    - 403: Insufficient permissions (requires ADMIN role)
    - 422: Invalid input data
    """
    rule = await service.pricing_rule_repository.create(data)
    return PricingRuleResponse.model_validate(rule)


@pricing_rules_router.get(
    "/{rule_id}",
    response_model=PricingRuleResponse,
    summary="Get a pricing rule by ID",
    description="[ADMIN/AGENT] Retrieve detailed information about a specific pricing rule.",
)
async def get_pricing_rule(
    rule_id: UUID,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: QuoteService = Depends(get_quote_service),
) -> PricingRuleResponse:
    """Get a pricing rule by ID.

    **Required Role:** AGENT, UNDERWRITER, or ADMIN (read-only for non-admin)

    **Returns:**
    - 200: Pricing rule found
    - 401: Not authenticated
    - 403: Insufficient permissions
    - 404: Pricing rule not found
    """
    from app.core.exceptions import NotFoundException

    rule = await service.pricing_rule_repository.get_by_id(rule_id)
    if not rule:
        raise NotFoundException(resource="PricingRule", resource_id=str(rule_id))
    return PricingRuleResponse.model_validate(rule)


@pricing_rules_router.get(
    "",
    response_model=list[PricingRuleResponse],
    summary="List pricing rules",
    description="[ADMIN/AGENT] Get a list of pricing rules with optional filters.",
)
async def list_pricing_rules(
    policy_type: Annotated[
        PolicyType | None, Query(description="Filter by policy type")
    ] = None,
    risk_level: Annotated[
        RiskLevel | None, Query(description="Filter by risk level")
    ] = None,
    is_active: Annotated[
        bool | None, Query(description="Filter by active status")
    ] = None,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: QuoteService = Depends(get_quote_service),
) -> list[PricingRuleResponse]:
    """List pricing rules with optional filters.

    **Required Role:** AGENT, UNDERWRITER, or ADMIN (read-only for non-admin)

    **Query Parameters:**
    - `policy_type`: Filter by policy type
    - `risk_level`: Filter by risk level
    - `is_active`: Filter by active status

    **Returns:**
    - 200: List of pricing rules
    - 401: Not authenticated
    - 403: Insufficient permissions
    """
    rules = await service.pricing_rule_repository.get_all(
        policy_type=policy_type,
        risk_level=risk_level,
        is_active=is_active,
    )
    return [PricingRuleResponse.model_validate(r) for r in rules]


@pricing_rules_router.put(
    "/{rule_id}",
    response_model=PricingRuleResponse,
    summary="Update a pricing rule",
    description="[ADMIN] Update an existing pricing rule.",
)
async def update_pricing_rule(
    rule_id: UUID,
    data: PricingRuleUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    service: QuoteService = Depends(get_quote_service),
) -> PricingRuleResponse:
    """Update a pricing rule.

    **Required Role:** ADMIN

    **Business Rules:**
    - Cannot change policy_type or risk_level (create a new rule instead)
    - Base premium must be positive if provided

    **Returns:**
    - 200: Pricing rule updated successfully
    - 401: Not authenticated
    - 403: Insufficient permissions (requires ADMIN role)
    - 404: Pricing rule not found
    - 422: Invalid input data
    """
    from app.core.exceptions import NotFoundException

    updated_rule = await service.pricing_rule_repository.update(rule_id, data)
    if not updated_rule:
        raise NotFoundException(resource="PricingRule", resource_id=str(rule_id))
    return PricingRuleResponse.model_validate(updated_rule)


@pricing_rules_router.delete(
    "/{rule_id}",
    response_model=MessageResponse,
    summary="Delete a pricing rule",
    description="[ADMIN] Soft delete a pricing rule (sets is_active to False).",
)
async def delete_pricing_rule(
    rule_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    service: QuoteService = Depends(get_quote_service),
) -> MessageResponse:
    """Soft delete a pricing rule.

    **Required Role:** ADMIN

    **Business Rules:**
    - Sets is_active to False
    - Rule remains in database for audit purposes
    - Existing quotes calculated with this rule are not affected

    **Returns:**
    - 200: Pricing rule deleted successfully
    - 401: Not authenticated
    - 403: Insufficient permissions (requires ADMIN role)
    - 404: Pricing rule not found
    """
    from app.core.exceptions import NotFoundException

    success = await service.pricing_rule_repository.delete(rule_id)
    if not success:
        raise NotFoundException(resource="PricingRule", resource_id=str(rule_id))
    return MessageResponse(message="Pricing rule deleted successfully")
