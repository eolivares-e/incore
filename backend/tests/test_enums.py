"""Tests for shared domain enums."""


from app.shared.enums import (
    ClaimStatus,
    CoverageType,
    Gender,
    IdentificationType,
    InvoiceStatus,
    PaymentMethod,
    PaymentStatus,
    PolicyStatus,
    PolicyType,
    QuoteStatus,
    RiskLevel,
    UnderwritingStatus,
)


def test_policy_status_enum():
    """Test PolicyStatus enum values."""
    assert PolicyStatus.DRAFT.value == "draft"
    assert PolicyStatus.ACTIVE.value == "active"
    assert PolicyStatus.EXPIRED.value == "expired"
    assert PolicyStatus.CANCELLED.value == "cancelled"
    assert PolicyStatus.SUSPENDED.value == "suspended"
    assert PolicyStatus.PENDING_APPROVAL.value == "pending_approval"
    assert PolicyStatus.PENDING_RENEWAL.value == "pending_renewal"

    # Test enum membership
    assert "active" in [s.value for s in PolicyStatus]
    assert len(list(PolicyStatus)) == 7


def test_policy_type_enum():
    """Test PolicyType enum values."""
    assert PolicyType.AUTO.value == "auto"
    assert PolicyType.HOME.value == "home"
    assert PolicyType.LIFE.value == "life"
    assert PolicyType.HEALTH.value == "health"

    assert len(list(PolicyType)) == 4


def test_claim_status_enum():
    """Test ClaimStatus enum values."""
    assert ClaimStatus.SUBMITTED.value == "submitted"
    assert ClaimStatus.UNDER_REVIEW.value == "under_review"
    assert ClaimStatus.APPROVED.value == "approved"
    assert ClaimStatus.REJECTED.value == "rejected"
    assert ClaimStatus.PAID.value == "paid"
    assert ClaimStatus.CLOSED.value == "closed"

    assert len(list(ClaimStatus)) >= 6


def test_payment_status_enum():
    """Test PaymentStatus enum values."""
    assert PaymentStatus.PENDING.value == "pending"
    assert PaymentStatus.COMPLETED.value == "completed"
    assert PaymentStatus.FAILED.value == "failed"
    assert PaymentStatus.REFUNDED.value == "refunded"
    assert PaymentStatus.CANCELLED.value == "cancelled"

    assert len(list(PaymentStatus)) >= 5


def test_payment_method_enum():
    """Test PaymentMethod enum values."""
    assert PaymentMethod.CREDIT_CARD.value == "credit_card"
    assert PaymentMethod.DEBIT_CARD.value == "debit_card"
    assert PaymentMethod.BANK_TRANSFER.value == "bank_transfer"
    assert PaymentMethod.CASH.value == "cash"
    assert PaymentMethod.CHECK.value == "check"
    assert PaymentMethod.DIGITAL_WALLET.value == "digital_wallet"

    assert len(list(PaymentMethod)) == 6


def test_underwriting_status_enum():
    """Test UnderwritingStatus enum values."""
    assert UnderwritingStatus.PENDING.value == "pending"
    assert UnderwritingStatus.IN_REVIEW.value == "in_review"
    assert UnderwritingStatus.APPROVED.value == "approved"
    assert UnderwritingStatus.REJECTED.value == "rejected"
    assert UnderwritingStatus.REQUIRES_MANUAL_REVIEW.value == "requires_manual_review"
    assert UnderwritingStatus.CONDITIONALLY_APPROVED.value == "conditionally_approved"

    assert len(list(UnderwritingStatus)) == 6


def test_coverage_type_enum():
    """Test CoverageType enum values."""
    # Auto coverages
    assert CoverageType.LIABILITY.value == "liability"
    assert CoverageType.COLLISION.value == "collision"
    assert CoverageType.COMPREHENSIVE.value == "comprehensive"

    # Home coverages
    assert CoverageType.DWELLING.value == "dwelling"
    assert CoverageType.PERSONAL_PROPERTY.value == "personal_property"

    # Life coverages
    assert CoverageType.DEATH_BENEFIT.value == "death_benefit"
    assert CoverageType.ACCIDENTAL_DEATH.value == "accidental_death"

    # Health coverages
    assert CoverageType.MEDICAL.value == "medical"
    assert CoverageType.DENTAL.value == "dental"
    assert CoverageType.VISION.value == "vision"

    assert len(list(CoverageType)) >= 10


def test_gender_enum():
    """Test Gender enum values."""
    assert Gender.MALE.value == "male"
    assert Gender.FEMALE.value == "female"
    assert Gender.OTHER.value == "other"
    assert Gender.PREFER_NOT_TO_SAY.value == "prefer_not_to_say"

    assert len(list(Gender)) == 4


def test_risk_level_enum():
    """Test RiskLevel enum values."""
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.MEDIUM.value == "medium"
    assert RiskLevel.HIGH.value == "high"
    assert RiskLevel.VERY_HIGH.value == "very_high"

    assert len(list(RiskLevel)) == 4


def test_identification_type_enum():
    """Test IdentificationType enum values."""
    assert IdentificationType.PASSPORT.value == "passport"
    assert IdentificationType.DRIVER_LICENSE.value == "driver_license"
    assert IdentificationType.NATIONAL_ID.value == "national_id"
    assert IdentificationType.SSN.value == "ssn"
    assert IdentificationType.TAX_ID.value == "tax_id"
    assert IdentificationType.OTHER.value == "other"

    assert len(list(IdentificationType)) == 6


def test_quote_status_enum():
    """Test QuoteStatus enum values."""
    assert QuoteStatus.DRAFT.value == "draft"
    assert QuoteStatus.PENDING.value == "pending"
    assert QuoteStatus.ACTIVE.value == "active"
    assert QuoteStatus.ACCEPTED.value == "accepted"
    assert QuoteStatus.REJECTED.value == "rejected"
    assert QuoteStatus.EXPIRED.value == "expired"
    assert QuoteStatus.CONVERTED_TO_POLICY.value == "converted_to_policy"

    assert len(list(QuoteStatus)) == 7


def test_invoice_status_enum():
    """Test InvoiceStatus enum values."""
    assert InvoiceStatus.DRAFT.value == "draft"
    assert InvoiceStatus.PENDING.value == "pending"
    assert InvoiceStatus.SENT.value == "sent"
    assert InvoiceStatus.PAID.value == "paid"
    assert InvoiceStatus.OVERDUE.value == "overdue"
    assert InvoiceStatus.PARTIALLY_PAID.value == "partially_paid"
    assert InvoiceStatus.CANCELLED.value == "cancelled"
    assert InvoiceStatus.REFUNDED.value == "refunded"

    assert len(list(InvoiceStatus)) == 8


def test_enum_string_inheritance():
    """Test that all enums are proper string enums."""
    # This ensures enums can be used directly as strings in APIs
    assert isinstance(PolicyStatus.ACTIVE, str)
    assert isinstance(PolicyType.AUTO, str)
    assert isinstance(PaymentStatus.COMPLETED, str)

    # Test string operations work
    assert PolicyStatus.ACTIVE == "active"
    assert PolicyStatus.ACTIVE.upper() == "ACTIVE"
