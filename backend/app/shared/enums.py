"""Insurance domain enumerations.

This module contains all enum types used across the insurance core system.
All enums use string values for better readability in APIs and databases.
"""

from enum import Enum


class PolicyStatus(str, Enum):
    """Status of an insurance policy."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING_RENEWAL = "pending_renewal"


class PolicyType(str, Enum):
    """Type of insurance policy."""

    AUTO = "auto"
    HOME = "home"
    LIFE = "life"
    HEALTH = "health"


class ClaimStatus(str, Enum):
    """Status of an insurance claim."""

    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    CLOSED = "closed"
    APPEALED = "appealed"


class PaymentStatus(str, Enum):
    """Status of a payment transaction."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    """Method used for payment."""

    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHECK = "check"
    DIGITAL_WALLET = "digital_wallet"


class UnderwritingStatus(str, Enum):
    """Status of underwriting review process."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"
    CONDITIONALLY_APPROVED = "conditionally_approved"


class CoverageType(str, Enum):
    """Type of coverage provided by a policy.

    Note: Different policy types may use different coverage types.
    """

    # Auto insurance coverages
    LIABILITY = "liability"
    COLLISION = "collision"
    COMPREHENSIVE = "comprehensive"
    PERSONAL_INJURY_PROTECTION = "personal_injury_protection"
    UNINSURED_MOTORIST = "uninsured_motorist"

    # Home insurance coverages
    DWELLING = "dwelling"
    PERSONAL_PROPERTY = "personal_property"
    LIABILITY_HOME = "liability_home"
    ADDITIONAL_LIVING_EXPENSES = "additional_living_expenses"

    # Life insurance coverages
    DEATH_BENEFIT = "death_benefit"
    ACCIDENTAL_DEATH = "accidental_death"
    CRITICAL_ILLNESS = "critical_illness"

    # Health insurance coverages
    MEDICAL = "medical"
    DENTAL = "dental"
    VISION = "vision"
    PRESCRIPTION = "prescription"
    MENTAL_HEALTH = "mental_health"

    # General
    OTHER = "other"


class Gender(str, Enum):
    """Gender identification."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class RiskLevel(str, Enum):
    """Risk level assessment for underwriting."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class IdentificationType(str, Enum):
    """Type of identification document."""

    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    NATIONAL_ID = "national_id"
    SSN = "ssn"
    TAX_ID = "tax_id"
    OTHER = "other"


class QuoteStatus(str, Enum):
    """Status of an insurance quote."""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED_TO_POLICY = "converted_to_policy"


class InvoiceStatus(str, Enum):
    """Status of an invoice."""

    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIALLY_PAID = "partially_paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
