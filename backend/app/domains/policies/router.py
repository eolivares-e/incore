"""API router for Policy endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domains.policies.schemas import (
    CoverageCreate,
    CoverageResponse,
    CoverageUpdate,
    PolicyCreate,
    PolicyFilterParams,
    PolicyResponse,
    PolicyUpdate,
)
from app.domains.policies.service import PolicyService
from app.domains.users.models import User, UserRole
from app.domains.users.router import get_current_user, require_role
from app.shared.enums import PolicyStatus, PolicyType
from app.shared.schemas.base import MessageResponse, PaginatedResponse, PaginationParams

router = APIRouter(prefix="/policies", tags=["Policies"])


# Dependency to get the service
async def get_policy_service(
    session: AsyncSession = Depends(get_db),
) -> PolicyService:
    """Dependency to get PolicyService instance."""
    return PolicyService(session)


# ============================================================================
# Policy Endpoints
# ============================================================================


@router.post(
    "",
    response_model=PolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new policy",
    description="Create a new insurance policy with coverages. Policy number is auto-generated.",
)
async def create_policy(
    data: PolicyCreate,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: PolicyService = Depends(get_policy_service),
) -> PolicyResponse:
    """Create a new policy with coverages.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Policy number is auto-generated (format: POL-YYYY-TYPE-NNNNN)
    - Policy starts in DRAFT status
    - At least one coverage must be provided
    - No duplicate coverage types allowed
    - End date must be after start date
    - Policyholder must exist

    **Returns:**
    - 201: Policy created successfully
    - 400: Validation error (e.g., invalid dates, duplicate coverages)
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Policyholder not found
    - 422: Invalid input data
    """
    return await service.create_policy(data)


@router.get(
    "/{policy_id}",
    response_model=PolicyResponse,
    summary="Get a policy by ID",
    description="Retrieve detailed information about a specific policy including coverages.",
)
async def get_policy(
    policy_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PolicyService = Depends(get_policy_service),
) -> PolicyResponse:
    """Get a policy by ID with coverages.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only view their own policies.

    **Returns:**
    - 200: Policy found
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER accessing other's data)
    - 404: Policy not found
    """
    # TODO: Add ownership validation for CUSTOMER role
    return await service.get_policy(policy_id)


@router.get(
    "/number/{policy_number}",
    response_model=PolicyResponse,
    summary="Get a policy by policy number",
    description="Retrieve detailed information about a specific policy by its policy number.",
)
async def get_policy_by_number(
    policy_number: str,
    current_user: User = Depends(get_current_user),
    service: PolicyService = Depends(get_policy_service),
) -> PolicyResponse:
    """Get a policy by policy number with coverages.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only view their own policies.

    **Returns:**
    - 200: Policy found
    - 401: Not authenticated
    - 403: Access denied (CUSTOMER accessing other's data)
    - 404: Policy not found
    """
    # TODO: Add ownership validation for CUSTOMER role
    return await service.get_policy_by_number(policy_number)


@router.get(
    "",
    response_model=PaginatedResponse[PolicyResponse],
    summary="List policies",
    description="Get a paginated list of policies with optional filters.",
)
async def list_policies(
    # Pagination parameters
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    order_by: Annotated[str | None, Query(description="Order by field")] = None,
    # Filter parameters
    policyholder_id: Annotated[
        UUID | None, Query(description="Filter by policyholder ID")
    ] = None,
    policy_type: Annotated[
        PolicyType | None, Query(description="Filter by policy type")
    ] = None,
    status: Annotated[
        PolicyStatus | None, Query(description="Filter by policy status")
    ] = None,
    is_active: Annotated[
        bool | None, Query(description="Filter by active status")
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Search in policy_number"),
    ] = None,
    current_user: User = Depends(get_current_user),
    service: PolicyService = Depends(get_policy_service),
) -> PaginatedResponse[PolicyResponse]:
    """List policies with pagination and filters.

    **Authentication:** Required
    **Access Control:** CUSTOMER can only see their own policies.

    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)
    - `policyholder_id`: Filter by policyholder
    - `policy_type`: Filter by policy type (AUTO, HEALTH, LIFE, HOME, TRAVEL)
    - `status`: Filter by status (DRAFT, ACTIVE, EXPIRED, CANCELLED)
    - `is_active`: Filter by active status
    - `search`: Search term for policy number

    **Returns:**
    - 200: Paginated list of policies
    - 401: Not authenticated
    """
    pagination = PaginationParams(page=page, page_size=page_size, order_by=order_by)
    filters = PolicyFilterParams(
        policyholder_id=policyholder_id,
        policy_type=policy_type,
        status=status,
        is_active=is_active,
        search=search,
    )

    # For CUSTOMER role, filter to only their policies
    # TODO: Auto-set policyholder_id from current_user.policyholder_id when that FK exists
    if current_user.role == UserRole.CUSTOMER and not current_user.is_superuser:
        pass  # Would filter by current_user.policyholder_id

    return await service.get_policies(pagination, filters)


@router.put(
    "/{policy_id}",
    response_model=PolicyResponse,
    summary="Update a policy",
    description="Update policy information. All fields are optional.",
)
async def update_policy(
    policy_id: UUID,
    data: PolicyUpdate,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: PolicyService = Depends(get_policy_service),
) -> PolicyResponse:
    """Update a policy.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Only provided fields will be updated
    - Status transitions must be valid:
      - DRAFT -> ACTIVE, CANCELLED
      - ACTIVE -> EXPIRED, CANCELLED
      - EXPIRED -> (no transitions allowed)
      - CANCELLED -> (no transitions allowed)
    - Cannot update policyholder_id or policy_number

    **Returns:**
    - 200: Policy updated successfully
    - 400: Invalid status transition or validation error
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Policy not found
    - 422: Invalid input data
    """
    return await service.update_policy(policy_id, data)


@router.delete(
    "/{policy_id}",
    response_model=MessageResponse,
    summary="Delete a policy",
    description="Soft delete a policy (sets is_active to False).",
)
async def delete_policy(
    policy_id: UUID,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: PolicyService = Depends(get_policy_service),
) -> MessageResponse:
    """Soft delete a policy.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - This is a soft delete (sets is_active to False)
    - Policy data is preserved in the database

    **Returns:**
    - 200: Policy deleted successfully
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Policy not found
    """
    await service.delete_policy(policy_id)
    return MessageResponse(message="Policy deleted successfully")


@router.post(
    "/{policy_id}/activate",
    response_model=PolicyResponse,
    summary="Activate a policy",
    description="Change policy status from DRAFT to ACTIVE.",
)
async def activate_policy(
    policy_id: UUID,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: PolicyService = Depends(get_policy_service),
) -> PolicyResponse:
    """Activate a policy (DRAFT -> ACTIVE).

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Policy must be in DRAFT status
    - Policy start date must be today or in the future

    **Returns:**
    - 200: Policy activated successfully
    - 400: Policy cannot be activated (wrong status or invalid date)
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Policy not found
    """
    return await service.activate_policy(policy_id)


@router.post(
    "/{policy_id}/cancel",
    response_model=PolicyResponse,
    summary="Cancel a policy",
    description="Change policy status to CANCELLED.",
)
async def cancel_policy(
    policy_id: UUID,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: PolicyService = Depends(get_policy_service),
) -> PolicyResponse:
    """Cancel a policy.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Policy must be in DRAFT or ACTIVE status
    - Cannot cancel EXPIRED or already CANCELLED policies

    **Returns:**
    - 200: Policy cancelled successfully
    - 400: Policy cannot be cancelled (wrong status)
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Policy not found
    """
    return await service.cancel_policy(policy_id)


# ============================================================================
# Coverage Endpoints
# ============================================================================


@router.post(
    "/{policy_id}/coverages",
    response_model=CoverageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add coverage to policy",
    description="Add a new coverage to an existing policy.",
)
async def add_coverage(
    policy_id: UUID,
    data: CoverageCreate,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: PolicyService = Depends(get_policy_service),
) -> CoverageResponse:
    """Add a coverage to a policy.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Policy must exist and be in DRAFT status
    - Coverage type must not already exist on the policy
    - Coverage amount must be positive
    - Deductible must be non-negative

    **Returns:**
    - 201: Coverage added successfully
    - 400: Validation error (e.g., duplicate coverage type, wrong status)
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Policy not found
    - 422: Invalid input data
    """
    return await service.add_coverage(policy_id, data)


@router.put(
    "/coverages/{coverage_id}",
    response_model=CoverageResponse,
    summary="Update a coverage",
    description="Update coverage information. All fields are optional.",
)
async def update_coverage(
    coverage_id: UUID,
    data: CoverageUpdate,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: PolicyService = Depends(get_policy_service),
) -> CoverageResponse:
    """Update a coverage.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Coverage must exist
    - Policy must be in DRAFT status
    - Only provided fields will be updated

    **Returns:**
    - 200: Coverage updated successfully
    - 400: Policy not in DRAFT status
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Coverage not found
    - 422: Invalid input data
    """
    return await service.update_coverage(coverage_id, data)


@router.delete(
    "/coverages/{coverage_id}",
    response_model=MessageResponse,
    summary="Delete a coverage",
    description="Remove a coverage from a policy.",
)
async def delete_coverage(
    coverage_id: UUID,
    current_user: User = Depends(require_role(UserRole.AGENT)),
    service: PolicyService = Depends(get_policy_service),
) -> MessageResponse:
    """Delete a coverage.

    **Required Role:** AGENT or ADMIN

    **Business Rules:**
    - Coverage must exist
    - Policy must be in DRAFT status
    - Policy must have at least 2 coverages (cannot delete the last one)

    **Returns:**
    - 200: Coverage deleted successfully
    - 400: Policy not in DRAFT status or would have no coverages remaining
    - 401: Not authenticated
    - 403: Insufficient permissions (requires AGENT role)
    - 404: Coverage not found
    """
    await service.delete_coverage(coverage_id)
    return MessageResponse(message="Coverage deleted successfully")
