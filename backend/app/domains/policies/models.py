"""SQLAlchemy models for the Policies domain."""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.enums import CoverageType, PolicyStatus, PolicyType


class Policy(Base):
    """Policy model.

    Represents an insurance policy with its terms, coverage details,
    and relationship to a policyholder.
    """

    __tablename__ = "policies"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Policy Identification
    policy_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    # Foreign Key to PolicyHolder
    policyholder_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy_holders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Policy Details
    policy_type: Mapped[PolicyType] = mapped_column(
        Enum(PolicyType, name="policy_type_enum", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus, name="policy_status_enum", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PolicyStatus.DRAFT,
        index=True,
    )

    # Premium Information (in cents/smallest currency unit)
    premium_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Policy Period
    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    # Optional fields
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
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
        back_populates="policies",
        lazy="joined",
    )
    coverages: Mapped[list["Coverage"]] = relationship(
        "Coverage",
        back_populates="policy",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    underwriting_reviews: Mapped[list["UnderwritingReview"]] = relationship(  # noqa: F821
        "UnderwritingReview",
        back_populates="policy",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    invoices: Mapped[list["Invoice"]] = relationship(  # noqa: F821
        "Invoice",
        back_populates="policy",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Composite indexes for common query patterns
    __table_args__ = (
        Index(
            "ix_policies_policyholder_status",
            "policyholder_id",
            "status",
        ),
        Index("ix_policies_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation of Policy."""
        return (
            f"<Policy(id={self.id}, "
            f"policy_number='{self.policy_number}', "
            f"type={self.policy_type.value}, "
            f"status={self.status.value})>"
        )

    @property
    def is_expired(self) -> bool:
        """Check if the policy has expired."""
        return date.today() > self.end_date

    @property
    def is_renewable(self) -> bool:
        """Check if the policy is renewable (within 30 days of expiration)."""
        days_until_expiry = (self.end_date - date.today()).days
        return 0 <= days_until_expiry <= 30

    @property
    def duration_days(self) -> int:
        """Calculate the duration of the policy in days."""
        return (self.end_date - self.start_date).days


class Coverage(Base):
    """Coverage model.

    Represents a specific coverage item within a policy,
    defining what is covered and the coverage limits.
    """

    __tablename__ = "coverages"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Foreign Key to Policy
    policy_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Coverage Details
    coverage_type: Mapped[CoverageType] = mapped_column(
        Enum(CoverageType, name="coverage_type_enum", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    coverage_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Coverage Amounts (in cents/smallest currency unit)
    coverage_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    deductible: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
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
    policy: Mapped["Policy"] = relationship(
        "Policy",
        back_populates="coverages",
    )

    def __repr__(self) -> str:
        """String representation of Coverage."""
        return (
            f"<Coverage(id={self.id}, "
            f"type={self.coverage_type.value}, "
            f"name='{self.coverage_name}', "
            f"amount={self.coverage_amount})>"
        )
