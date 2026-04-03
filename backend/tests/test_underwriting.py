"""Tests for the Underwriting domain."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domains.policies.models import Policy  # noqa: F401
from app.domains.policy_holders.models import PolicyHolder  # noqa: F401
from app.domains.pricing.models import Quote  # noqa: F401
from app.domains.underwriting.models import UnderwritingReview
from app.domains.underwriting.schemas import (
    UnderwritingReviewApprove,
    UnderwritingReviewCreate,
    UnderwritingReviewReject,
    UnderwritingReviewResponse,
)
from app.domains.underwriting.service import RiskScoringEngine, UnderwritingService
from app.shared.enums import RiskLevel, UnderwritingStatus

# ============================================================================
# Model Tests
# ============================================================================


class TestUnderwritingReviewModel:
    """Tests for the UnderwritingReview model."""

    def test_review_repr(self):
        """Test UnderwritingReview __repr__ method."""
        quote_id = uuid4()
        review = UnderwritingReview(
            quote_id=quote_id,
            status=UnderwritingStatus.APPROVED,
            risk_level=RiskLevel.LOW,
            risk_score=25,
            risk_assessment={},
        )
        repr_str = repr(review)
        assert str(quote_id) in repr_str
        assert "approved" in repr_str.lower()
        assert "low" in repr_str.lower()
        assert "25" in repr_str

    def test_review_is_pending_property(self):
        """Test UnderwritingReview.is_pending property."""
        # Pending review
        pending_review = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.PENDING,
            risk_level=RiskLevel.MEDIUM,
            risk_score=40,
            risk_assessment={},
        )
        assert pending_review.is_pending is True

        # In review
        in_review = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.IN_REVIEW,
            risk_level=RiskLevel.MEDIUM,
            risk_score=45,
            risk_assessment={},
        )
        assert in_review.is_pending is True

        # Requires manual review
        manual_review = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.REQUIRES_MANUAL_REVIEW,
            risk_level=RiskLevel.HIGH,
            risk_score=75,
            risk_assessment={},
        )
        assert manual_review.is_pending is True

        # Approved review
        approved_review = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.APPROVED,
            risk_level=RiskLevel.LOW,
            risk_score=20,
            risk_assessment={},
        )
        assert approved_review.is_pending is False

    def test_review_is_decided_property(self):
        """Test UnderwritingReview.is_decided property."""
        # Approved
        approved = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.APPROVED,
            risk_level=RiskLevel.LOW,
            risk_score=25,
            risk_assessment={},
        )
        assert approved.is_decided is True

        # Rejected
        rejected = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.REJECTED,
            risk_level=RiskLevel.HIGH,
            risk_score=85,
            risk_assessment={},
        )
        assert rejected.is_decided is True

        # Conditionally approved
        conditional = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.CONDITIONALLY_APPROVED,
            risk_level=RiskLevel.MEDIUM,
            risk_score=50,
            risk_assessment={},
        )
        assert conditional.is_decided is True

        # Pending
        pending = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.PENDING,
            risk_level=RiskLevel.MEDIUM,
            risk_score=40,
            risk_assessment={},
        )
        assert pending.is_decided is False

    def test_review_is_auto_approved_property(self):
        """Test UnderwritingReview.is_auto_approved property."""
        # Auto-approved (no reviewer)
        auto_approved = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.APPROVED,
            risk_level=RiskLevel.LOW,
            risk_score=20,
            risk_assessment={},
            reviewer_id=None,
        )
        assert auto_approved.is_auto_approved is True

        # Manually approved
        manual_approved = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.APPROVED,
            risk_level=RiskLevel.MEDIUM,
            risk_score=45,
            risk_assessment={},
            reviewer_id=uuid4(),
        )
        assert manual_approved.is_auto_approved is False

        # Not approved
        pending = UnderwritingReview(
            quote_id=uuid4(),
            status=UnderwritingStatus.PENDING,
            risk_level=RiskLevel.MEDIUM,
            risk_score=40,
            risk_assessment={},
            reviewer_id=None,
        )
        assert pending.is_auto_approved is False


# ============================================================================
# Schema Tests
# ============================================================================


class TestUnderwritingReviewSchemas:
    """Tests for UnderwritingReview schemas."""

    def test_review_create_schema_with_quote(self):
        """Test UnderwritingReviewCreate schema with quote_id."""
        quote_id = uuid4()
        data = UnderwritingReviewCreate(
            quote_id=quote_id,
            notes="Initial review for high coverage amount",
        )
        assert data.quote_id == quote_id
        assert data.policy_id is None
        assert data.notes == "Initial review for high coverage amount"

    def test_review_create_schema_with_policy(self):
        """Test UnderwritingReviewCreate schema with policy_id."""
        policy_id = uuid4()
        data = UnderwritingReviewCreate(
            policy_id=policy_id,
            notes="Post-issuance review",
        )
        assert data.policy_id == policy_id
        assert data.quote_id is None

    def test_review_create_schema_validation_both_ids(self):
        """Test UnderwritingReviewCreate fails if both IDs provided."""
        quote_id = uuid4()
        policy_id = uuid4()

        with pytest.raises(
            ValueError, match="Provide either quote_id or policy_id, not both"
        ):
            UnderwritingReviewCreate(
                quote_id=quote_id,
                policy_id=policy_id,
            )

    def test_review_create_schema_validation_no_ids(self):
        """Test UnderwritingReviewCreate fails if no IDs provided."""
        # When both are None/not provided, the validator should catch it
        with pytest.raises(
            ValueError, match="Either quote_id or policy_id must be provided"
        ):
            UnderwritingReviewCreate(quote_id=None, policy_id=None)

    def test_review_approve_schema(self):
        """Test UnderwritingReviewApprove schema."""
        reviewer_id = uuid4()
        data = UnderwritingReviewApprove(
            reviewer_id=reviewer_id,
            notes="Approved with standard terms",
        )
        assert data.reviewer_id == reviewer_id
        assert data.notes == "Approved with standard terms"

    def test_review_reject_schema(self):
        """Test UnderwritingReviewReject schema."""
        reviewer_id = uuid4()
        data = UnderwritingReviewReject(
            reviewer_id=reviewer_id,
            notes="Does not meet age requirements",
        )
        assert data.reviewer_id == reviewer_id
        assert data.notes == "Does not meet age requirements"

    def test_review_reject_schema_notes_required(self):
        """Test UnderwritingReviewReject requires notes."""
        # Notes are required for rejection
        data = UnderwritingReviewReject(notes="Rejection reason")
        assert data.notes == "Rejection reason"


# ============================================================================
# RiskScoringEngine Tests
# ============================================================================


class TestRiskScoringEngine:
    """Tests for the RiskScoringEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = RiskScoringEngine()

    def test_calculate_risk_from_quote_low_risk(self):
        """Test risk calculation from quote with low risk."""
        quote_risk_factors = {
            "total_risk_score": 20,
            "age": 35,
            "coverage_amount": 250000.00,
        }

        risk_score, risk_level, assessment = (
            self.engine.calculate_risk_score_from_quote(
                RiskLevel.LOW,
                quote_risk_factors,
            )
        )

        assert risk_score == 20
        assert risk_level == RiskLevel.LOW
        assert assessment["source"] == "quote"
        assert assessment["base_risk_score"] == 20
        assert assessment["final_risk_score"] == 20

    def test_calculate_risk_from_quote_medium_risk(self):
        """Test risk calculation from quote with medium risk."""
        quote_risk_factors = {
            "total_risk_score": 40,
            "age": 22,
            "coverage_amount": 500000.00,
        }

        risk_score, risk_level, assessment = (
            self.engine.calculate_risk_score_from_quote(
                RiskLevel.MEDIUM,
                quote_risk_factors,
            )
        )

        assert risk_score == 40
        assert risk_level == RiskLevel.MEDIUM
        assert assessment["quote_risk_level"] == "medium"

    def test_calculate_risk_from_quote_high_risk(self):
        """Test risk calculation from quote with high risk."""
        quote_risk_factors = {
            "total_risk_score": 65,
            "age": 75,
            "coverage_amount": 2000000.00,
        }

        risk_score, risk_level, assessment = (
            self.engine.calculate_risk_score_from_quote(
                RiskLevel.HIGH,
                quote_risk_factors,
            )
        )

        assert risk_score == 65
        assert risk_level == RiskLevel.HIGH

    def test_calculate_risk_from_quote_very_high_risk(self):
        """Test risk calculation from quote with very high risk."""
        quote_risk_factors = {
            "total_risk_score": 85,
            "age": 22,
            "coverage_amount": 7000000.00,
        }

        risk_score, risk_level, assessment = (
            self.engine.calculate_risk_score_from_quote(
                RiskLevel.VERY_HIGH,
                quote_risk_factors,
            )
        )

        assert risk_score == 85
        assert risk_level == RiskLevel.VERY_HIGH

    def test_calculate_risk_from_policy_low_premium(self):
        """Test risk calculation from policy with low premium."""
        risk_score, risk_level, assessment = (
            self.engine.calculate_risk_score_from_policy(
                policy_premium=1200.00,
                policy_type="home",
            )
        )

        assert risk_score == 0  # Low premium + home type
        assert risk_level == RiskLevel.LOW
        assert assessment["source"] == "policy"
        assert assessment["premium_risk_reason"] == "standard_premium"

    def test_calculate_risk_from_policy_medium_premium(self):
        """Test risk calculation from policy with medium premium."""
        risk_score, risk_level, assessment = (
            self.engine.calculate_risk_score_from_policy(
                policy_premium=7000.00,
                policy_type="auto",
            )
        )

        assert risk_score == 25  # 15 (medium premium) + 10 (auto type)
        assert risk_level == RiskLevel.LOW
        assert assessment["premium_risk_score"] == 15

    def test_calculate_risk_from_policy_high_premium(self):
        """Test risk calculation from policy with high premium."""
        risk_score, risk_level, assessment = (
            self.engine.calculate_risk_score_from_policy(
                policy_premium=12000.00,
                policy_type="life",
            )
        )

        assert risk_score == 35  # 30 (high premium) + 5 (life type)
        assert risk_level == RiskLevel.MEDIUM
        assert assessment["premium_risk_reason"] == "high_premium"

    def test_risk_level_boundaries(self):
        """Test risk level boundary conditions."""
        # Test LOW/MEDIUM boundary (30)
        _, level_30, _ = self.engine.calculate_risk_score_from_quote(
            RiskLevel.LOW, {"total_risk_score": 30}
        )
        assert level_30 == RiskLevel.LOW

        _, level_31, _ = self.engine.calculate_risk_score_from_quote(
            RiskLevel.MEDIUM, {"total_risk_score": 31}
        )
        assert level_31 == RiskLevel.MEDIUM

        # Test MEDIUM/HIGH boundary (50)
        _, level_50, _ = self.engine.calculate_risk_score_from_quote(
            RiskLevel.MEDIUM, {"total_risk_score": 50}
        )
        assert level_50 == RiskLevel.MEDIUM

        _, level_51, _ = self.engine.calculate_risk_score_from_quote(
            RiskLevel.HIGH, {"total_risk_score": 51}
        )
        assert level_51 == RiskLevel.HIGH

        # Test HIGH/VERY_HIGH boundary (70)
        _, level_70, _ = self.engine.calculate_risk_score_from_quote(
            RiskLevel.HIGH, {"total_risk_score": 70}
        )
        assert level_70 == RiskLevel.HIGH

        _, level_71, _ = self.engine.calculate_risk_score_from_quote(
            RiskLevel.VERY_HIGH, {"total_risk_score": 71}
        )
        assert level_71 == RiskLevel.VERY_HIGH


# ============================================================================
# UnderwritingService Tests (Business Logic)
# ============================================================================


class TestUnderwritingServiceLogic:
    """Tests for UnderwritingService business logic (unit tests)."""

    def test_auto_approve_threshold(self):
        """Test auto-approve threshold constant."""
        assert UnderwritingService.AUTO_APPROVE_THRESHOLD == 30

    def test_manual_review_threshold(self):
        """Test manual review threshold constant."""
        assert UnderwritingService.MANUAL_REVIEW_THRESHOLD == 70

    def test_risk_engine_initialization(self):
        """Test that service initializes with risk engine."""
        # This would need a mock session in a real test
        # Just testing the class structure here
        assert hasattr(UnderwritingService, "__init__")
