"""Pydantic schemas for the Underwriting domain."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.shared.enums import RiskLevel, UnderwritingStatus
from app.shared.schemas.base import BaseSchema, TimestampMixin, UUIDMixin

# ============================================================================
# UnderwritingReview Schemas
# ============================================================================


class UnderwritingReviewBase(BaseSchema):
    """Base schema with common UnderwritingReview fields."""

    notes: Optional[str] = Field(
        None,
        description="Review notes from underwriter",
        examples=["Application requires additional medical documentation"],
    )


class UnderwritingReviewCreate(BaseSchema):
    """Schema for creating a new UnderwritingReview.

    Used in POST /api/v1/underwriting/reviews
    Initiates a review for either a quote or a policy (not both).
    """

    quote_id: Optional[UUID] = Field(
        None,
        description="ID of the quote to review (mutually exclusive with policy_id)",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    policy_id: Optional[UUID] = Field(
        None,
        description="ID of the policy to review (mutually exclusive with quote_id)",
        examples=["123e4567-e89b-12d3-a456-426614174001"],
    )
    notes: Optional[str] = Field(
        None,
        description="Initial review notes",
        examples=["High-value policy requires senior underwriter approval"],
    )

    @field_validator("policy_id")
    @classmethod
    def validate_quote_or_policy(cls, v: Optional[UUID], info) -> Optional[UUID]:
        """Ensure either quote_id or policy_id is provided, but not both."""
        quote_id = info.data.get("quote_id")
        if quote_id and v:
            raise ValueError("Provide either quote_id or policy_id, not both")
        if not quote_id and not v:
            raise ValueError("Either quote_id or policy_id must be provided")
        return v


class UnderwritingReviewUpdate(BaseSchema):
    """Schema for updating an UnderwritingReview.

    Used for manual review updates.
    All fields are optional. Only provided fields will be updated.
    """

    notes: Optional[str] = Field(
        None,
        description="Updated review notes",
    )


class UnderwritingReviewApprove(BaseSchema):
    """Schema for approving an underwriting review.

    Used in POST /api/v1/underwriting/reviews/{id}/approve
    """

    reviewer_id: Optional[UUID] = Field(
        None,
        description="ID of the reviewer (from JWT token in Phase 7)",
        examples=["123e4567-e89b-12d3-a456-426614174002"],
    )
    notes: Optional[str] = Field(
        None,
        description="Approval notes",
        examples=["All documentation verified, approved with standard terms"],
    )


class UnderwritingReviewReject(BaseSchema):
    """Schema for rejecting an underwriting review.

    Used in POST /api/v1/underwriting/reviews/{id}/reject
    """

    reviewer_id: Optional[UUID] = Field(
        None,
        description="ID of the reviewer (from JWT token in Phase 7)",
        examples=["123e4567-e89b-12d3-a456-426614174002"],
    )
    notes: str = Field(
        description="Rejection reason (required)",
        examples=[
            "Applicant does not meet minimum age requirements for this policy type"
        ],
    )


class UnderwritingReviewResponse(UUIDMixin, TimestampMixin):
    """Schema for UnderwritingReview responses.

    Includes all fields plus UUID and timestamps.
    Used in all GET endpoints.
    """

    quote_id: Optional[UUID] = Field(
        None,
        description="ID of the reviewed quote",
    )
    policy_id: Optional[UUID] = Field(
        None,
        description="ID of the reviewed policy",
    )
    reviewer_id: Optional[UUID] = Field(
        None,
        description="ID of the reviewer (null for auto-approval)",
    )
    status: UnderwritingStatus = Field(
        description="Current review status",
        examples=[UnderwritingStatus.APPROVED],
    )
    risk_level: RiskLevel = Field(
        description="Assessed risk level",
        examples=[RiskLevel.MEDIUM],
    )
    risk_score: int = Field(
        ge=0,
        le=100,
        description="Risk score (0-100)",
        examples=[45],
    )
    risk_assessment: dict[str, Any] = Field(
        description="Detailed risk assessment factors",
        examples=[
            {
                "age": 35,
                "policy_type": "auto",
                "coverage_amount": 500000.00,
                "previous_claims": 0,
                "credit_score": 750,
                "risk_factors": ["high_coverage"],
            }
        ],
    )
    notes: Optional[str] = Field(
        None,
        description="Review notes",
    )
    approved_at: Optional[datetime] = Field(
        None,
        description="Timestamp when approved",
    )
    rejected_at: Optional[datetime] = Field(
        None,
        description="Timestamp when rejected",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "quote_id": "123e4567-e89b-12d3-a456-426614174001",
                    "policy_id": None,
                    "reviewer_id": None,
                    "status": "approved",
                    "risk_level": "medium",
                    "risk_score": 45,
                    "risk_assessment": {
                        "age": 35,
                        "policy_type": "auto",
                        "coverage_amount": 500000.00,
                    },
                    "notes": "Auto-approved based on low risk score",
                    "approved_at": "2026-04-02T10:30:00Z",
                    "rejected_at": None,
                    "created_at": "2026-04-02T10:00:00Z",
                    "updated_at": "2026-04-02T10:30:00Z",
                }
            ]
        }
    }


class UnderwritingReviewListResponse(BaseSchema):
    """Schema for paginated list of UnderwritingReview responses."""

    reviews: list[UnderwritingReviewResponse] = Field(
        description="List of underwriting reviews",
    )
    total: int = Field(
        ge=0,
        description="Total number of reviews matching filters",
    )
    page: int = Field(
        ge=1,
        description="Current page number",
    )
    size: int = Field(
        ge=1,
        le=100,
        description="Page size",
    )


class UnderwritingReviewFilterParams(BaseSchema):
    """Schema for filtering underwriting reviews.

    Used as query parameters in GET /api/v1/underwriting/reviews
    """

    status: Optional[UnderwritingStatus] = Field(
        None,
        description="Filter by status",
    )
    risk_level: Optional[RiskLevel] = Field(
        None,
        description="Filter by risk level",
    )
    quote_id: Optional[UUID] = Field(
        None,
        description="Filter by quote ID",
    )
    policy_id: Optional[UUID] = Field(
        None,
        description="Filter by policy ID",
    )
    reviewer_id: Optional[UUID] = Field(
        None,
        description="Filter by reviewer ID",
    )
    min_risk_score: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Minimum risk score",
    )
    max_risk_score: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Maximum risk score",
    )
    page: int = Field(
        1,
        ge=1,
        description="Page number",
    )
    size: int = Field(
        10,
        ge=1,
        le=100,
        description="Page size",
    )
