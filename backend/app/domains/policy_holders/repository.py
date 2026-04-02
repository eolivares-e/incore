"""Repository for PolicyHolder data access.

This module implements the Repository pattern for the PolicyHolder domain,
providing an abstraction layer over database operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.policy_holders.models import PolicyHolder
from app.domains.policy_holders.schemas import PolicyHolderCreate, PolicyHolderUpdate


class PolicyHolderRepository:
    """Repository for PolicyHolder database operations.

    Implements the Repository pattern to abstract database queries
    and provide a clean interface for data access.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, data: PolicyHolderCreate) -> PolicyHolder:
        """Create a new policyholder.

        Args:
            data: PolicyHolder creation data

        Returns:
            Created PolicyHolder instance
        """
        policyholder = PolicyHolder(**data.model_dump())
        self.session.add(policyholder)
        await self.session.commit()
        await self.session.refresh(policyholder)
        return policyholder

    async def get_by_id(self, policyholder_id: UUID) -> Optional[PolicyHolder]:
        """Get a policyholder by ID.

        Args:
            policyholder_id: UUID of the policyholder

        Returns:
            PolicyHolder instance if found, None otherwise
        """
        stmt = select(PolicyHolder).where(PolicyHolder.id == policyholder_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[PolicyHolder]:
        """Get a policyholder by email.

        Args:
            email: Email address

        Returns:
            PolicyHolder instance if found, None otherwise
        """
        stmt = select(PolicyHolder).where(PolicyHolder.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        email: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> list[PolicyHolder]:
        """Get all policyholders with optional filtering.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            email: Filter by email (partial match)
            is_active: Filter by active status
            search: Search term for first_name, last_name, or email

        Returns:
            List of PolicyHolder instances
        """
        stmt = select(PolicyHolder)

        # Apply filters
        if email:
            stmt = stmt.where(PolicyHolder.email.ilike(f"%{email}%"))

        if is_active is not None:
            stmt = stmt.where(PolicyHolder.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    PolicyHolder.first_name.ilike(search_pattern),
                    PolicyHolder.last_name.ilike(search_pattern),
                    PolicyHolder.email.ilike(search_pattern),
                )
            )

        # Apply pagination and ordering
        stmt = stmt.order_by(PolicyHolder.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        email: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count policyholders with optional filtering.

        Args:
            email: Filter by email (partial match)
            is_active: Filter by active status
            search: Search term for first_name, last_name, or email

        Returns:
            Total count of matching policyholders
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(PolicyHolder)

        # Apply same filters as get_all
        if email:
            stmt = stmt.where(PolicyHolder.email.ilike(f"%{email}%"))

        if is_active is not None:
            stmt = stmt.where(PolicyHolder.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    PolicyHolder.first_name.ilike(search_pattern),
                    PolicyHolder.last_name.ilike(search_pattern),
                    PolicyHolder.email.ilike(search_pattern),
                )
            )

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(
        self,
        policyholder_id: UUID,
        data: PolicyHolderUpdate,
    ) -> Optional[PolicyHolder]:
        """Update a policyholder.

        Args:
            policyholder_id: UUID of the policyholder to update
            data: Update data (only provided fields will be updated)

        Returns:
            Updated PolicyHolder instance if found, None otherwise
        """
        policyholder = await self.get_by_id(policyholder_id)
        if not policyholder:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policyholder, field, value)

        await self.session.commit()
        await self.session.refresh(policyholder)
        return policyholder

    async def delete(self, policyholder_id: UUID) -> bool:
        """Soft delete a policyholder (set is_active to False).

        Args:
            policyholder_id: UUID of the policyholder to delete

        Returns:
            True if deleted, False if not found
        """
        policyholder = await self.get_by_id(policyholder_id)
        if not policyholder:
            return False

        policyholder.is_active = False
        await self.session.commit()
        return True

    async def hard_delete(self, policyholder_id: UUID) -> bool:
        """Permanently delete a policyholder from the database.

        WARNING: This cannot be undone. Use soft delete instead for normal operations.

        Args:
            policyholder_id: UUID of the policyholder to delete

        Returns:
            True if deleted, False if not found
        """
        policyholder = await self.get_by_id(policyholder_id)
        if not policyholder:
            return False

        await self.session.delete(policyholder)
        await self.session.commit()
        return True
