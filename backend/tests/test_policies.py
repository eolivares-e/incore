"""Tests for the Policies domain."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domains.policies.models import Coverage, Policy
from app.domains.policies.schemas import (
    CoverageCreate,
    PolicyCreate,
    PolicyResponse,
    PolicyUpdate,
)
from app.domains.policy_holders.models import (
    PolicyHolder,  # noqa: F401 - needed for SQLAlchemy relationship resolution
)
from app.shared.enums import CoverageType, PolicyStatus, PolicyType

# ============================================================================
# Model Tests
# ============================================================================


class TestPolicyModel:
    """Tests for the Policy model."""

    def test_policy_repr(self):
        """Test Policy __repr__ method."""
        policy = Policy(
            policy_number="POL-2026-AUTO-00001",
            policy_type=PolicyType.AUTO,
            status=PolicyStatus.DRAFT,
        )
        repr_str = repr(policy)
        assert "POL-2026-AUTO-00001" in repr_str
        assert "auto" in repr_str.lower()
        assert "draft" in repr_str.lower()

    def test_policy_is_expired_property(self):
        """Test Policy.is_expired property."""
        # Expired policy
        expired_policy = Policy(
            end_date=date.today() - timedelta(days=1),
            policy_type=PolicyType.AUTO,
        )
        assert expired_policy.is_expired is True

        # Active policy
        active_policy = Policy(
            end_date=date.today() + timedelta(days=30),
            policy_type=PolicyType.AUTO,
        )
        assert active_policy.is_expired is False

    def test_policy_is_renewable_property(self):
        """Test Policy.is_renewable property."""
        # Renewable (within 30 days of expiration)
        renewable_policy = Policy(
            end_date=date.today() + timedelta(days=15),
            policy_type=PolicyType.AUTO,
        )
        assert renewable_policy.is_renewable is True

        # Not renewable (too far in the future)
        future_policy = Policy(
            end_date=date.today() + timedelta(days=60),
            policy_type=PolicyType.AUTO,
        )
        assert future_policy.is_renewable is False

        # Expired (not renewable)
        expired_policy = Policy(
            end_date=date.today() - timedelta(days=1),
            policy_type=PolicyType.AUTO,
        )
        assert expired_policy.is_renewable is False

    def test_policy_duration_days_property(self):
        """Test Policy.duration_days property."""
        start = date.today()
        end = date.today() + timedelta(days=365)
        policy = Policy(
            start_date=start,
            end_date=end,
            policy_type=PolicyType.AUTO,
        )
        assert policy.duration_days == 365


class TestCoverageModel:
    """Tests for the Coverage model."""

    def test_coverage_repr(self):
        """Test Coverage __repr__ method."""
        coverage = Coverage(
            coverage_type=CoverageType.LIABILITY,
            coverage_name="Liability Coverage",
            coverage_amount=Decimal("100000.00"),
        )
        repr_str = repr(coverage)
        assert "liability" in repr_str.lower()
        assert "Liability Coverage" in repr_str
        assert "100000" in repr_str


# ============================================================================
# Schema Tests
# ============================================================================


class TestPolicySchemas:
    """Tests for Policy Pydantic schemas."""

    def test_policy_create_valid(self):
        """Test PolicyCreate with valid data."""
        policy_data = PolicyCreate(
            policyholder_id="123e4567-e89b-12d3-a456-426614174000",
            policy_type=PolicyType.AUTO,
            premium_amount=Decimal("1200.00"),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            coverages=[
                CoverageCreate(
                    coverage_type=CoverageType.LIABILITY,
                    coverage_name="Liability Coverage",
                    coverage_amount=Decimal("100000.00"),
                    deductible=Decimal("500.00"),
                )
            ],
        )
        assert policy_data.policy_type == PolicyType.AUTO
        assert len(policy_data.coverages) == 1

    def test_policy_create_end_date_validation(self):
        """Test PolicyCreate validates end_date is after start_date."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyCreate(
                policyholder_id="123e4567-e89b-12d3-a456-426614174000",
                policy_type=PolicyType.AUTO,
                premium_amount=Decimal("1200.00"),
                start_date=date.today(),
                end_date=date.today() - timedelta(days=1),  # Invalid: before start
                coverages=[
                    CoverageCreate(
                        coverage_type=CoverageType.LIABILITY,
                        coverage_name="Liability Coverage",
                        coverage_amount=Decimal("100000.00"),
                    )
                ],
            )
        assert "end_date must be after start_date" in str(exc_info.value)

    def test_policy_create_requires_coverage(self):
        """Test PolicyCreate requires at least one coverage."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyCreate(
                policyholder_id="123e4567-e89b-12d3-a456-426614174000",
                policy_type=PolicyType.AUTO,
                premium_amount=Decimal("1200.00"),
                start_date=date.today(),
                end_date=date.today() + timedelta(days=365),
                coverages=[],  # Empty list
            )
        assert "at least one coverage" in str(exc_info.value).lower()

    def test_policy_create_duplicate_coverage_types(self):
        """Test PolicyCreate rejects duplicate coverage types."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyCreate(
                policyholder_id="123e4567-e89b-12d3-a456-426614174000",
                policy_type=PolicyType.AUTO,
                premium_amount=Decimal("1200.00"),
                start_date=date.today(),
                end_date=date.today() + timedelta(days=365),
                coverages=[
                    CoverageCreate(
                        coverage_type=CoverageType.LIABILITY,
                        coverage_name="Liability 1",
                        coverage_amount=Decimal("100000.00"),
                    ),
                    CoverageCreate(
                        coverage_type=CoverageType.LIABILITY,  # Duplicate type
                        coverage_name="Liability 2",
                        coverage_amount=Decimal("200000.00"),
                    ),
                ],
            )
        assert "duplicate" in str(exc_info.value).lower()

    def test_policy_update_valid(self):
        """Test PolicyUpdate with partial data."""
        update_data = PolicyUpdate(
            status=PolicyStatus.ACTIVE,
            premium_amount=Decimal("1500.00"),
        )
        assert update_data.status == PolicyStatus.ACTIVE
        assert update_data.premium_amount == Decimal("1500.00")
        assert update_data.policy_type is None  # Not provided

    def test_policy_response_from_model(self):
        """Test PolicyResponse can be created from a Policy model."""
        # This would need a real model instance from the database
        # For now, just test schema structure
        response = PolicyResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            policy_number="POL-2026-AUTO-00001",
            policyholder_id="987e6543-e21b-12d3-a456-426614174999",
            policy_type=PolicyType.AUTO,
            status=PolicyStatus.ACTIVE,
            premium_amount=Decimal("1200.00"),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            coverages=[],
        )
        assert response.policy_number == "POL-2026-AUTO-00001"
        assert response.policy_type == PolicyType.AUTO


class TestCoverageSchemas:
    """Tests for Coverage Pydantic schemas."""

    def test_coverage_create_valid(self):
        """Test CoverageCreate with valid data."""
        coverage = CoverageCreate(
            coverage_type=CoverageType.LIABILITY,
            coverage_name="Liability Coverage",
            coverage_amount=Decimal("100000.00"),
            deductible=Decimal("500.00"),
        )
        assert coverage.coverage_type == CoverageType.LIABILITY
        assert coverage.deductible == Decimal("500.00")

    def test_coverage_create_positive_amount(self):
        """Test CoverageCreate validates positive coverage_amount."""
        with pytest.raises(ValidationError) as exc_info:
            CoverageCreate(
                coverage_type=CoverageType.LIABILITY,
                coverage_name="Liability Coverage",
                coverage_amount=Decimal("0.00"),  # Must be > 0
            )
        assert "greater than 0" in str(exc_info.value).lower()

    def test_coverage_create_non_negative_deductible(self):
        """Test CoverageCreate validates non-negative deductible."""
        with pytest.raises(ValidationError) as exc_info:
            CoverageCreate(
                coverage_type=CoverageType.LIABILITY,
                coverage_name="Liability Coverage",
                coverage_amount=Decimal("100000.00"),
                deductible=Decimal("-100.00"),  # Must be >= 0
            )
        assert "greater than or equal to 0" in str(exc_info.value).lower()


# ============================================================================
# Enum Tests
# ============================================================================


class TestPolicyEnums:
    """Tests for Policy-related enums."""

    def test_policy_type_enum(self):
        """Test PolicyType enum values."""
        # Note: SQLAlchemy stores enums as lowercase in database
        assert PolicyType.AUTO.name == "AUTO"
        assert PolicyType.HEALTH.name == "HEALTH"
        assert PolicyType.LIFE.name == "LIFE"
        assert PolicyType.HOME.name == "HOME"
        # PolicyType only has 4 values (no TRAVEL in MVP)

    def test_policy_status_enum(self):
        """Test PolicyStatus enum values."""
        # Note: SQLAlchemy stores enums as lowercase in database
        assert PolicyStatus.DRAFT.name == "DRAFT"
        assert PolicyStatus.ACTIVE.name == "ACTIVE"
        assert PolicyStatus.EXPIRED.name == "EXPIRED"
        assert PolicyStatus.CANCELLED.name == "CANCELLED"

    def test_coverage_type_enum(self):
        """Test CoverageType enum has expected values."""
        # Note: SQLAlchemy stores enums as lowercase in database
        assert CoverageType.LIABILITY.name == "LIABILITY"
        assert CoverageType.COLLISION.name == "COLLISION"
        assert CoverageType.MEDICAL.name == "MEDICAL"
