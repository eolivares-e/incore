"""Service layer for PolicyHolder business logic.

This module contains the business logic for the PolicyHolder domain,
including validation rules and complex operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.domains.policy_holders.repository import PolicyHolderRepository
from app.domains.policy_holders.schemas import (
    PolicyHolderCreate,
    PolicyHolderFilterParams,
    PolicyHolderResponse,
    PolicyHolderUpdate,
)
from app.shared.schemas.base import PaginatedResponse, PaginationParams


class PolicyHolderService:
    """Service for PolicyHolder business logic.

    Handles validation, business rules, and orchestrates repository operations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize service with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.repository = PolicyHolderRepository(session)

    async def create_policyholder(
        self, data: PolicyHolderCreate
    ) -> PolicyHolderResponse:
        """Create a new policyholder.

        Business rules:
        - Email must be unique
        - PolicyHolder must be at least 18 years old (validated in schema)

        Args:
            data: PolicyHolder creation data

        Returns:
            Created policyholder

        Raises:
            ValidationException: If email already exists
        """
        # Check if email already exists
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise ValidationException(
                message=f"Email '{data.email}' is already registered",
                details={"field": "email", "error": "duplicate"},
            )

        # Create policyholder
        policyholder = await self.repository.create(data)
        return PolicyHolderResponse.model_validate(policyholder)

    async def get_policyholder(self, policyholder_id: UUID) -> PolicyHolderResponse:
        """Get a policyholder by ID.

        Args:
            policyholder_id: UUID of the policyholder

        Returns:
            PolicyHolder data

        Raises:
            NotFoundException: If policyholder not found
        """
        policyholder = await self.repository.get_by_id(policyholder_id)
        if not policyholder:
            raise NotFoundException(
                resource="PolicyHolder",
                resource_id=str(policyholder_id),
            )

        return PolicyHolderResponse.model_validate(policyholder)

    async def get_policyholders(
        self,
        pagination: PaginationParams,
        filters: PolicyHolderFilterParams,
    ) -> PaginatedResponse[PolicyHolderResponse]:
        """Get a paginated list of policyholders with optional filters.

        Args:
            pagination: Pagination parameters
            filters: Filter parameters

        Returns:
            Paginated list of policyholders
        """
        # Get total count for pagination
        total = await self.repository.count(
            email=filters.email,
            is_active=filters.is_active,
            search=filters.search,
        )

        # Get policyholders
        policyholders = await self.repository.get_all(
            skip=pagination.offset,
            limit=pagination.limit,
            email=filters.email,
            is_active=filters.is_active,
            search=filters.search,
        )

        # Convert to response schemas
        items = [PolicyHolderResponse.model_validate(ph) for ph in policyholders]

        return PaginatedResponse.create(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def update_policyholder(
        self,
        policyholder_id: UUID,
        data: PolicyHolderUpdate,
    ) -> PolicyHolderResponse:
        """Update a policyholder.

        Business rules:
        - Email must be unique (if being updated)
        - Cannot update to an inactive policyholder's email

        Args:
            policyholder_id: UUID of the policyholder to update
            data: Update data

        Returns:
            Updated policyholder

        Raises:
            NotFoundException: If policyholder not found
            ValidationException: If email already exists
        """
        # Check if policyholder exists
        existing = await self.repository.get_by_id(policyholder_id)
        if not existing:
            raise NotFoundException(
                resource="PolicyHolder",
                resource_id=str(policyholder_id),
            )

        # If updating email, check uniqueness
        if data.email and data.email != existing.email:
            email_exists = await self.repository.get_by_email(data.email)
            if email_exists:
                raise ValidationException(
                    message=f"Email '{data.email}' is already registered",
                    details={"field": "email", "error": "duplicate"},
                )

        # Update policyholder
        updated = await self.repository.update(policyholder_id, data)
        return PolicyHolderResponse.model_validate(updated)

    async def delete_policyholder(self, policyholder_id: UUID) -> None:
        """Soft delete a policyholder.

        Sets is_active to False instead of permanently deleting.

        Args:
            policyholder_id: UUID of the policyholder to delete

        Raises:
            NotFoundException: If policyholder not found
        """
        deleted = await self.repository.delete(policyholder_id)
        if not deleted:
            raise NotFoundException(
                resource="PolicyHolder",
                resource_id=str(policyholder_id),
            )

    async def activate_policyholder(
        self, policyholder_id: UUID
    ) -> PolicyHolderResponse:
        """Reactivate a previously deactivated policyholder.

        Args:
            policyholder_id: UUID of the policyholder to activate

        Returns:
            Reactivated policyholder

        Raises:
            NotFoundException: If policyholder not found
        """
        # Use update to set is_active to True
        update_data = PolicyHolderUpdate(is_active=True)
        updated = await self.repository.update(policyholder_id, update_data)

        if not updated:
            raise NotFoundException(
                resource="PolicyHolder",
                resource_id=str(policyholder_id),
            )

        return PolicyHolderResponse.model_validate(updated)

    async def get_policyholder_by_email(
        self, email: str
    ) -> Optional[PolicyHolderResponse]:
        """Get a policyholder by email address.

        Args:
            email: Email address to search for

        Returns:
            PolicyHolder if found, None otherwise
        """
        policyholder = await self.repository.get_by_email(email)
        if not policyholder:
            return None

        return PolicyHolderResponse.model_validate(policyholder)
