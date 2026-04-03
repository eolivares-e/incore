"""Repository for Underwriting data access.

This module implements the Repository pattern for the Underwriting domain,
providing an abstraction layer over database operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.underwriting.models import UnderwritingReview
from app.domains.underwriting.schemas import (
    UnderwritingReviewCreate,
    UnderwritingReviewUpdate,
)
from app.shared.enums import RiskLevel, UnderwritingStatus


class UnderwritingRepository:
    """Repository for UnderwritingReview database operations.

    Implements the Repository pattern to abstract database queries
    and provide a clean interface for data access.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self,
        data: UnderwritingReviewCreate,
        risk_score: int,
        risk_level: RiskLevel,
        risk_assessment: dict,
        status: UnderwritingStatus = UnderwritingStatus.PENDING,
    ) -> UnderwritingReview:
        """Create a new underwriting review.

        Args:
            data: UnderwritingReview creation data
            risk_score: Calculated risk score (0-100)
            risk_level: Calculated risk level
            risk_assessment: Risk assessment factors
            status: Initial status (default: PENDING)

        Returns:
            Created UnderwritingReview instance
        """
        review_data = data.model_dump(exclude_unset=True)
        review = UnderwritingReview(
            **review_data,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_assessment=risk_assessment,
            status=status,
        )

        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def get_by_id(self, review_id: UUID) -> Optional[UnderwritingReview]:
        """Get an underwriting review by ID.

        Args:
            review_id: UUID of the review

        Returns:
            UnderwritingReview instance if found, None otherwise
        """
        stmt = select(UnderwritingReview).where(UnderwritingReview.id == review_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_quote_id(self, quote_id: UUID) -> list[UnderwritingReview]:
        """Get all underwriting reviews for a quote.

        Args:
            quote_id: UUID of the quote

        Returns:
            List of UnderwritingReview instances
        """
        stmt = (
            select(UnderwritingReview)
            .where(UnderwritingReview.quote_id == quote_id)
            .order_by(UnderwritingReview.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_policy_id(self, policy_id: UUID) -> list[UnderwritingReview]:
        """Get all underwriting reviews for a policy.

        Args:
            policy_id: UUID of the policy

        Returns:
            List of UnderwritingReview instances
        """
        stmt = (
            select(UnderwritingReview)
            .where(UnderwritingReview.policy_id == policy_id)
            .order_by(UnderwritingReview.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[UnderwritingStatus] = None,
        risk_level: Optional[RiskLevel] = None,
        quote_id: Optional[UUID] = None,
        policy_id: Optional[UUID] = None,
        reviewer_id: Optional[UUID] = None,
        min_risk_score: Optional[int] = None,
        max_risk_score: Optional[int] = None,
    ) -> list[UnderwritingReview]:
        """Get all underwriting reviews with optional filtering.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            status: Filter by status
            risk_level: Filter by risk level
            quote_id: Filter by quote ID
            policy_id: Filter by policy ID
            reviewer_id: Filter by reviewer ID
            min_risk_score: Minimum risk score
            max_risk_score: Maximum risk score

        Returns:
            List of UnderwritingReview instances
        """
        stmt = select(UnderwritingReview)

        # Apply filters
        if status:
            stmt = stmt.where(UnderwritingReview.status == status)

        if risk_level:
            stmt = stmt.where(UnderwritingReview.risk_level == risk_level)

        if quote_id:
            stmt = stmt.where(UnderwritingReview.quote_id == quote_id)

        if policy_id:
            stmt = stmt.where(UnderwritingReview.policy_id == policy_id)

        if reviewer_id:
            stmt = stmt.where(UnderwritingReview.reviewer_id == reviewer_id)

        if min_risk_score is not None:
            stmt = stmt.where(UnderwritingReview.risk_score >= min_risk_score)

        if max_risk_score is not None:
            stmt = stmt.where(UnderwritingReview.risk_score <= max_risk_score)

        # Apply pagination and ordering
        stmt = stmt.order_by(UnderwritingReview.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        status: Optional[UnderwritingStatus] = None,
        risk_level: Optional[RiskLevel] = None,
        quote_id: Optional[UUID] = None,
        policy_id: Optional[UUID] = None,
        reviewer_id: Optional[UUID] = None,
        min_risk_score: Optional[int] = None,
        max_risk_score: Optional[int] = None,
    ) -> int:
        """Count underwriting reviews with optional filtering.

        Args:
            status: Filter by status
            risk_level: Filter by risk level
            quote_id: Filter by quote ID
            policy_id: Filter by policy ID
            reviewer_id: Filter by reviewer ID
            min_risk_score: Minimum risk score
            max_risk_score: Maximum risk score

        Returns:
            Count of matching reviews
        """
        stmt = select(func.count(UnderwritingReview.id))

        # Apply same filters as get_all
        if status:
            stmt = stmt.where(UnderwritingReview.status == status)

        if risk_level:
            stmt = stmt.where(UnderwritingReview.risk_level == risk_level)

        if quote_id:
            stmt = stmt.where(UnderwritingReview.quote_id == quote_id)

        if policy_id:
            stmt = stmt.where(UnderwritingReview.policy_id == policy_id)

        if reviewer_id:
            stmt = stmt.where(UnderwritingReview.reviewer_id == reviewer_id)

        if min_risk_score is not None:
            stmt = stmt.where(UnderwritingReview.risk_score >= min_risk_score)

        if max_risk_score is not None:
            stmt = stmt.where(UnderwritingReview.risk_score <= max_risk_score)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def update(
        self,
        review_id: UUID,
        data: UnderwritingReviewUpdate,
    ) -> Optional[UnderwritingReview]:
        """Update an underwriting review.

        Args:
            review_id: UUID of the review
            data: Update data

        Returns:
            Updated UnderwritingReview instance if found, None otherwise
        """
        review = await self.get_by_id(review_id)
        if not review:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(review, key, value)

        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def delete(self, review_id: UUID) -> bool:
        """Delete an underwriting review.

        Args:
            review_id: UUID of the review

        Returns:
            True if deleted, False if not found
        """
        review = await self.get_by_id(review_id)
        if not review:
            return False

        await self.session.delete(review)
        await self.session.commit()
        return True

    async def get_pending_reviews(
        self, skip: int = 0, limit: int = 20
    ) -> list[UnderwritingReview]:
        """Get all pending reviews (requiring manual action).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of pending UnderwritingReview instances
        """
        pending_statuses = [
            UnderwritingStatus.PENDING,
            UnderwritingStatus.IN_REVIEW,
            UnderwritingStatus.REQUIRES_MANUAL_REVIEW,
        ]

        stmt = (
            select(UnderwritingReview)
            .where(UnderwritingReview.status.in_(pending_statuses))
            .order_by(UnderwritingReview.risk_score.desc())  # High risk first
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_pending_reviews(self) -> int:
        """Count all pending reviews.

        Returns:
            Count of pending reviews
        """
        pending_statuses = [
            UnderwritingStatus.PENDING,
            UnderwritingStatus.IN_REVIEW,
            UnderwritingStatus.REQUIRES_MANUAL_REVIEW,
        ]

        stmt = select(func.count(UnderwritingReview.id)).where(
            UnderwritingReview.status.in_(pending_statuses)
        )

        result = await self.session.execute(stmt)
        return result.scalar() or 0
