"""SQLAlchemy models for the Policy Holders domain."""

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.enums import Gender, IdentificationType


class PolicyHolder(Base):
    """Policy Holder (customer) model.

    Represents an insurance policy holder with personal information,
    contact details, and identification.
    """

    __tablename__ = "policy_holders"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Personal Information
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, name="gender_enum", create_type=False),
        nullable=False,
    )

    # Contact Information
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Address
    street_address: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    zip_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="USA",
    )

    # Identification
    identification_type: Mapped[IdentificationType] = mapped_column(
        Enum(IdentificationType, name="identification_type_enum", create_type=False),
        nullable=False,
    )
    identification_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
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
    policies: Mapped[list["Policy"]] = relationship(
        "Policy",
        back_populates="policy_holder",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of PolicyHolder."""
        return (
            f"<PolicyHolder(id={self.id}, "
            f"name='{self.first_name} {self.last_name}', "
            f"email='{self.email}')>"
        )

    @property
    def full_name(self) -> str:
        """Get the full name of the policy holder."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        """Calculate the age of the policy holder."""
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )
