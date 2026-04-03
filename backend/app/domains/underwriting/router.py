"""API router for Underwriting endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domains.underwriting.schemas import (
    UnderwritingReviewApprove,
    UnderwritingReviewCreate,
    UnderwritingReviewFilterParams,
    UnderwritingReviewListResponse,
    UnderwritingReviewReject,
    UnderwritingReviewResponse,
    UnderwritingReviewUpdate,
)
from app.domains.underwriting.service import UnderwritingService
from app.shared.enums import RiskLevel, UnderwritingStatus

# Router for underwriting reviews
router = APIRouter(prefix="/underwriting/reviews", tags=["Underwriting"])


# ============================================================================
# Dependencies
# ============================================================================


async def get_underwriting_service(
    session: AsyncSession = Depends(get_db),
) -> UnderwritingService:
    """Dependency to get UnderwritingService instance."""
    return UnderwritingService(session)


# ============================================================================
# UnderwritingReview Endpoints
# ============================================================================


@router.post(
    "",
    response_model=UnderwritingReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new underwriting review",
    description="Create a new underwriting review for a quote or policy with automated risk assessment.",
)
async def create_review(
    data: UnderwritingReviewCreate,
    service: UnderwritingService = Depends(get_underwriting_service),
) -> UnderwritingReviewResponse:
    """Create a new underwriting review.

    **Business Rules:**
    - Either quote_id or policy_id must be provided (not both)
    - Risk score is calculated automatically (0-100 scale)
    - Auto-approve if risk_score < 30 (LOW risk)
    - Manual review required if risk_score >= 70 (HIGH/VERY_HIGH)
    - Medium risk (30-69) defaults to IN_REVIEW status

    **Risk Assessment:**
    For quotes:
    - Uses existing quote risk assessment
    - Inherits age, coverage, and policy type factors

    For policies:
    - Calculates based on premium amount and policy type
    - Premium-based risk scoring applied

    **Returns:**
    - 201: Review created successfully with risk assessment
    - 400: Validation error (both quote_id and policy_id provided)
    - 404: Quote or policy not found
    - 422: Invalid input data
    """
    return await service.create_review(data)


@router.get(
    "/{review_id}",
    response_model=UnderwritingReviewResponse,
    summary="Get an underwriting review by ID",
    description="Retrieve detailed information about a specific underwriting review.",
)
async def get_review(
    review_id: UUID,
    service: UnderwritingService = Depends(get_underwriting_service),
) -> UnderwritingReviewResponse:
    """Get an underwriting review by ID.

    **Returns:**
    - 200: Review found
    - 404: Review not found
    """
    return await service.get_review(review_id)


@router.get(
    "",
    response_model=UnderwritingReviewListResponse,
    summary="List underwriting reviews",
    description="Retrieve a paginated list of underwriting reviews with optional filtering.",
)
async def list_reviews(
    status: Annotated[
        UnderwritingStatus | None,
        Query(description="Filter by review status"),
    ] = None,
    risk_level: Annotated[
        RiskLevel | None,
        Query(description="Filter by risk level"),
    ] = None,
    quote_id: Annotated[
        UUID | None,
        Query(description="Filter by quote ID"),
    ] = None,
    policy_id: Annotated[
        UUID | None,
        Query(description="Filter by policy ID"),
    ] = None,
    reviewer_id: Annotated[
        UUID | None,
        Query(description="Filter by reviewer ID"),
    ] = None,
    min_risk_score: Annotated[
        int | None,
        Query(ge=0, le=100, description="Minimum risk score"),
    ] = None,
    max_risk_score: Annotated[
        int | None,
        Query(ge=0, le=100, description="Maximum risk score"),
    ] = None,
    page: Annotated[
        int,
        Query(ge=1, description="Page number"),
    ] = 1,
    size: Annotated[
        int,
        Query(ge=1, le=100, description="Page size"),
    ] = 10,
    service: UnderwritingService = Depends(get_underwriting_service),
) -> UnderwritingReviewListResponse:
    """List underwriting reviews with filtering and pagination.

    **Query Parameters:**
    - status: Filter by underwriting status
    - risk_level: Filter by risk level (LOW, MEDIUM, HIGH, VERY_HIGH)
    - quote_id: Filter by specific quote
    - policy_id: Filter by specific policy
    - reviewer_id: Filter by reviewer (null for auto-approved)
    - min_risk_score: Minimum risk score (0-100)
    - max_risk_score: Maximum risk score (0-100)
    - page: Page number (default: 1)
    - size: Page size (default: 10, max: 100)

    **Returns:**
    - 200: List of reviews with pagination metadata
    """
    filters = UnderwritingReviewFilterParams(
        status=status,
        risk_level=risk_level,
        quote_id=quote_id,
        policy_id=policy_id,
        reviewer_id=reviewer_id,
        min_risk_score=min_risk_score,
        max_risk_score=max_risk_score,
        page=page,
        size=size,
    )
    return await service.get_reviews(filters)


@router.get(
    "/pending/all",
    response_model=UnderwritingReviewListResponse,
    summary="Get all pending reviews",
    description="Retrieve reviews requiring manual action, sorted by risk score (highest first).",
)
async def get_pending_reviews(
    page: Annotated[
        int,
        Query(ge=1, description="Page number"),
    ] = 1,
    size: Annotated[
        int,
        Query(ge=1, le=100, description="Page size"),
    ] = 20,
    service: UnderwritingService = Depends(get_underwriting_service),
) -> UnderwritingReviewListResponse:
    """Get all reviews requiring manual action.

    Returns reviews with PENDING, IN_REVIEW, or REQUIRES_MANUAL_REVIEW status,
    ordered by risk score (highest risk first).

    **Use Case:**
    - Underwriter dashboard to see prioritized workqueue
    - High-risk reviews appear first

    **Returns:**
    - 200: List of pending reviews with pagination
    """
    return await service.get_pending_reviews(page, size)


@router.put(
    "/{review_id}",
    response_model=UnderwritingReviewResponse,
    summary="Update an underwriting review",
    description="Update notes or other mutable fields on a review.",
)
async def update_review(
    review_id: UUID,
    data: UnderwritingReviewUpdate,
    service: UnderwritingService = Depends(get_underwriting_service),
) -> UnderwritingReviewResponse:
    """Update an underwriting review.

    **Allowed Updates:**
    - notes: Add or update review notes

    **Returns:**
    - 200: Review updated successfully
    - 404: Review not found
    - 422: Invalid input data
    """
    return await service.update_review(review_id, data)


@router.post(
    "/{review_id}/approve",
    response_model=UnderwritingReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve an underwriting review",
    description="Manually approve a review (changes status to APPROVED).",
)
async def approve_review(
    review_id: UUID,
    data: UnderwritingReviewApprove,
    service: UnderwritingService = Depends(get_underwriting_service),
) -> UnderwritingReviewResponse:
    """Approve an underwriting review.

    **Business Rules:**
    - Review must be in pending state (PENDING, IN_REVIEW, REQUIRES_MANUAL_REVIEW)
    - Cannot approve already decided reviews
    - Sets approved_at timestamp
    - Reviewer ID should come from JWT token (Phase 7)

    **Returns:**
    - 200: Review approved successfully
    - 400: Review already decided
    - 404: Review not found
    - 422: Invalid input data
    """
    return await service.approve_review(review_id, data)


@router.post(
    "/{review_id}/reject",
    response_model=UnderwritingReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject an underwriting review",
    description="Manually reject a review (changes status to REJECTED).",
)
async def reject_review(
    review_id: UUID,
    data: UnderwritingReviewReject,
    service: UnderwritingService = Depends(get_underwriting_service),
) -> UnderwritingReviewResponse:
    """Reject an underwriting review.

    **Business Rules:**
    - Review must be in pending state (PENDING, IN_REVIEW, REQUIRES_MANUAL_REVIEW)
    - Cannot reject already decided reviews
    - Rejection notes are REQUIRED
    - Sets rejected_at timestamp
    - Reviewer ID should come from JWT token (Phase 7)

    **Returns:**
    - 200: Review rejected successfully
    - 400: Review already decided or missing notes
    - 404: Review not found
    - 422: Invalid input data
    """
    return await service.reject_review(review_id, data)
