"""Insurance domain enumerations.

This module contains all enum types used across the insurance core system.
All enums use string values for better readability in APIs and databases.
"""

from enum import Enum


class _CaseInsensitiveMixin:
    """Mixin that makes Enum accept values case-insensitively."""

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


class PolicyStatus(_CaseInsensitiveMixin, str, Enum):
    """Status of an insurance policy."""

    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    PENDING_RENEWAL = "PENDING_RENEWAL"


class PolicyType(_CaseInsensitiveMixin, str, Enum):
    """Type of insurance policy."""

    AUTO = "AUTO"
    HOME = "HOME"
    LIFE = "LIFE"
    HEALTH = "HEALTH"


class ClaimStatus(_CaseInsensitiveMixin, str, Enum):
    """Status of an insurance claim."""

    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    CLOSED = "closed"
    APPEALED = "appealed"


class PaymentStatus(_CaseInsensitiveMixin, str, Enum):
    """Status of a payment transaction."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CANCELLED = "cancelled"


class PaymentMethod(_CaseInsensitiveMixin, str, Enum):
    """Method used for payment."""

    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHECK = "check"
    DIGITAL_WALLET = "digital_wallet"


class UnderwritingStatus(_CaseInsensitiveMixin, str, Enum):
    """Status of underwriting review process."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"
    CONDITIONALLY_APPROVED = "conditionally_approved"


class CoverageType(_CaseInsensitiveMixin, str, Enum):
    """Type of coverage provided by a policy.

    Note: Different policy types may use different coverage types.
    """

    # Auto insurance coverages
    LIABILITY = "LIABILITY"
    COLLISION = "COLLISION"
    COMPREHENSIVE = "COMPREHENSIVE"
    PERSONAL_INJURY_PROTECTION = "PERSONAL_INJURY_PROTECTION"
    UNINSURED_MOTORIST = "UNINSURED_MOTORIST"

    # Home insurance coverages
    DWELLING = "DWELLING"
    PERSONAL_PROPERTY = "PERSONAL_PROPERTY"
    LIABILITY_HOME = "LIABILITY_HOME"
    ADDITIONAL_LIVING_EXPENSES = "ADDITIONAL_LIVING_EXPENSES"

    # Life insurance coverages
    DEATH_BENEFIT = "DEATH_BENEFIT"
    ACCIDENTAL_DEATH = "ACCIDENTAL_DEATH"
    CRITICAL_ILLNESS = "CRITICAL_ILLNESS"

    # Health insurance coverages
    MEDICAL = "MEDICAL"
    DENTAL = "DENTAL"
    VISION = "VISION"
    PRESCRIPTION = "PRESCRIPTION"
    MENTAL_HEALTH = "MENTAL_HEALTH"

    # General
    OTHER = "OTHER"


class Gender(_CaseInsensitiveMixin, str, Enum):
    """Gender identification."""

    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class RiskLevel(_CaseInsensitiveMixin, str, Enum):
    """Risk level assessment for underwriting."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class IdentificationType(_CaseInsensitiveMixin, str, Enum):
    """Type of identification document."""

    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    NATIONAL_ID = "national_id"
    SSN = "ssn"
    TAX_ID = "tax_id"
    OTHER = "other"


class QuoteStatus(_CaseInsensitiveMixin, str, Enum):
    """Status of an insurance quote."""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED_TO_POLICY = "converted_to_policy"


class InvoiceStatus(_CaseInsensitiveMixin, str, Enum):
    """Status of an invoice."""

    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIALLY_PAID = "partially_paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
