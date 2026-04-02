"""Pydantic schemas for the Policies domain."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from app.shared.enums import CoverageType, PolicyStatus, PolicyType
from app.shared.schemas.base import BaseSchema, TimestampMixin, UUIDMixin
from app.shared.types import CoverageAmount, PolicyNumber, PremiumAmount

# ============================================================================
# Coverage Schemas
# ============================================================================


class CoverageBase(BaseSchema):
    """Base schema with common Coverage fields."""

    coverage_type: CoverageType = Field(
        description="Type of coverage",
        examples=[CoverageType.LIABILITY],
    )
    coverage_name: str = Field(
        min_length=1,
        max_length=200,
        description="Name of the coverage",
        examples=["Liability Coverage"],
    )
    coverage_amount: CoverageAmount = Field(
        gt=0,
        description="Coverage amount in dollars",
        examples=[Decimal("100000.00")],
    )
    deductible: CoverageAmount = Field(
        ge=0,
        description="Deductible amount in dollars",
        examples=[Decimal("500.00")],
        default=Decimal("0.00"),
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the coverage",
        examples=["Covers bodily injury and property damage"],
    )


class CoverageCreate(CoverageBase):
    """Schema for creating a new Coverage.

    Used when creating coverages as part of a policy.
    """

    pass


class CoverageUpdate(BaseSchema):
    """Schema for updating a Coverage.

    All fields are optional. Only provided fields will be updated.
    """

    coverage_type: Optional[CoverageType] = Field(
        None,
        description="Type of coverage",
    )
    coverage_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Name of the coverage",
    )
    coverage_amount: Optional[CoverageAmount] = Field(
        None,
        gt=0,
        description="Coverage amount in dollars",
    )
    deductible: Optional[CoverageAmount] = Field(
        None,
        ge=0,
        description="Deductible amount in dollars",
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the coverage",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the coverage is active",
    )


class CoverageResponse(CoverageBase, UUIDMixin, TimestampMixin):
    """Schema for Coverage responses.

    Includes all fields plus UUID, policy_id, and timestamps.
    """

    policy_id: UUID = Field(
        description="ID of the policy this coverage belongs to",
    )
    is_active: bool = Field(
        description="Whether the coverage is active",
        examples=[True],
    )

    model_config = {
        "from_attributes": True,
    }


# ============================================================================
# Policy Base Schemas
# ============================================================================


class PolicyBase(BaseSchema):
    """Base schema with common Policy fields."""

    policyholder_id: UUID = Field(
        description="ID of the policyholder",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    policy_type: PolicyType = Field(
        description="Type of insurance policy",
        examples=[PolicyType.AUTO],
    )
    premium_amount: PremiumAmount = Field(
        gt=0,
        description="Annual premium amount in dollars",
        examples=[Decimal("1200.00")],
    )
    start_date: date = Field(
        description="Policy start date",
        examples=["2026-01-01"],
    )
    end_date: date = Field(
        description="Policy end date",
        examples=["2027-01-01"],
    )
    description: Optional[str] = Field(
        None,
        description="Policy description",
        examples=["Auto insurance policy for 2026"],
    )
    notes: Optional[str] = Field(
        None,
        description="Internal notes about the policy",
        examples=["Customer requested annual payment"],
    )

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date, info) -> date:
        """Validate that end_date is after start_date."""
        if "start_date" in info.data:
            start_date = info.data["start_date"]
            if v <= start_date:
                raise ValueError("end_date must be after start_date")

            # Validate that policy duration is at least 1 day and max 10 years
            duration_days = (v - start_date).days
            if duration_days < 1:
                raise ValueError("Policy duration must be at least 1 day")
            if duration_days > 3650:  # ~10 years
                raise ValueError("Policy duration cannot exceed 10 years")

        return v


# ============================================================================
# Policy Request Schemas
# ============================================================================


class PolicyCreate(PolicyBase):
    """Schema for creating a new Policy.

    Used in POST /api/v1/policies
    Can include coverages to create them atomically.
    """

    coverages: list[CoverageCreate] = Field(
        default_factory=list,
        description="List of coverages to create with the policy",
        examples=[[]],
    )

    @field_validator("coverages")
    @classmethod
    def validate_coverages(cls, v: list[CoverageCreate]) -> list[CoverageCreate]:
        """Validate that at least one coverage is provided."""
        if len(v) == 0:
            raise ValueError("At least one coverage must be provided")

        # Check for duplicate coverage types
        coverage_types = [c.coverage_type for c in v]
        if len(coverage_types) != len(set(coverage_types)):
            raise ValueError("Duplicate coverage types are not allowed")

        return v


class PolicyUpdate(BaseSchema):
    """Schema for updating a Policy.

    All fields are optional. Only provided fields will be updated.
    Used in PUT /api/v1/policies/{id}
    Note: Coverages must be updated separately via coverage endpoints.
    """

    policy_type: Optional[PolicyType] = Field(
        None,
        description="Type of insurance policy",
    )
    status: Optional[PolicyStatus] = Field(
        None,
        description="Policy status",
    )
    premium_amount: Optional[PremiumAmount] = Field(
        None,
        gt=0,
        description="Annual premium amount in dollars",
    )
    start_date: Optional[date] = Field(
        None,
        description="Policy start date",
    )
    end_date: Optional[date] = Field(
        None,
        description="Policy end date",
    )
    description: Optional[str] = Field(
        None,
        description="Policy description",
    )
    notes: Optional[str] = Field(
        None,
        description="Internal notes about the policy",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the policy is active",
    )

    @model_validator(mode="after")
    def validate_dates(self):
        """Validate that end_date is after start_date if both are provided."""
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValueError("end_date must be after start_date")

            duration_days = (self.end_date - self.start_date).days
            if duration_days < 1:
                raise ValueError("Policy duration must be at least 1 day")
            if duration_days > 3650:
                raise ValueError("Policy duration cannot exceed 10 years")

        return self


# ============================================================================
# Policy Response Schemas
# ============================================================================


class PolicyResponse(PolicyBase, UUIDMixin, TimestampMixin):
    """Schema for Policy responses.

    Includes all fields plus UUID, policy_number, status, and timestamps.
    Used in all GET endpoints.
    """

    policy_number: PolicyNumber = Field(
        description="Unique policy number",
        examples=["POL-2026-AUTO-00001"],
    )
    status: PolicyStatus = Field(
        description="Policy status",
        examples=[PolicyStatus.ACTIVE],
    )
    is_active: bool = Field(
        description="Whether the policy is active",
        examples=[True],
    )
    coverages: list[CoverageResponse] = Field(
        default_factory=list,
        description="List of coverages for this policy",
    )

    model_config = {
        "from_attributes": True,
    }


class PolicyListResponse(BaseSchema):
    """Schema for paginated list of policies.

    This is a simplified version for list endpoints.
    """

    id: UUID
    policy_number: PolicyNumber
    policyholder_id: UUID
    policy_type: PolicyType
    status: PolicyStatus
    premium_amount: Decimal
    start_date: date
    end_date: date
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


# ============================================================================
# Filter Schemas
# ============================================================================


class PolicyFilterParams(BaseSchema):
    """Query parameters for filtering policies."""

    policyholder_id: Optional[UUID] = Field(
        None,
        description="Filter by policyholder ID",
    )
    policy_type: Optional[PolicyType] = Field(
        None,
        description="Filter by policy type",
    )
    status: Optional[PolicyStatus] = Field(
        None,
        description="Filter by policy status",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Filter by active status",
    )
    search: Optional[str] = Field(
        None,
        description="Search in policy_number",
    )
