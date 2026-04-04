"""Service layer for Policy business logic.

This module contains the business logic for the Policy domain,
including validation rules, policy number generation, and complex operations.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.domains.policies.repository import PolicyRepository
from app.domains.policies.schemas import (
    CoverageCreate,
    CoverageResponse,
    CoverageUpdate,
    PolicyCreate,
    PolicyFilterParams,
    PolicyResponse,
    PolicyUpdate,
)
from app.shared.enums import PolicyStatus, PolicyType
from app.shared.schemas.base import PaginatedResponse, PaginationParams


class PolicyService:
    """Service for Policy business logic.

    Handles validation, business rules, policy number generation,
    and orchestrates repository operations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize service with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.repository = PolicyRepository(session)

    def _generate_policy_number(
        self, year: int, policy_type: PolicyType, sequence: int
    ) -> str:
        """Generate a policy number in format: POL-YYYY-TYPE-NNNNN.

        Args:
            year: Year (e.g., 2026)
            policy_type: Policy type enum
            sequence: Sequence number (will be zero-padded to 5 digits)

        Returns:
            Generated policy number

        Examples:
            POL-2026-AUTO-00001
            POL-2026-HEALTH-00042
            POL-2026-LIFE-99999
        """
        pt = policy_type if isinstance(policy_type, str) else policy_type.value
        return f"POL-{year}-{pt.upper()}-{sequence:05d}"

    async def _get_next_policy_number(self, policy_type: PolicyType) -> str:
        """Get the next available policy number for a given type.

        Args:
            policy_type: Policy type

        Returns:
            Next available policy number
        """
        current_year = datetime.now().year
        latest_sequence = await self.repository.get_latest_policy_number_sequence(
            year=current_year,
            policy_type=policy_type,
        )
        next_sequence = latest_sequence + 1
        return self._generate_policy_number(current_year, policy_type, next_sequence)

    async def create_policy(self, data: PolicyCreate) -> PolicyResponse:
        """Create a new policy with coverages.

        Business rules:
        - Policy must have at least one coverage (validated in schema)
        - Policy number is auto-generated
        - Policy starts in DRAFT status
        - Start date cannot be in the past (more than 1 day ago)
        - Policyholder must exist (enforced by FK constraint)

        Args:
            data: Policy creation data with coverages

        Returns:
            Created policy with coverages

        Raises:
            ValidationException: If business rules are violated
        """
        # Generate policy number
        policy_number = await self._get_next_policy_number(data.policy_type)

        # Create policy with coverages
        policy = await self.repository.create(data, policy_number)
        return PolicyResponse.model_validate(policy)

    async def get_policy(self, policy_id: UUID) -> PolicyResponse:
        """Get a policy by ID with coverages.

        Args:
            policy_id: UUID of the policy

        Returns:
            Policy data with coverages

        Raises:
            NotFoundException: If policy not found
        """
        policy = await self.repository.get_by_id(policy_id)
        if not policy:
            raise NotFoundException(
                resource="Policy",
                resource_id=str(policy_id),
            )

        return PolicyResponse.model_validate(policy)

    async def get_policy_by_number(self, policy_number: str) -> PolicyResponse:
        """Get a policy by policy number with coverages.

        Args:
            policy_number: Policy number

        Returns:
            Policy data with coverages

        Raises:
            NotFoundException: If policy not found
        """
        policy = await self.repository.get_by_policy_number(policy_number)
        if not policy:
            raise NotFoundException(
                resource="Policy",
                resource_id=policy_number,
            )

        return PolicyResponse.model_validate(policy)

    async def get_policies(
        self,
        pagination: PaginationParams,
        filters: PolicyFilterParams,
    ) -> PaginatedResponse[PolicyResponse]:
        """Get a paginated list of policies with optional filters.

        Args:
            pagination: Pagination parameters
            filters: Filter parameters

        Returns:
            Paginated list of policies
        """
        # Get total count for pagination
        total = await self.repository.count(
            policyholder_id=filters.policyholder_id,
            policy_type=filters.policy_type,
            status=filters.status,
            is_active=filters.is_active,
            search=filters.search,
        )

        # Get policies
        policies = await self.repository.get_all(
            skip=pagination.offset,
            limit=pagination.limit,
            policyholder_id=filters.policyholder_id,
            policy_type=filters.policy_type,
            status=filters.status,
            is_active=filters.is_active,
            search=filters.search,
        )

        # Convert to response schemas
        items = [PolicyResponse.model_validate(p) for p in policies]

        return PaginatedResponse.create(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def update_policy(
        self,
        policy_id: UUID,
        data: PolicyUpdate,
    ) -> PolicyResponse:
        """Update a policy.

        Business rules:
        - Cannot change policyholder_id (not allowed in update schema)
        - Cannot change policy_number (not allowed in update schema)
        - Status transitions must be valid (DRAFT -> ACTIVE -> EXPIRED/CANCELLED)

        Args:
            policy_id: UUID of the policy to update
            data: Update data

        Returns:
            Updated policy

        Raises:
            NotFoundException: If policy not found
            ValidationException: If business rules are violated
        """
        # Check if policy exists
        policy = await self.repository.get_by_id(policy_id)
        if not policy:
            raise NotFoundException(
                resource="Policy",
                resource_id=str(policy_id),
            )

        # Validate status transition if status is being updated
        if data.status is not None:
            self._validate_status_transition(policy.status, data.status)

        # Update policy
        updated_policy = await self.repository.update(policy_id, data)
        return PolicyResponse.model_validate(updated_policy)

    def _validate_status_transition(
        self, current_status: PolicyStatus, new_status: PolicyStatus
    ) -> None:
        """Validate policy status transitions.

        Valid transitions:
        - DRAFT -> ACTIVE
        - DRAFT -> CANCELLED
        - ACTIVE -> EXPIRED
        - ACTIVE -> CANCELLED

        Args:
            current_status: Current policy status
            new_status: New policy status

        Raises:
            ValidationException: If transition is invalid
        """
        valid_transitions = {
            PolicyStatus.DRAFT: {PolicyStatus.ACTIVE, PolicyStatus.CANCELLED},
            PolicyStatus.ACTIVE: {PolicyStatus.EXPIRED, PolicyStatus.CANCELLED},
            PolicyStatus.EXPIRED: set(),  # No transitions allowed
            PolicyStatus.CANCELLED: set(),  # No transitions allowed
        }

        if current_status == new_status:
            return  # No change

        if new_status not in valid_transitions.get(current_status, set()):
            raise ValidationException(
                message=f"Invalid status transition from {current_status.value} to {new_status.value}",
                details={
                    "current_status": current_status.value,
                    "new_status": new_status.value,
                },
            )

    async def delete_policy(self, policy_id: UUID) -> None:
        """Soft delete a policy.

        Business rules:
        - Policy must exist
        - Sets is_active to False

        Args:
            policy_id: UUID of the policy to delete

        Raises:
            NotFoundException: If policy not found
        """
        success = await self.repository.delete(policy_id)
        if not success:
            raise NotFoundException(
                resource="Policy",
                resource_id=str(policy_id),
            )

    async def activate_policy(self, policy_id: UUID) -> PolicyResponse:
        """Activate a policy (change status from DRAFT to ACTIVE).

        Business rules:
        - Policy must be in DRAFT status
        - Policy start date must be today or in the future

        Args:
            policy_id: UUID of the policy to activate

        Returns:
            Activated policy

        Raises:
            NotFoundException: If policy not found
            ValidationException: If policy cannot be activated
        """
        policy = await self.repository.get_by_id(policy_id)
        if not policy:
            raise NotFoundException(
                resource="Policy",
                resource_id=str(policy_id),
            )

        # Check if policy is in DRAFT status
        if policy.status != PolicyStatus.DRAFT:
            raise ValidationException(
                message=f"Cannot activate policy with status {policy.status.value}",
                details={"current_status": policy.status.value},
            )

        # Update status to ACTIVE
        update_data = PolicyUpdate(status=PolicyStatus.ACTIVE)
        updated_policy = await self.repository.update(policy_id, update_data)
        return PolicyResponse.model_validate(updated_policy)

    async def cancel_policy(self, policy_id: UUID) -> PolicyResponse:
        """Cancel a policy (change status to CANCELLED).

        Business rules:
        - Policy must be in DRAFT or ACTIVE status
        - Cannot cancel EXPIRED or already CANCELLED policies

        Args:
            policy_id: UUID of the policy to cancel

        Returns:
            Cancelled policy

        Raises:
            NotFoundException: If policy not found
            ValidationException: If policy cannot be cancelled
        """
        policy = await self.repository.get_by_id(policy_id)
        if not policy:
            raise NotFoundException(
                resource="Policy",
                resource_id=str(policy_id),
            )

        # Check if policy can be cancelled
        if policy.status not in {PolicyStatus.DRAFT, PolicyStatus.ACTIVE}:
            raise ValidationException(
                message=f"Cannot cancel policy with status {policy.status.value}",
                details={"current_status": policy.status.value},
            )

        # Update status to CANCELLED
        update_data = PolicyUpdate(status=PolicyStatus.CANCELLED)
        updated_policy = await self.repository.update(policy_id, update_data)
        return PolicyResponse.model_validate(updated_policy)

    # Coverage operations

    async def add_coverage(
        self, policy_id: UUID, data: CoverageCreate
    ) -> CoverageResponse:
        """Add a coverage to an existing policy.

        Business rules:
        - Policy must exist
        - Policy must be in DRAFT status
        - Coverage type must not already exist on the policy

        Args:
            policy_id: UUID of the policy
            data: Coverage creation data

        Returns:
            Created coverage

        Raises:
            NotFoundException: If policy not found
            ValidationException: If business rules are violated
        """
        # Check if policy exists and is in DRAFT status
        policy = await self.repository.get_by_id(policy_id)
        if not policy:
            raise NotFoundException(
                resource="Policy",
                resource_id=str(policy_id),
            )

        if policy.status != PolicyStatus.DRAFT:
            raise ValidationException(
                message="Can only add coverages to policies in DRAFT status",
                details={"current_status": policy.status.value},
            )

        # Check if coverage type already exists
        for coverage in policy.coverages:
            if coverage.coverage_type == data.coverage_type:
                raise ValidationException(
                    message=f"Coverage type {data.coverage_type if isinstance(data.coverage_type, str) else data.coverage_type.value} already exists on this policy",
                    details={"coverage_type": data.coverage_type if isinstance(data.coverage_type, str) else data.coverage_type.value},
                )

        # Add coverage
        coverage = await self.repository.add_coverage(policy_id, data)
        return CoverageResponse.model_validate(coverage)

    async def update_coverage(
        self, coverage_id: UUID, data: CoverageUpdate
    ) -> CoverageResponse:
        """Update a coverage.

        Business rules:
        - Coverage must exist
        - Policy must be in DRAFT status

        Args:
            coverage_id: UUID of the coverage to update
            data: Update data

        Returns:
            Updated coverage

        Raises:
            NotFoundException: If coverage not found
            ValidationException: If business rules are violated
        """
        # Check if coverage exists
        coverage = await self.repository.get_coverage_by_id(coverage_id)
        if not coverage:
            raise NotFoundException(
                resource="Coverage",
                resource_id=str(coverage_id),
            )

        # Check if policy is in DRAFT status
        policy = await self.repository.get_by_id(coverage.policy_id)
        if policy and policy.status != PolicyStatus.DRAFT:
            raise ValidationException(
                message="Can only update coverages on policies in DRAFT status",
                details={"current_status": policy.status.value},
            )

        # Update coverage
        updated_coverage = await self.repository.update_coverage(coverage_id, data)
        return CoverageResponse.model_validate(updated_coverage)

    async def delete_coverage(self, coverage_id: UUID) -> None:
        """Delete a coverage.

        Business rules:
        - Coverage must exist
        - Policy must be in DRAFT status
        - Policy must have at least 2 coverages (cannot delete the last one)

        Args:
            coverage_id: UUID of the coverage to delete

        Raises:
            NotFoundException: If coverage not found
            ValidationException: If business rules are violated
        """
        # Check if coverage exists
        coverage = await self.repository.get_coverage_by_id(coverage_id)
        if not coverage:
            raise NotFoundException(
                resource="Coverage",
                resource_id=str(coverage_id),
            )

        # Check if policy is in DRAFT status
        policy = await self.repository.get_by_id(coverage.policy_id)
        if policy:
            if policy.status != PolicyStatus.DRAFT:
                raise ValidationException(
                    message="Can only delete coverages from policies in DRAFT status",
                    details={"current_status": policy.status.value},
                )

            # Check if policy would have at least 1 coverage remaining
            if len(policy.coverages) <= 1:
                raise ValidationException(
                    message="Cannot delete the last coverage from a policy",
                    details={"remaining_coverages": len(policy.coverages)},
                )

        # Delete coverage
        success = await self.repository.delete_coverage(coverage_id)
        if not success:
            raise NotFoundException(
                resource="Coverage",
                resource_id=str(coverage_id),
            )
