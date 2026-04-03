"""Service layer for Underwriting business logic.

This module contains the business logic for the Underwriting domain,
including risk assessment, automatic approval rules, and manual review
workflows for insurance quotes and policies.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.domains.policies.repository import PolicyRepository
from app.domains.pricing.repository import QuoteRepository
from app.domains.underwriting.repository import UnderwritingRepository
from app.domains.underwriting.schemas import (
    UnderwritingReviewApprove,
    UnderwritingReviewCreate,
    UnderwritingReviewFilterParams,
    UnderwritingReviewReject,
    UnderwritingReviewResponse,
    UnderwritingReviewUpdate,
)
from app.shared.enums import RiskLevel, UnderwritingStatus


class RiskScoringEngine:
    """Risk scoring engine for underwriting assessments.

    This class implements the core risk scoring logic for underwriting
    reviews. Risk scores are calculated on a 0-100 scale.
    """

    def calculate_risk_score_from_quote(
        self,
        quote_risk_level: RiskLevel,
        quote_risk_factors: dict[str, Any],
    ) -> tuple[int, RiskLevel, dict[str, Any]]:
        """Calculate risk score from a quote's existing risk assessment.

        This uses the risk score already calculated during quote generation
        and can add additional underwriting-specific factors.

        Args:
            quote_risk_level: Risk level from quote
            quote_risk_factors: Risk factors from quote

        Returns:
            Tuple of (risk_score, risk_level, risk_assessment)
        """
        # Extract risk score from quote factors
        base_risk_score = quote_risk_factors.get("total_risk_score", 0)

        # Build risk assessment
        risk_assessment = {
            "source": "quote",
            "base_risk_score": base_risk_score,
            "quote_risk_level": quote_risk_level.value,
            "quote_risk_factors": quote_risk_factors,
        }

        # Additional underwriting factors could be added here
        # For MVP, we use the quote's risk score directly
        final_risk_score = base_risk_score

        # Determine risk level
        if final_risk_score <= 30:
            final_risk_level = RiskLevel.LOW
        elif final_risk_score <= 50:
            final_risk_level = RiskLevel.MEDIUM
        elif final_risk_score <= 70:
            final_risk_level = RiskLevel.HIGH
        else:
            final_risk_level = RiskLevel.VERY_HIGH

        risk_assessment["final_risk_score"] = final_risk_score
        risk_assessment["final_risk_level"] = final_risk_level.value

        return final_risk_score, final_risk_level, risk_assessment

    def calculate_risk_score_from_policy(
        self,
        policy_premium: float,
        policy_type: str,
    ) -> tuple[int, RiskLevel, dict[str, Any]]:
        """Calculate risk score from a policy's attributes.

        This provides a basic risk assessment for policies that don't
        have an associated quote.

        Args:
            policy_premium: Annual premium amount
            policy_type: Type of policy

        Returns:
            Tuple of (risk_score, risk_level, risk_assessment)
        """
        risk_score = 0
        risk_assessment = {
            "source": "policy",
            "policy_premium": policy_premium,
            "policy_type": policy_type,
        }

        # Premium-based risk (simplified)
        if policy_premium > 10000:
            risk_score += 30
            risk_assessment["premium_risk_score"] = 30
            risk_assessment["premium_risk_reason"] = "high_premium"
        elif policy_premium > 5000:
            risk_score += 15
            risk_assessment["premium_risk_score"] = 15
            risk_assessment["premium_risk_reason"] = "medium_premium"
        else:
            risk_assessment["premium_risk_score"] = 0
            risk_assessment["premium_risk_reason"] = "standard_premium"

        # Policy type adjustments
        policy_type_adjustments = {
            "auto": 10,
            "life": 5,
            "home": 0,
            "health": 0,
        }
        type_adjustment = policy_type_adjustments.get(policy_type, 0)
        risk_score += type_adjustment
        risk_assessment["policy_type_adjustment"] = type_adjustment

        # Determine risk level
        if risk_score <= 30:
            risk_level = RiskLevel.LOW
        elif risk_score <= 50:
            risk_level = RiskLevel.MEDIUM
        elif risk_score <= 70:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH

        risk_assessment["final_risk_score"] = risk_score
        risk_assessment["final_risk_level"] = risk_level.value

        return risk_score, risk_level, risk_assessment


class UnderwritingService:
    """Service for Underwriting business logic.

    Handles underwriting review creation, approval/rejection workflows,
    and orchestrates risk assessment with automatic approval rules.
    """

    # Auto-approval threshold (risk scores below this are auto-approved)
    AUTO_APPROVE_THRESHOLD = 30

    # Manual review threshold (risk scores at or above this require manual review)
    MANUAL_REVIEW_THRESHOLD = 70

    def __init__(self, session: AsyncSession):
        """Initialize service with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.repository = UnderwritingRepository(session)
        self.quote_repository = QuoteRepository(session)
        self.policy_repository = PolicyRepository(session)
        self.risk_engine = RiskScoringEngine()
        self.session = session

    async def create_review(
        self,
        data: UnderwritingReviewCreate,
    ) -> UnderwritingReviewResponse:
        """Create a new underwriting review for a quote or policy.

        Automatically calculates risk score and determines if auto-approval
        or manual review is required based on thresholds.

        Business Rules:
        - Auto-approve if risk_score < 30 (LOW risk)
        - Manual review required if risk_score >= 70 (HIGH/VERY_HIGH)
        - Medium risk (30-69) defaults to IN_REVIEW status

        Args:
            data: Review creation data (with quote_id or policy_id)

        Returns:
            UnderwritingReviewResponse with calculated risk assessment

        Raises:
            NotFoundException: If quote or policy not found
            ValidationException: If validation fails
        """
        # Calculate risk score based on entity type
        if data.quote_id:
            quote = await self.quote_repository.get_by_id(data.quote_id)
            if not quote:
                raise NotFoundException(f"Quote with id {data.quote_id} not found")

            (
                risk_score,
                risk_level,
                risk_assessment,
            ) = self.risk_engine.calculate_risk_score_from_quote(
                quote.risk_level,
                quote.risk_factors,
            )

        elif data.policy_id:
            policy = await self.policy_repository.get_by_id(data.policy_id)
            if not policy:
                raise NotFoundException(f"Policy with id {data.policy_id} not found")

            (
                risk_score,
                risk_level,
                risk_assessment,
            ) = self.risk_engine.calculate_risk_score_from_policy(
                float(policy.premium_amount),
                policy.policy_type.value,
            )
        else:
            raise ValidationException("Either quote_id or policy_id must be provided")

        # Determine initial status based on risk score
        if risk_score < self.AUTO_APPROVE_THRESHOLD:
            status = UnderwritingStatus.APPROVED
        elif risk_score >= self.MANUAL_REVIEW_THRESHOLD:
            status = UnderwritingStatus.REQUIRES_MANUAL_REVIEW
        else:
            status = UnderwritingStatus.IN_REVIEW

        # Create review
        review = await self.repository.create(
            data=data,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_assessment=risk_assessment,
            status=status,
        )

        # If auto-approved, set approved_at timestamp
        if status == UnderwritingStatus.APPROVED:
            review.approved_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(review)

        return UnderwritingReviewResponse.model_validate(review)

    async def get_review(self, review_id: UUID) -> UnderwritingReviewResponse:
        """Get an underwriting review by ID.

        Args:
            review_id: UUID of the review

        Returns:
            UnderwritingReviewResponse

        Raises:
            NotFoundException: If review not found
        """
        review = await self.repository.get_by_id(review_id)
        if not review:
            raise NotFoundException(f"UnderwritingReview with id {review_id} not found")

        return UnderwritingReviewResponse.model_validate(review)

    async def get_reviews(
        self,
        filters: UnderwritingReviewFilterParams,
    ) -> dict:
        """Get list of underwriting reviews with filtering and pagination.

        Args:
            filters: Filter parameters

        Returns:
            Dict with reviews list and pagination metadata
        """
        skip = (filters.page - 1) * filters.size

        reviews = await self.repository.get_all(
            skip=skip,
            limit=filters.size,
            status=filters.status,
            risk_level=filters.risk_level,
            quote_id=filters.quote_id,
            policy_id=filters.policy_id,
            reviewer_id=filters.reviewer_id,
            min_risk_score=filters.min_risk_score,
            max_risk_score=filters.max_risk_score,
        )

        total = await self.repository.count(
            status=filters.status,
            risk_level=filters.risk_level,
            quote_id=filters.quote_id,
            policy_id=filters.policy_id,
            reviewer_id=filters.reviewer_id,
            min_risk_score=filters.min_risk_score,
            max_risk_score=filters.max_risk_score,
        )

        review_responses = [
            UnderwritingReviewResponse.model_validate(review) for review in reviews
        ]

        return {
            "reviews": review_responses,
            "total": total,
            "page": filters.page,
            "size": filters.size,
        }

    async def update_review(
        self,
        review_id: UUID,
        data: UnderwritingReviewUpdate,
    ) -> UnderwritingReviewResponse:
        """Update an underwriting review.

        Args:
            review_id: UUID of the review
            data: Update data

        Returns:
            Updated UnderwritingReviewResponse

        Raises:
            NotFoundException: If review not found
        """
        review = await self.repository.update(review_id, data)
        if not review:
            raise NotFoundException(f"UnderwritingReview with id {review_id} not found")

        return UnderwritingReviewResponse.model_validate(review)

    async def approve_review(
        self,
        review_id: UUID,
        data: UnderwritingReviewApprove,
    ) -> UnderwritingReviewResponse:
        """Approve an underwriting review.

        Args:
            review_id: UUID of the review
            data: Approval data (reviewer_id, notes)

        Returns:
            Updated UnderwritingReviewResponse

        Raises:
            NotFoundException: If review not found
            ValidationException: If review already decided
        """
        review = await self.repository.get_by_id(review_id)
        if not review:
            raise NotFoundException(f"UnderwritingReview with id {review_id} not found")

        if review.is_decided:
            raise ValidationException(
                f"Review {review_id} has already been decided "
                f"(status: {review.status.value})"
            )

        # Update review
        review.status = UnderwritingStatus.APPROVED
        review.reviewer_id = data.reviewer_id
        review.approved_at = datetime.utcnow()

        if data.notes:
            review.notes = data.notes

        await self.session.commit()
        await self.session.refresh(review)

        return UnderwritingReviewResponse.model_validate(review)

    async def reject_review(
        self,
        review_id: UUID,
        data: UnderwritingReviewReject,
    ) -> UnderwritingReviewResponse:
        """Reject an underwriting review.

        Args:
            review_id: UUID of the review
            data: Rejection data (reviewer_id, notes - required)

        Returns:
            Updated UnderwritingReviewResponse

        Raises:
            NotFoundException: If review not found
            ValidationException: If review already decided
        """
        review = await self.repository.get_by_id(review_id)
        if not review:
            raise NotFoundException(f"UnderwritingReview with id {review_id} not found")

        if review.is_decided:
            raise ValidationException(
                f"Review {review_id} has already been decided "
                f"(status: {review.status.value})"
            )

        # Update review
        review.status = UnderwritingStatus.REJECTED
        review.reviewer_id = data.reviewer_id
        review.rejected_at = datetime.utcnow()
        review.notes = data.notes  # Notes are required for rejection

        await self.session.commit()
        await self.session.refresh(review)

        return UnderwritingReviewResponse.model_validate(review)

    async def get_pending_reviews(self, page: int = 1, size: int = 20) -> dict:
        """Get all reviews requiring manual action.

        Returns reviews with PENDING, IN_REVIEW, or REQUIRES_MANUAL_REVIEW status,
        ordered by risk score (highest risk first).

        Args:
            page: Page number
            size: Page size

        Returns:
            Dict with reviews list and pagination metadata
        """
        skip = (page - 1) * size

        reviews = await self.repository.get_pending_reviews(skip=skip, limit=size)
        total = await self.repository.count_pending_reviews()

        review_responses = [
            UnderwritingReviewResponse.model_validate(review) for review in reviews
        ]

        return {
            "reviews": review_responses,
            "total": total,
            "page": page,
            "size": size,
        }
