"""Pydantic schemas for the Policyholders domain."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from app.shared.enums import Gender, IdentificationType
from app.shared.schemas.base import BaseSchema, TimestampMixin, UUIDMixin
from app.shared.types import Email, IdentificationNumber, PhoneNumber, ZipCode


# ============================================================================
# Base Schemas
# ============================================================================


class PolicyholderBase(BaseSchema):
    """Base schema with common Policyholder fields."""

    first_name: str = Field(
        min_length=1,
        max_length=100,
        description="First name of the policyholder",
        examples=["John"],
    )
    last_name: str = Field(
        min_length=1,
        max_length=100,
        description="Last name of the policyholder",
        examples=["Doe"],
    )
    email: EmailStr = Field(
        description="Email address (must be unique)",
        examples=["john.doe@example.com"],
    )
    phone: PhoneNumber = Field(
        description="Phone number with country code",
        examples=["+1-555-123-4567"],
    )
    date_of_birth: date = Field(
        description="Date of birth",
        examples=["1990-01-15"],
    )
    gender: Gender = Field(
        description="Gender",
        examples=[Gender.MALE],
    )
    street_address: str = Field(
        min_length=1,
        max_length=255,
        description="Street address",
        examples=["123 Main Street"],
    )
    city: str = Field(
        min_length=1,
        max_length=100,
        description="City",
        examples=["New York"],
    )
    state: str = Field(
        min_length=1,
        max_length=100,
        description="State or province",
        examples=["NY"],
    )
    zip_code: ZipCode = Field(
        description="ZIP or postal code",
        examples=["10001"],
    )
    country: str = Field(
        min_length=1,
        max_length=100,
        description="Country",
        examples=["USA"],
        default="USA",
    )
    identification_type: IdentificationType = Field(
        description="Type of identification document",
        examples=[IdentificationType.DRIVER_LICENSE],
    )
    identification_number: IdentificationNumber = Field(
        description="Identification document number",
        examples=["DL123456789"],
    )

    @field_validator("date_of_birth")
    @classmethod
    def validate_age(cls, v: date) -> date:
        """Validate that the policyholder is at least 18 years old."""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

        if age < 18:
            raise ValueError("Policyholder must be at least 18 years old")
        if age > 150:
            raise ValueError("Invalid date of birth")

        return v


# ============================================================================
# Request Schemas
# ============================================================================


class PolicyholderCreate(PolicyholderBase):
    """Schema for creating a new Policyholder.

    Used in POST /api/v1/policyholders
    """

    pass


class PolicyholderUpdate(BaseSchema):
    """Schema for updating a Policyholder.

    All fields are optional. Only provided fields will be updated.
    Used in PUT /api/v1/policyholders/{id}
    """

    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="First name of the policyholder",
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Last name of the policyholder",
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Email address (must be unique)",
    )
    phone: Optional[PhoneNumber] = Field(
        None,
        description="Phone number with country code",
    )
    date_of_birth: Optional[date] = Field(
        None,
        description="Date of birth",
    )
    gender: Optional[Gender] = Field(
        None,
        description="Gender",
    )
    street_address: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Street address",
    )
    city: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="City",
    )
    state: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="State or province",
    )
    zip_code: Optional[ZipCode] = Field(
        None,
        description="ZIP or postal code",
    )
    country: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Country",
    )
    identification_type: Optional[IdentificationType] = Field(
        None,
        description="Type of identification document",
    )
    identification_number: Optional[IdentificationNumber] = Field(
        None,
        description="Identification document number",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the policyholder is active",
    )

    @field_validator("date_of_birth")
    @classmethod
    def validate_age(cls, v: Optional[date]) -> Optional[date]:
        """Validate that the policyholder is at least 18 years old."""
        if v is None:
            return v

        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

        if age < 18:
            raise ValueError("Policyholder must be at least 18 years old")
        if age > 150:
            raise ValueError("Invalid date of birth")

        return v


# ============================================================================
# Response Schemas
# ============================================================================


class PolicyholderResponse(PolicyholderBase, UUIDMixin, TimestampMixin):
    """Schema for Policyholder responses.

    Includes all fields plus UUID, timestamps, and computed fields.
    Used in all GET endpoints.
    """

    is_active: bool = Field(
        description="Whether the policyholder is active",
        examples=[True],
    )

    # Override to use datetime instead of date for proper serialization
    created_at: datetime = Field(
        description="Timestamp when the policyholder was created",
    )
    updated_at: datetime = Field(
        description="Timestamp when the policyholder was last updated",
    )

    model_config = {
        "from_attributes": True,  # Enable ORM mode for SQLAlchemy models
    }


class PolicyholderListResponse(BaseSchema):
    """Schema for paginated list of policyholders.

    This is a simplified version for list endpoints.
    """

    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


# ============================================================================
# Filter Schemas
# ============================================================================


class PolicyholderFilterParams(BaseSchema):
    """Query parameters for filtering policyholders."""

    email: Optional[str] = Field(
        None,
        description="Filter by email (partial match)",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Filter by active status",
    )
    search: Optional[str] = Field(
        None,
        description="Search in first_name, last_name, or email",
    )
