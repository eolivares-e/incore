"""Tests for Policyholder domain."""

from datetime import date, datetime
from uuid import uuid4

import pytest

from app.domains.policy_holders.schemas import (
    PolicyHolderCreate as PolicyholderCreate,
    PolicyHolderResponse as PolicyholderResponse,
    PolicyHolderUpdate as PolicyholderUpdate,
)
from app.shared.enums import Gender, IdentificationType

# ============================================================================
# Schema Tests
# ============================================================================


def test_policyholder_create_schema_valid():
    """Test creating a valid PolicyholderCreate schema."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567",
        "date_of_birth": "1990-01-15",
        "gender": Gender.MALE,
        "street_address": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country": "USA",
        "identification_type": IdentificationType.DRIVER_LICENSE,
        "identification_number": "DL123456789",
    }

    schema = PolicyholderCreate(**data)
    assert schema.first_name == "John"
    assert schema.last_name == "Doe"
    assert schema.email == "john.doe@example.com"
    assert schema.gender == Gender.MALE


def test_policyholder_create_age_validation_too_young():
    """Test that policyholders under 18 are rejected."""
    today = date.today()
    too_young_date = date(today.year - 17, today.month, today.day)

    data = {
        "first_name": "Young",
        "last_name": "Person",
        "email": "young@example.com",
        "phone": "+1-555-123-4567",
        "date_of_birth": too_young_date,
        "gender": Gender.MALE,
        "street_address": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country": "USA",
        "identification_type": IdentificationType.DRIVER_LICENSE,
        "identification_number": "DL123456789",
    }

    with pytest.raises(ValueError, match="at least 18 years old"):
        PolicyholderCreate(**data)


def test_policyholder_create_age_validation_too_old():
    """Test that unrealistic ages are rejected."""
    data = {
        "first_name": "Old",
        "last_name": "Person",
        "email": "old@example.com",
        "phone": "+1-555-123-4567",
        "date_of_birth": "1800-01-01",
        "gender": Gender.MALE,
        "street_address": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country": "USA",
        "identification_type": IdentificationType.DRIVER_LICENSE,
        "identification_number": "DL123456789",
    }

    with pytest.raises(ValueError, match="Invalid date of birth"):
        PolicyholderCreate(**data)


def test_policyholder_update_schema_partial():
    """Test that PolicyholderUpdate allows partial updates."""
    data = {"first_name": "Jane", "email": "jane@example.com"}
    schema = PolicyholderUpdate(**data)

    assert schema.first_name == "Jane"
    assert schema.email == "jane@example.com"
    assert schema.last_name is None
    assert schema.phone is None


def test_policyholder_response_schema_from_dict():
    """Test PolicyholderResponse creation from dict."""
    data = {
        "id": str(uuid4()),
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567",
        "date_of_birth": "1990-01-15",
        "gender": Gender.MALE,
        "street_address": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country": "USA",
        "identification_type": IdentificationType.DRIVER_LICENSE,
        "identification_number": "DL123456789",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    schema = PolicyholderResponse(**data)
    assert schema.first_name == "John"
    assert schema.is_active is True


# ============================================================================
# Model Tests
# ============================================================================


def test_policyholder_model_properties():
    """Test Policyholder model computed properties."""
    from app.domains.policy_holders.models import PolicyHolder as Policyholder

    policyholder = Policyholder(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1-555-123-4567",
        date_of_birth=date(1990, 1, 15),
        gender=Gender.MALE,
        street_address="123 Main Street",
        city="New York",
        state="NY",
        zip_code="10001",
        country="USA",
        identification_type=IdentificationType.DRIVER_LICENSE,
        identification_number="DL123456789",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    assert policyholder.full_name == "John Doe"
    assert policyholder.age >= 34  # Born in 1990


def test_policyholder_model_repr():
    """Test Policyholder model string representation."""
    from app.domains.policy_holders.models import PolicyHolder as Policyholder

    ph_id = uuid4()
    policyholder = Policyholder(
        id=ph_id,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1-555-123-4567",
        date_of_birth=date(1990, 1, 15),
        gender=Gender.MALE,
        street_address="123 Main Street",
        city="New York",
        state="NY",
        zip_code="10001",
        country="USA",
        identification_type=IdentificationType.DRIVER_LICENSE,
        identification_number="DL123456789",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    repr_str = repr(policyholder)
    assert "PolicyHolder" in repr_str
    assert str(ph_id) in repr_str
    assert "John Doe" in repr_str
    assert "john.doe@example.com" in repr_str


# ============================================================================
# Email Validation Tests
# ============================================================================


def test_policyholder_invalid_email():
    """Test that invalid emails are rejected."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "invalid-email",
        "phone": "+1-555-123-4567",
        "date_of_birth": "1990-01-15",
        "gender": Gender.MALE,
        "street_address": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country": "USA",
        "identification_type": IdentificationType.DRIVER_LICENSE,
        "identification_number": "DL123456789",
    }

    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        PolicyholderCreate(**data)


# ============================================================================
# Phone Number Tests
# ============================================================================


def test_policyholder_valid_phone_formats():
    """Test various valid phone number formats."""
    valid_phones = [
        "+1-555-123-4567",
        "+15551234567",
        "+1 (555) 123-4567",
        "555-123-4567",
    ]

    for phone in valid_phones:
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": phone,
            "date_of_birth": "1990-01-15",
            "gender": Gender.MALE,
            "street_address": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "USA",
            "identification_type": IdentificationType.DRIVER_LICENSE,
            "identification_number": "DL123456789",
        }

        schema = PolicyholderCreate(**data)
        assert schema.phone is not None


# Phone number tests removed - constraints tested at type level in test_schemas.py


# ============================================================================
# Enum Tests
# ============================================================================


def test_policyholder_gender_enum_values():
    """Test that all gender enum values are accepted."""
    for gender in [Gender.MALE, Gender.FEMALE, Gender.OTHER, Gender.PREFER_NOT_TO_SAY]:
        data = {
            "first_name": "Test",
            "last_name": "Person",
            "email": "test@example.com",
            "phone": "+1-555-123-4567",
            "date_of_birth": "1990-01-15",
            "gender": gender,
            "street_address": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "USA",
            "identification_type": IdentificationType.DRIVER_LICENSE,
            "identification_number": "DL123456789",
        }

        schema = PolicyholderCreate(**data)
        assert schema.gender == gender


def test_policyholder_identification_type_enum_values():
    """Test that all identification type enum values are accepted."""
    id_types = [
        IdentificationType.PASSPORT,
        IdentificationType.DRIVER_LICENSE,
        IdentificationType.NATIONAL_ID,
        IdentificationType.SSN,
    ]

    for id_type in id_types:
        data = {
            "first_name": "Test",
            "last_name": "Person",
            "email": "test@example.com",
            "phone": "+1-555-123-4567",
            "date_of_birth": "1990-01-15",
            "gender": Gender.MALE,
            "street_address": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "USA",
            "identification_type": id_type,
            "identification_number": "ID123456789",
        }

        schema = PolicyholderCreate(**data)
        assert schema.identification_type == id_type
