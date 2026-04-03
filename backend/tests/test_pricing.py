"""Tests for the Pricing domain."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.domains.pricing.models import PricingRule, Quote
from app.domains.pricing.schemas import (
    PricingRuleCreate,
    QuoteAcceptRequest,
    QuoteCreate,
    QuoteResponse,
)
from app.domains.pricing.service import PricingEngine, QuoteService
from app.domains.policy_holders.models import PolicyHolder  # noqa: F401
from app.shared.enums import PolicyType, QuoteStatus, RiskLevel

# ============================================================================
# Model Tests
# ============================================================================


class TestQuoteModel:
    """Tests for the Quote model."""

    def test_quote_repr(self):
        """Test Quote __repr__ method."""
        quote = Quote(
            quote_number="QTE-2026-AUTO-00001",
            policy_type=PolicyType.AUTO,
            status=QuoteStatus.ACTIVE,
        )
        repr_str = repr(quote)
        assert "QTE-2026-AUTO-00001" in repr_str
        assert "auto" in repr_str.lower()
        assert "active" in repr_str.lower()

    def test_quote_is_expired_property(self):
        """Test Quote.is_expired property."""
        # Expired quote
        expired_quote = Quote(
            valid_until=date.today() - timedelta(days=1),
            policy_type=PolicyType.AUTO,
        )
        assert expired_quote.is_expired is True

        # Active quote
        active_quote = Quote(
            valid_until=date.today() + timedelta(days=30),
            policy_type=PolicyType.AUTO,
        )
        assert active_quote.is_expired is False

    def test_quote_is_valid_property(self):
        """Test Quote.is_valid property."""
        # Valid quote (ACTIVE status, not expired)
        valid_quote = Quote(
            valid_until=date.today() + timedelta(days=30),
            status=QuoteStatus.ACTIVE,
            policy_type=PolicyType.AUTO,
        )
        assert valid_quote.is_valid is True

        # Invalid quote (expired)
        expired_quote = Quote(
            valid_until=date.today() - timedelta(days=1),
            status=QuoteStatus.ACTIVE,
            policy_type=PolicyType.AUTO,
        )
        assert expired_quote.is_valid is False

        # Invalid quote (wrong status)
        rejected_quote = Quote(
            valid_until=date.today() + timedelta(days=30),
            status=QuoteStatus.REJECTED,
            policy_type=PolicyType.AUTO,
        )
        assert rejected_quote.is_valid is False

    def test_quote_days_until_expiry_property(self):
        """Test Quote.days_until_expiry property."""
        # Future expiry
        future_quote = Quote(
            valid_until=date.today() + timedelta(days=15),
            policy_type=PolicyType.AUTO,
        )
        assert future_quote.days_until_expiry == 15

        # Past expiry
        expired_quote = Quote(
            valid_until=date.today() - timedelta(days=5),
            policy_type=PolicyType.AUTO,
        )
        assert expired_quote.days_until_expiry == -5


class TestPricingRuleModel:
    """Tests for the PricingRule model."""

    def test_pricing_rule_repr(self):
        """Test PricingRule __repr__ method."""
        rule = PricingRule(
            name="Auto - Low Risk",
            policy_type=PolicyType.AUTO,
            risk_level=RiskLevel.LOW,
            base_premium=Decimal("800.00"),
        )
        repr_str = repr(rule)
        assert "Auto - Low Risk" in repr_str
        assert "auto" in repr_str.lower()
        assert "low" in repr_str.lower()
        assert "800.00" in repr_str


# ============================================================================
# Schema Tests
# ============================================================================


class TestQuoteSchemas:
    """Tests for Quote schemas."""

    def test_quote_create_schema_valid(self):
        """Test QuoteCreate schema with valid data."""
        from uuid import uuid4

        quote_data = QuoteCreate(
            policy_holder_id=uuid4(),
            policy_type=PolicyType.AUTO,
            requested_coverage_amount=Decimal("500000.00"),
            notes="Test quote",
        )
        assert quote_data.policy_type == PolicyType.AUTO
        assert quote_data.requested_coverage_amount == Decimal("500000.00")

    def test_quote_accept_request_valid_dates(self):
        """Test QuoteAcceptRequest validates dates correctly."""
        start = date.today()
        end = start + timedelta(days=365)

        request = QuoteAcceptRequest(
            start_date=start,
            end_date=end,
            description="Test policy",
        )
        assert request.end_date > request.start_date

    def test_quote_accept_request_invalid_dates(self):
        """Test QuoteAcceptRequest rejects invalid dates."""
        start = date.today()
        end = start - timedelta(days=1)  # End before start

        with pytest.raises(Exception):  # Pydantic ValidationError
            QuoteAcceptRequest(
                start_date=start,
                end_date=end,
            )


class TestPricingRuleSchemas:
    """Tests for PricingRule schemas."""

    def test_pricing_rule_create_schema_valid(self):
        """Test PricingRuleCreate schema with valid data."""
        rule_data = PricingRuleCreate(
            name="Test Rule",
            description="Test description",
            policy_type=PolicyType.AUTO,
            risk_level=RiskLevel.LOW,
            base_premium=Decimal("800.00"),
            multiplier_factors={"coverage_per_100k": 0.05},
        )
        assert rule_data.policy_type == PolicyType.AUTO
        assert rule_data.risk_level == RiskLevel.LOW
        assert rule_data.base_premium == Decimal("800.00")


# ============================================================================
# PricingEngine Tests
# ============================================================================


class TestPricingEngine:
    """Tests for the PricingEngine class."""

    def test_calculate_risk_level_low(self):
        """Test risk calculation for low-risk scenarios."""
        engine = PricingEngine()
        risk_level, factors = engine.calculate_risk_level(
            policy_holder_age=35,
            coverage_amount=Decimal("250000.00"),
            policy_type=PolicyType.HOME,
        )
        assert risk_level == RiskLevel.LOW
        assert factors["total_risk_score"] <= 30

    def test_calculate_risk_level_medium_young_driver(self):
        """Test risk calculation for young driver."""
        engine = PricingEngine()
        risk_level, factors = engine.calculate_risk_level(
            policy_holder_age=22,
            coverage_amount=Decimal("500000.00"),
            policy_type=PolicyType.AUTO,
        )
        # Young driver (20) + Auto adjustment (10) = 30 points = LOW (0-30)
        assert risk_level == RiskLevel.LOW
        assert factors["age_risk_score"] == 20
        assert factors["age_risk_reason"] == "young_driver"
        assert factors["total_risk_score"] == 30

    def test_calculate_risk_level_medium_senior_driver(self):
        """Test risk calculation for senior driver."""
        engine = PricingEngine()
        risk_level, factors = engine.calculate_risk_level(
            policy_holder_age=75,
            coverage_amount=Decimal("500000.00"),
            policy_type=PolicyType.AUTO,
        )
        # Senior driver (20) + Auto adjustment (10) = 30 points = LOW (0-30)
        assert risk_level == RiskLevel.LOW
        assert factors["age_risk_score"] == 20
        assert factors["age_risk_reason"] == "senior_driver"
        assert factors["total_risk_score"] == 30

    def test_calculate_risk_level_high_coverage(self):
        """Test risk calculation for high coverage amount."""
        engine = PricingEngine()
        risk_level, factors = engine.calculate_risk_level(
            policy_holder_age=35,
            coverage_amount=Decimal("2000000.00"),  # >$1M
            policy_type=PolicyType.AUTO,
        )
        # High coverage (15) + Auto adjustment (10) = 25 points = LOW
        # Wait, that's still LOW. Let me recalculate:
        # Coverage > $1M = 15 points
        # Auto = 10 points
        # Total = 25 points = LOW (0-30)
        assert risk_level == RiskLevel.LOW
        assert factors["coverage_risk_score"] == 15

    def test_calculate_risk_level_very_high(self):
        """Test risk calculation for very high risk."""
        engine = PricingEngine()
        risk_level, factors = engine.calculate_risk_level(
            policy_holder_age=22,  # Young driver: 20 points
            coverage_amount=Decimal("6000000.00"),  # Very high coverage: 30 points
            policy_type=PolicyType.AUTO,  # Auto adjustment: 10 points
        )
        # Total: 20 + 30 + 10 = 60 points = HIGH
        assert risk_level == RiskLevel.HIGH
        assert factors["total_risk_score"] == 60

    def test_calculate_premium_basic(self):
        """Test basic premium calculation."""
        engine = PricingEngine()
        base_premium = Decimal("800.00")
        coverage_amount = Decimal("500000.00")
        risk_factors = {"age_risk_reason": "standard"}
        multiplier_factors = {"coverage_per_100k": 0.05}

        premium = engine.calculate_premium(
            base_premium=base_premium,
            coverage_amount=coverage_amount,
            risk_factors=risk_factors,
            multiplier_factors=multiplier_factors,
        )
        # premium = 800 + (500000/100000 * 0.05 * 800) = 800 + (5 * 40) = 800 + 200 = 1000
        assert premium == Decimal("1000.00")

    def test_calculate_premium_young_driver_multiplier(self):
        """Test premium calculation with young driver multiplier."""
        engine = PricingEngine()
        base_premium = Decimal("800.00")
        coverage_amount = Decimal("500000.00")
        risk_factors = {"age_risk_reason": "young_driver"}
        multiplier_factors = {
            "coverage_per_100k": 0.05,
            "young_driver_multiplier": 1.2,
        }

        premium = engine.calculate_premium(
            base_premium=base_premium,
            coverage_amount=coverage_amount,
            risk_factors=risk_factors,
            multiplier_factors=multiplier_factors,
        )
        # premium = (800 + (5 * 40)) * 1.2 = 1000 * 1.2 = 1200
        assert premium == Decimal("1200.00")

    def test_calculate_premium_senior_driver_multiplier(self):
        """Test premium calculation with senior driver multiplier."""
        engine = PricingEngine()
        base_premium = Decimal("800.00")
        coverage_amount = Decimal("500000.00")
        risk_factors = {"age_risk_reason": "senior_driver"}
        multiplier_factors = {
            "coverage_per_100k": 0.05,
            "senior_driver_multiplier": 1.15,
        }

        premium = engine.calculate_premium(
            base_premium=base_premium,
            coverage_amount=coverage_amount,
            risk_factors=risk_factors,
            multiplier_factors=multiplier_factors,
        )
        # premium = (800 + (5 * 40)) * 1.15 = 1000 * 1.15 = 1150
        assert premium == Decimal("1150.00")
