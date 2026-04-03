"""SQLAlchemy models for the Pricing domain."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.enums import PolicyType, QuoteStatus, RiskLevel


class Quote(Base):
    """Quote model.

    Represents an insurance quote with calculated premium,
    risk assessment, and relationship to a policyholder.
    """

    __tablename__ = "quotes"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Quote Identification
    quote_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    # Foreign Key to PolicyHolder
    policy_holder_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy_holders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Quote Details
    policy_type: Mapped[PolicyType] = mapped_column(
        Enum(PolicyType, name="policy_type_enum", create_type=False),
        nullable=False,
        index=True,
    )

    # Coverage & Premium
    requested_coverage_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    calculated_premium: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Risk Assessment
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(
            RiskLevel,
            name="risk_level_enum",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    risk_factors: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # Validity
    valid_until: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    # Status
    status: Mapped[QuoteStatus] = mapped_column(
        Enum(QuoteStatus, name="quote_status_enum", create_type=False),
        nullable=False,
        default=QuoteStatus.DRAFT,
        index=True,
    )

    # Optional fields
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    policy_holder: Mapped["PolicyHolder"] = relationship(  # noqa: F821
        "PolicyHolder",
        back_populates="quotes",
        lazy="joined",
    )

    # Indexes
    __table_args__ = (
        Index("ix_quotes_policy_holder_id_status", "policy_holder_id", "status"),
        Index("ix_quotes_policy_type_risk_level", "policy_type", "risk_level"),
        Index("ix_quotes_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation of Quote."""
        return (
            f"<Quote(id={self.id}, "
            f"quote_number='{self.quote_number}', "
            f"policy_type={self.policy_type.value}, "
            f"status={self.status.value})>"
        )

    @property
    def is_expired(self) -> bool:
        """Check if the quote has expired."""
        return date.today() > self.valid_until

    @property
    def is_valid(self) -> bool:
        """Check if the quote is still valid (not expired and status is valid)."""
        valid_statuses = {QuoteStatus.ACTIVE, QuoteStatus.PENDING}
        return not self.is_expired and self.status in valid_statuses

    @property
    def days_until_expiry(self) -> int:
        """Calculate days until expiry (negative if expired)."""
        return (self.valid_until - date.today()).days


class PricingRule(Base):
    """PricingRule model.

    Represents pricing rules for different policy types and risk levels.
    Used by the pricing engine to calculate premiums.
    """

    __tablename__ = "pricing_rules"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Rule Identification
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Rule Scope
    policy_type: Mapped[PolicyType] = mapped_column(
        Enum(PolicyType, name="policy_type_enum", create_type=False),
        nullable=False,
        index=True,
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(
            RiskLevel,
            name="risk_level_enum",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )

    # Pricing Parameters
    base_premium: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    multiplier_factors: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Constraints
    __table_args__ = (
        # Only one active rule per policy_type + risk_level combination
        UniqueConstraint(
            "policy_type",
            "risk_level",
            "is_active",
            name="uq_pricing_rules_policy_type_risk_level_active",
        ),
        # Ensure base_premium is positive
        CheckConstraint(
            "base_premium > 0", name="ck_pricing_rules_base_premium_positive"
        ),
        Index("ix_pricing_rules_policy_type_risk_level", "policy_type", "risk_level"),
    )

    def __repr__(self) -> str:
        """String representation of PricingRule."""
        return (
            f"<PricingRule(id={self.id}, "
            f"name='{self.name}', "
            f"policy_type={self.policy_type.value}, "
            f"risk_level={self.risk_level.value}, "
            f"base_premium={self.base_premium})>"
        )
