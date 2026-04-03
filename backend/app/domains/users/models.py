"""User domain models for authentication and authorization."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

if TYPE_CHECKING:
    pass  # For future foreign key relationships


class UserRole(str, Enum):
    """User role enumeration for role-based access control."""

    ADMIN = "admin"
    UNDERWRITER = "underwriter"
    AGENT = "agent"
    CUSTOMER = "customer"


class User(Base):
    """User model for authentication and authorization.

    Represents a system user with role-based access control.
    Supports JWT-based authentication with email/password.
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # User information
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Authorization fields
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default=UserRole.CUSTOMER.value, index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'",
            name="check_email_format",
        ),
        CheckConstraint(
            "role IN ('admin', 'underwriter', 'agent', 'customer')",
            name="check_valid_role",
        ),
        # Composite index for common queries
        {"comment": "User table for authentication and authorization"},
    )

    # Properties
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin (has ADMIN role or is superuser)."""
        return self.role == UserRole.ADMIN.value or self.is_superuser

    @property
    def is_active_and_enabled(self) -> bool:
        """Check if user is active and can use the system."""
        return self.is_active is True

    def __repr__(self) -> str:
        """String representation of User."""
        return (
            f"<User(id={self.id}, email='{self.email}', "
            f"role='{self.role}', is_active={self.is_active})>"
        )
