"""API router for PolicyHolder endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domains.policy_holders.schemas import (
    PolicyHolderCreate,
    PolicyHolderFilterParams,
    PolicyHolderResponse,
    PolicyHolderUpdate,
)
from app.domains.policy_holders.service import PolicyHolderService
from app.shared.schemas.base import MessageResponse, PaginatedResponse, PaginationParams

router = APIRouter(prefix="/policyholders", tags=["PolicyHolders"])


# Dependency to get the service
async def get_policyholder_service(
    session: AsyncSession = Depends(get_db),
) -> PolicyHolderService:
    """Dependency to get PolicyHolderService instance."""
    return PolicyHolderService(session)


@router.post(
    "",
    response_model=PolicyHolderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new policyholder",
    description="Create a new insurance policyholder with personal and contact information.",
)
async def create_policyholder(
    data: PolicyHolderCreate,
    service: PolicyHolderService = Depends(get_policyholder_service),
) -> PolicyHolderResponse:
    """Create a new policyholder.

    **Business Rules:**
    - Email must be unique
    - Age must be at least 18 years
    - Phone number must be valid format

    **Returns:**
    - 201: PolicyHolder created successfully
    - 400: Validation error (e.g., duplicate email, age < 18)
    - 422: Invalid input data
    """
    return await service.create_policyholder(data)


@router.get(
    "/{policyholder_id}",
    response_model=PolicyHolderResponse,
    summary="Get a policyholder by ID",
    description="Retrieve detailed information about a specific policyholder.",
)
async def get_policyholder(
    policyholder_id: UUID,
    service: PolicyHolderService = Depends(get_policyholder_service),
) -> PolicyHolderResponse:
    """Get a policyholder by ID.

    **Returns:**
    - 200: PolicyHolder found
    - 404: PolicyHolder not found
    """
    return await service.get_policyholder(policyholder_id)


@router.get(
    "",
    response_model=PaginatedResponse[PolicyHolderResponse],
    summary="List policyholders",
    description="Get a paginated list of policyholders with optional filters.",
)
async def list_policyholders(
    # Pagination parameters
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    order_by: Annotated[str | None, Query(description="Order by field")] = None,
    # Filter parameters
    email: Annotated[
        str | None, Query(description="Filter by email (partial match)")
    ] = None,
    is_active: Annotated[
        bool | None, Query(description="Filter by active status")
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Search in first_name, last_name, or email"),
    ] = None,
    service: PolicyHolderService = Depends(get_policyholder_service),
) -> PaginatedResponse[PolicyHolderResponse]:
    """List policyholders with pagination and filters.

    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)
    - `email`: Filter by email (partial match)
    - `is_active`: Filter by active status
    - `search`: Search term for name or email

    **Returns:**
    - 200: Paginated list of policyholders
    """
    pagination = PaginationParams(page=page, page_size=page_size, order_by=order_by)
    filters = PolicyHolderFilterParams(
        email=email,
        is_active=is_active,
        search=search,
    )
    return await service.get_policyholders(pagination, filters)


@router.put(
    "/{policyholder_id}",
    response_model=PolicyHolderResponse,
    summary="Update a policyholder",
    description="Update policyholder information. Only provided fields will be updated.",
)
async def update_policyholder(
    policyholder_id: UUID,
    data: PolicyHolderUpdate,
    service: PolicyHolderService = Depends(get_policyholder_service),
) -> PolicyHolderResponse:
    """Update a policyholder.

    **Note:** Only the fields provided in the request body will be updated.
    All fields are optional.

    **Returns:**
    - 200: PolicyHolder updated successfully
    - 400: Validation error (e.g., duplicate email)
    - 404: PolicyHolder not found
    - 422: Invalid input data
    """
    return await service.update_policyholder(policyholder_id, data)


@router.delete(
    "/{policyholder_id}",
    response_model=MessageResponse,
    summary="Delete a policyholder",
    description="Soft delete a policyholder (sets is_active to False).",
)
async def delete_policyholder(
    policyholder_id: UUID,
    service: PolicyHolderService = Depends(get_policyholder_service),
) -> MessageResponse:
    """Delete a policyholder (soft delete).

    **Note:** This performs a soft delete by setting is_active to False.
    The policyholder record is not permanently removed from the database.

    **Returns:**
    - 200: PolicyHolder deleted successfully
    - 404: PolicyHolder not found
    """
    await service.delete_policyholder(policyholder_id)
    return MessageResponse(message="PolicyHolder deleted successfully")


@router.post(
    "/{policyholder_id}/activate",
    response_model=PolicyHolderResponse,
    summary="Reactivate a policyholder",
    description="Reactivate a previously deactivated policyholder.",
)
async def activate_policyholder(
    policyholder_id: UUID,
    service: PolicyHolderService = Depends(get_policyholder_service),
) -> PolicyHolderResponse:
    """Reactivate a deactivated policyholder.

    Sets is_active to True for a previously deactivated policyholder.

    **Returns:**
    - 200: PolicyHolder reactivated successfully
    - 404: PolicyHolder not found
    """
    return await service.activate_policyholder(policyholder_id)


@router.get(
    "/by-email/{email}",
    response_model=PolicyHolderResponse | None,
    summary="Get policyholder by email",
    description="Find a policyholder by their email address.",
)
async def get_policyholder_by_email(
    email: str,
    service: PolicyHolderService = Depends(get_policyholder_service),
) -> PolicyHolderResponse | None:
    """Get a policyholder by email address.

    **Returns:**
    - 200: PolicyHolder found (or null if not found)
    """
    return await service.get_policyholder_by_email(email)
