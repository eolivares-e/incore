"""SQLAlchemy models for the Underwriting domain."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.enums import RiskLevel, UnderwritingStatus


class UnderwritingReview(Base):
    """UnderwritingReview model.

    Represents a risk assessment and approval/rejection workflow
    for insurance quotes or policies. Used for manual review of high-risk
    applications.
    """

    __tablename__ = "underwriting_reviews"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Foreign Keys (nullable - either quote_id OR policy_id, but not both)
    quote_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    policy_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Reviewer (nullable for auto-approval)
    reviewer_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        # ForeignKey("users.id", ondelete="SET NULL"),  # TODO: Phase 7
        nullable=True,
        index=True,
    )

    # Review Status
    status: Mapped[UnderwritingStatus] = mapped_column(
        Enum(
            UnderwritingStatus,
            name="underwriting_status_enum",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=UnderwritingStatus.PENDING,
        index=True,
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
    risk_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    risk_assessment: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # Review Notes
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Decision Timestamps
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    rejected_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    quote: Mapped["Quote"] = relationship(  # noqa: F821
        "Quote",
        back_populates="underwriting_reviews",
        foreign_keys=[quote_id],
        lazy="joined",
    )
    policy: Mapped["Policy"] = relationship(  # noqa: F821
        "Policy",
        back_populates="underwriting_reviews",
        foreign_keys=[policy_id],
        lazy="joined",
    )
    # reviewer: Mapped["User"] = relationship(  # noqa: F821
    #     "User",
    #     back_populates="underwriting_reviews",
    #     lazy="joined",
    # )  # TODO: Phase 7

    # Constraints and Indexes
    __table_args__ = (
        # Ensure risk_score is between 0 and 100
        CheckConstraint(
            "risk_score >= 0 AND risk_score <= 100",
            name="ck_underwriting_reviews_risk_score_range",
        ),
        # Ensure either quote_id or policy_id is set (but not both)
        CheckConstraint(
            "(quote_id IS NOT NULL AND policy_id IS NULL) OR "
            "(quote_id IS NULL AND policy_id IS NOT NULL)",
            name="ck_underwriting_reviews_quote_or_policy",
        ),
        Index("ix_underwriting_reviews_status_risk_level", "status", "risk_level"),
        Index("ix_underwriting_reviews_quote_id_status", "quote_id", "status"),
        Index("ix_underwriting_reviews_policy_id_status", "policy_id", "status"),
    )

    def __repr__(self) -> str:
        """String representation of UnderwritingReview."""
        entity_type = "quote" if self.quote_id else "policy"
        entity_id = self.quote_id if self.quote_id else self.policy_id
        return (
            f"<UnderwritingReview(id={self.id}, "
            f"{entity_type}_id={entity_id}, "
            f"status={self.status.value}, "
            f"risk_level={self.risk_level.value}, "
            f"risk_score={self.risk_score})>"
        )

    @property
    def is_pending(self) -> bool:
        """Check if review is pending."""
        return self.status in {
            UnderwritingStatus.PENDING,
            UnderwritingStatus.IN_REVIEW,
            UnderwritingStatus.REQUIRES_MANUAL_REVIEW,
        }

    @property
    def is_decided(self) -> bool:
        """Check if a decision has been made."""
        return self.status in {
            UnderwritingStatus.APPROVED,
            UnderwritingStatus.REJECTED,
            UnderwritingStatus.CONDITIONALLY_APPROVED,
        }

    @property
    def is_auto_approved(self) -> bool:
        """Check if this was auto-approved (no reviewer)."""
        return self.status == UnderwritingStatus.APPROVED and self.reviewer_id is None
