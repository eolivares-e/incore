"""Repository for Policy data access.

This module implements the Repository pattern for the Policy domain,
providing an abstraction layer over database operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.policies.models import Coverage, Policy
from app.domains.policies.schemas import (
    CoverageCreate,
    CoverageUpdate,
    PolicyCreate,
    PolicyUpdate,
)
from app.shared.enums import PolicyStatus, PolicyType


class PolicyRepository:
    """Repository for Policy database operations.

    Implements the Repository pattern to abstract database queries
    and provide a clean interface for data access.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, data: PolicyCreate, policy_number: str) -> Policy:
        """Create a new policy with coverages.

        Args:
            data: Policy creation data
            policy_number: Generated policy number

        Returns:
            Created Policy instance with coverages
        """
        # Create policy without coverages first
        policy_data = data.model_dump(exclude={"coverages"})
        policy = Policy(**policy_data, policy_number=policy_number)

        # Create coverages
        for coverage_data in data.coverages:
            coverage = Coverage(**coverage_data.model_dump(), policy=policy)
            policy.coverages.append(coverage)

        self.session.add(policy)
        await self.session.commit()
        await self.session.refresh(policy)
        return policy

    async def get_by_id(self, policy_id: UUID) -> Optional[Policy]:
        """Get a policy by ID with coverages.

        Args:
            policy_id: UUID of the policy

        Returns:
            Policy instance if found, None otherwise
        """
        stmt = (
            select(Policy)
            .where(Policy.id == policy_id)
            .options(selectinload(Policy.coverages))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_policy_number(self, policy_number: str) -> Optional[Policy]:
        """Get a policy by policy number with coverages.

        Args:
            policy_number: Policy number

        Returns:
            Policy instance if found, None otherwise
        """
        stmt = (
            select(Policy)
            .where(Policy.policy_number == policy_number)
            .options(selectinload(Policy.coverages))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        policyholder_id: Optional[UUID] = None,
        policy_type: Optional[PolicyType] = None,
        status: Optional[PolicyStatus] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> list[Policy]:
        """Get all policies with optional filtering.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            policyholder_id: Filter by policyholder ID
            policy_type: Filter by policy type
            status: Filter by policy status
            is_active: Filter by active status
            search: Search term for policy_number

        Returns:
            List of Policy instances
        """
        stmt = select(Policy).options(selectinload(Policy.coverages))

        # Apply filters
        if policyholder_id:
            stmt = stmt.where(Policy.policyholder_id == policyholder_id)

        if policy_type:
            stmt = stmt.where(Policy.policy_type == policy_type)

        if status:
            stmt = stmt.where(Policy.status == status)

        if is_active is not None:
            stmt = stmt.where(Policy.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(Policy.policy_number.ilike(search_pattern))

        # Apply pagination and ordering
        stmt = stmt.order_by(Policy.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        policyholder_id: Optional[UUID] = None,
        policy_type: Optional[PolicyType] = None,
        status: Optional[PolicyStatus] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count policies with optional filtering.

        Args:
            policyholder_id: Filter by policyholder ID
            policy_type: Filter by policy type
            status: Filter by policy status
            is_active: Filter by active status
            search: Search term for policy_number

        Returns:
            Total count of matching policies
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(Policy)

        # Apply same filters as get_all
        if policyholder_id:
            stmt = stmt.where(Policy.policyholder_id == policyholder_id)

        if policy_type:
            stmt = stmt.where(Policy.policy_type == policy_type)

        if status:
            stmt = stmt.where(Policy.status == status)

        if is_active is not None:
            stmt = stmt.where(Policy.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(Policy.policy_number.ilike(search_pattern))

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(
        self,
        policy_id: UUID,
        data: PolicyUpdate,
    ) -> Optional[Policy]:
        """Update a policy.

        Args:
            policy_id: UUID of the policy to update
            data: Update data (only provided fields will be updated)

        Returns:
            Updated Policy instance if found, None otherwise
        """
        policy = await self.get_by_id(policy_id)
        if not policy:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)

        await self.session.commit()
        await self.session.refresh(policy)
        return policy

    async def delete(self, policy_id: UUID) -> bool:
        """Soft delete a policy (set is_active to False).

        Args:
            policy_id: UUID of the policy to delete

        Returns:
            True if deleted, False if not found
        """
        policy = await self.get_by_id(policy_id)
        if not policy:
            return False

        policy.is_active = False
        await self.session.commit()
        return True

    async def hard_delete(self, policy_id: UUID) -> bool:
        """Permanently delete a policy from the database.

        WARNING: This cannot be undone. Use soft delete instead for normal operations.

        Args:
            policy_id: UUID of the policy to delete

        Returns:
            True if deleted, False if not found
        """
        policy = await self.get_by_id(policy_id)
        if not policy:
            return False

        await self.session.delete(policy)
        await self.session.commit()
        return True

    async def get_latest_policy_number_sequence(
        self, year: int, policy_type: PolicyType
    ) -> int:
        """Get the latest policy number sequence for a given year and type.

        Args:
            year: Year (e.g., 2026)
            policy_type: Policy type

        Returns:
            Latest sequence number (0 if none exist)
        """
        # Query for policies with pattern POL-{year}-{type}-
        pt = policy_type if isinstance(policy_type, str) else policy_type.value
        pattern = f"POL-{year}-{pt.upper()}-%"
        stmt = (
            select(Policy.policy_number)
            .where(Policy.policy_number.like(pattern))
            .order_by(Policy.policy_number.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        latest = result.scalar_one_or_none()

        if not latest:
            return 0

        # Extract sequence number from policy_number (last 5 digits)
        try:
            sequence = int(latest.split("-")[-1])
            return sequence
        except (ValueError, IndexError):
            return 0

    # Coverage-specific methods

    async def get_coverage_by_id(self, coverage_id: UUID) -> Optional[Coverage]:
        """Get a coverage by ID.

        Args:
            coverage_id: UUID of the coverage

        Returns:
            Coverage instance if found, None otherwise
        """
        stmt = select(Coverage).where(Coverage.id == coverage_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_coverage(
        self, policy_id: UUID, data: CoverageCreate
    ) -> Optional[Coverage]:
        """Add a coverage to an existing policy.

        Args:
            policy_id: UUID of the policy
            data: Coverage creation data

        Returns:
            Created Coverage instance if policy found, None otherwise
        """
        policy = await self.get_by_id(policy_id)
        if not policy:
            return None

        coverage = Coverage(**data.model_dump(), policy_id=policy_id)
        self.session.add(coverage)
        await self.session.commit()
        await self.session.refresh(coverage)
        return coverage

    async def update_coverage(
        self,
        coverage_id: UUID,
        data: CoverageUpdate,
    ) -> Optional[Coverage]:
        """Update a coverage.

        Args:
            coverage_id: UUID of the coverage to update
            data: Update data (only provided fields will be updated)

        Returns:
            Updated Coverage instance if found, None otherwise
        """
        coverage = await self.get_coverage_by_id(coverage_id)
        if not coverage:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(coverage, field, value)

        await self.session.commit()
        await self.session.refresh(coverage)
        return coverage

    async def delete_coverage(self, coverage_id: UUID) -> bool:
        """Delete a coverage.

        Args:
            coverage_id: UUID of the coverage to delete

        Returns:
            True if deleted, False if not found
        """
        coverage = await self.get_coverage_by_id(coverage_id)
        if not coverage:
            return False

        await self.session.delete(coverage)
        await self.session.commit()
        return True
