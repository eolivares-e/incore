"""Pydantic schemas for the Pricing domain."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.shared.enums import PolicyType, QuoteStatus, RiskLevel
from app.shared.schemas.base import BaseSchema, TimestampMixin, UUIDMixin
from app.shared.types import CoverageAmount, PremiumAmount, QuoteNumber

# ============================================================================
# Quote Schemas
# ============================================================================


class QuoteBase(BaseSchema):
    """Base schema with common Quote fields."""

    policy_holder_id: UUID = Field(
        description="ID of the policy holder",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    policy_type: PolicyType = Field(
        description="Type of insurance policy",
        examples=[PolicyType.AUTO],
    )
    requested_coverage_amount: CoverageAmount = Field(
        gt=0,
        description="Requested coverage amount in dollars",
        examples=[Decimal("500000.00")],
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the quote",
        examples=["Customer interested in comprehensive coverage"],
    )


class QuoteCreate(QuoteBase):
    """Schema for creating a new Quote.

    Used in POST /api/v1/quotes
    Premium and risk assessment are calculated automatically.
    """

    pass


class QuoteUpdate(BaseSchema):
    """Schema for updating a Quote.

    All fields are optional. Only provided fields will be updated.
    Used in PUT /api/v1/quotes/{id}
    """

    requested_coverage_amount: Optional[CoverageAmount] = Field(
        None,
        gt=0,
        description="Requested coverage amount in dollars",
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the quote",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the quote is active",
    )


class QuoteResponse(QuoteBase, UUIDMixin, TimestampMixin):
    """Schema for Quote responses.

    Includes all fields plus UUID, quote_number, calculated fields,
    risk assessment, and timestamps.
    Used in all GET endpoints.
    """

    quote_number: QuoteNumber = Field(
        description="Unique quote number",
        examples=["QTE-2026-AUTO-00001"],
    )
    calculated_premium: PremiumAmount = Field(
        description="Calculated annual premium amount in dollars",
        examples=[Decimal("1200.00")],
    )
    risk_level: RiskLevel = Field(
        description="Calculated risk level",
        examples=[RiskLevel.MEDIUM],
    )
    risk_factors: dict[str, Any] = Field(
        description="Risk factors used in calculation",
        examples=[
            {
                "age": 35,
                "age_risk_score": 0,
                "coverage_amount": 500000.00,
                "coverage_risk_score": 0,
                "total_risk_score": 45,
            }
        ],
    )
    valid_until: date = Field(
        description="Date until which the quote is valid",
        examples=["2026-04-30"],
    )
    status: QuoteStatus = Field(
        description="Quote status",
        examples=[QuoteStatus.ACTIVE],
    )
    is_active: bool = Field(
        description="Whether the quote is active",
        examples=[True],
    )
    is_expired: bool = Field(
        description="Whether the quote has expired (computed)",
        examples=[False],
    )
    is_valid: bool = Field(
        description="Whether the quote is still valid (computed)",
        examples=[True],
    )
    days_until_expiry: int = Field(
        description="Days until expiry (negative if expired)",
        examples=[28],
    )

    model_config = {
        "from_attributes": True,
    }


class QuoteListResponse(BaseSchema):
    """Schema for paginated list of quotes.

    This is a simplified version for list endpoints.
    """

    id: UUID
    quote_number: QuoteNumber
    policy_holder_id: UUID
    policy_type: PolicyType
    requested_coverage_amount: Decimal
    calculated_premium: Decimal
    risk_level: RiskLevel
    valid_until: date
    status: QuoteStatus
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


# ============================================================================
# Quote Action Schemas
# ============================================================================


class QuoteAcceptRequest(BaseSchema):
    """Schema for accepting a quote and converting it to a policy.

    Used in POST /api/v1/quotes/{id}/accept
    """

    start_date: date = Field(
        description="Policy start date",
        examples=["2026-05-01"],
    )
    end_date: date = Field(
        description="Policy end date",
        examples=["2027-05-01"],
    )
    description: Optional[str] = Field(
        None,
        description="Policy description",
        examples=["Auto insurance policy converted from quote QTE-2026-AUTO-00001"],
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes for the policy",
        examples=["Customer approved quote on 2026-04-02"],
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
# Filter Schemas
# ============================================================================


class QuoteFilterParams(BaseSchema):
    """Query parameters for filtering quotes."""

    policy_holder_id: Optional[UUID] = Field(
        None,
        description="Filter by policy holder ID",
    )
    policy_type: Optional[PolicyType] = Field(
        None,
        description="Filter by policy type",
    )
    status: Optional[QuoteStatus] = Field(
        None,
        description="Filter by quote status",
    )
    risk_level: Optional[RiskLevel] = Field(
        None,
        description="Filter by risk level",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Filter by active status",
    )
    search: Optional[str] = Field(
        None,
        description="Search in quote_number",
    )


# ============================================================================
# PricingRule Schemas
# ============================================================================


class PricingRuleBase(BaseSchema):
    """Base schema with common PricingRule fields."""

    name: str = Field(
        min_length=1,
        max_length=200,
        description="Name of the pricing rule",
        examples=["Auto - Low Risk Base Rate"],
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the pricing rule",
        examples=["Base pricing rule for low-risk auto insurance policies"],
    )
    policy_type: PolicyType = Field(
        description="Type of insurance policy this rule applies to",
        examples=[PolicyType.AUTO],
    )
    risk_level: RiskLevel = Field(
        description="Risk level this rule applies to",
        examples=[RiskLevel.LOW],
    )
    base_premium: PremiumAmount = Field(
        gt=0,
        description="Base annual premium amount in dollars",
        examples=[Decimal("800.00")],
    )
    multiplier_factors: dict[str, Any] = Field(
        default_factory=dict,
        description="Multiplier factors for premium calculation",
        examples=[
            {
                "coverage_per_100k": 0.05,
                "young_driver_multiplier": 1.2,
                "senior_driver_multiplier": 1.15,
            }
        ],
    )


class PricingRuleCreate(PricingRuleBase):
    """Schema for creating a new PricingRule.

    Used in POST /api/v1/pricing-rules
    """

    pass


class PricingRuleUpdate(BaseSchema):
    """Schema for updating a PricingRule.

    All fields are optional. Only provided fields will be updated.
    Used in PUT /api/v1/pricing-rules/{id}
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Name of the pricing rule",
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the pricing rule",
    )
    base_premium: Optional[PremiumAmount] = Field(
        None,
        gt=0,
        description="Base annual premium amount in dollars",
    )
    multiplier_factors: Optional[dict[str, Any]] = Field(
        None,
        description="Multiplier factors for premium calculation",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the pricing rule is active",
    )


class PricingRuleResponse(PricingRuleBase, UUIDMixin, TimestampMixin):
    """Schema for PricingRule responses.

    Includes all fields plus UUID, status, and timestamps.
    Used in all GET endpoints.
    """

    is_active: bool = Field(
        description="Whether the pricing rule is active",
        examples=[True],
    )

    model_config = {
        "from_attributes": True,
    }
