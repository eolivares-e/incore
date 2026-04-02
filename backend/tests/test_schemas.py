"""Tests for shared schemas and base types."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.shared.schemas.base import (
    BaseSchema,
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
    TimestampMixin,
    UUIDMixin,
)
from app.shared.types import (
    CoverageAmount,
    Email,
    MoneyAmount,
    PhoneNumber,
    PolicyNumber,
    PremiumAmount,
    RiskScore,
)


# Test Models
class TestBaseSchema(BaseSchema):
    """Test schema for BaseSchema."""

    name: str
    value: int


class TestTimestampSchema(TimestampMixin):
    """Test schema for TimestampMixin."""

    name: str


class TestUUIDSchema(UUIDMixin):
    """Test schema for UUIDMixin."""

    name: str


class TestFullSchema(BaseSchema, UUIDMixin, TimestampMixin):
    """Test schema combining all mixins."""

    name: str
    value: int


# BaseSchema Tests
def test_base_schema_creation():
    """Test basic schema creation."""
    data = {"name": "test", "value": 42}
    schema = TestBaseSchema(**data)
    assert schema.name == "test"
    assert schema.value == 42


def test_base_schema_model_dump():
    """Test schema serialization."""
    schema = TestBaseSchema(name="test", value=42)
    data = schema.model_dump()
    assert data == {"name": "test", "value": 42}


def test_base_schema_model_dump_json():
    """Test schema JSON serialization."""
    schema = TestBaseSchema(name="test", value=42)
    json_str = schema.model_dump_json()
    assert '"name":"test"' in json_str
    assert '"value":42' in json_str


def test_base_schema_validation_error():
    """Test schema validation errors."""
    with pytest.raises(ValidationError) as exc_info:
        TestBaseSchema(name="test", value="not an int")

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["loc"] == ("value",)


# TimestampMixin Tests
def test_timestamp_mixin_required_fields():
    """Test that timestamp fields are required."""
    with pytest.raises(ValidationError) as exc_info:
        TestTimestampSchema(name="test")

    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}
    assert "created_at" in error_fields
    assert "updated_at" in error_fields


def test_timestamp_mixin_custom_timestamps():
    """Test custom timestamp values."""
    now = datetime.now()
    schema = TestTimestampSchema(
        name="test",
        created_at=now,
        updated_at=now,
    )
    assert schema.created_at == now
    assert schema.updated_at == now


def test_timestamp_mixin_serialization():
    """Test timestamp serialization."""
    now = datetime.now()
    schema = TestTimestampSchema(name="test", created_at=now, updated_at=now)
    data = schema.model_dump()
    assert "created_at" in data
    assert "updated_at" in data
    assert isinstance(data["created_at"], datetime)
    assert isinstance(data["updated_at"], datetime)


# UUIDMixin Tests
def test_uuid_mixin_required_id():
    """Test that ID field is required."""
    with pytest.raises(ValidationError) as exc_info:
        TestUUIDSchema(name="test")

    errors = exc_info.value.errors()
    assert any(error["loc"][0] == "id" for error in errors)


def test_uuid_mixin_custom_id():
    """Test custom UUID value."""
    custom_id = uuid4()
    schema = TestUUIDSchema(id=custom_id, name="test")
    assert schema.id == custom_id


def test_uuid_mixin_string_conversion():
    """Test UUID from string."""
    uuid_str = "12345678-1234-5678-1234-567812345678"
    schema = TestUUIDSchema(id=uuid_str, name="test")
    assert isinstance(schema.id, UUID)
    assert str(schema.id) == uuid_str


def test_uuid_mixin_serialization():
    """Test UUID serialization."""
    custom_id = uuid4()
    schema = TestUUIDSchema(id=custom_id, name="test")
    data = schema.model_dump()
    assert "id" in data
    assert isinstance(data["id"], UUID)


# Combined Schema Tests
def test_full_schema_all_fields():
    """Test schema with all mixins."""
    custom_id = uuid4()
    now = datetime.now()
    schema = TestFullSchema(
        id=custom_id,
        created_at=now,
        updated_at=now,
        name="test",
        value=42,
    )
    assert schema.id == custom_id
    assert schema.created_at == now
    assert schema.updated_at == now
    assert schema.name == "test"
    assert schema.value == 42


def test_full_schema_custom_values():
    """Test full schema with custom values."""
    custom_id = uuid4()
    now = datetime.now()
    schema = TestFullSchema(
        id=custom_id,
        created_at=now,
        updated_at=now,
        name="test",
        value=42,
    )
    assert schema.id == custom_id
    assert schema.created_at == now
    assert schema.updated_at == now


# PaginationParams Tests
def test_pagination_params_defaults():
    """Test pagination with default values."""
    params = PaginationParams()
    assert params.page == 1
    assert params.page_size == 20


def test_pagination_params_custom():
    """Test pagination with custom values."""
    params = PaginationParams(page=3, page_size=50)
    assert params.page == 3
    assert params.page_size == 50


def test_pagination_params_offset_calculation():
    """Test offset calculation."""
    params = PaginationParams(page=3, page_size=10)
    assert params.offset == 20  # (3 - 1) * 10


def test_pagination_params_first_page():
    """Test offset on first page."""
    params = PaginationParams(page=1, page_size=10)
    assert params.offset == 0


def test_pagination_params_validation_min_page():
    """Test minimum page validation."""
    with pytest.raises(ValidationError) as exc_info:
        PaginationParams(page=0)

    errors = exc_info.value.errors()
    assert any("page" in str(error["loc"]) for error in errors)


def test_pagination_params_validation_max_page_size():
    """Test maximum page size validation."""
    with pytest.raises(ValidationError) as exc_info:
        PaginationParams(page_size=101)

    errors = exc_info.value.errors()
    assert any("page_size" in str(error["loc"]) for error in errors)


# PaginatedResponse Tests
def test_paginated_response_creation():
    """Test paginated response creation using factory method."""
    items = [
        TestBaseSchema(name="item1", value=1),
        TestBaseSchema(name="item2", value=2),
    ]
    response = PaginatedResponse.create(
        items=items,
        total=10,
        page=1,
        page_size=2,
    )
    assert len(response.items) == 2
    assert response.total == 10
    assert response.page == 1
    assert response.page_size == 2
    assert response.total_pages == 5


def test_paginated_response_total_pages_calculation():
    """Test total pages calculation."""
    response = PaginatedResponse.create(
        items=[],
        total=25,
        page=1,
        page_size=10,
    )
    assert response.total_pages == 3


def test_paginated_response_total_pages_exact():
    """Test total pages with exact division."""
    response = PaginatedResponse.create(
        items=[],
        total=20,
        page=1,
        page_size=10,
    )
    assert response.total_pages == 2


def test_paginated_response_empty():
    """Test empty paginated response."""
    response = PaginatedResponse.create(
        items=[],
        total=0,
        page=1,
        page_size=10,
    )
    assert response.items == []
    assert response.total == 0
    assert response.total_pages == 0


def test_paginated_response_serialization():
    """Test paginated response serialization."""
    items = [TestBaseSchema(name="item1", value=1)]
    response = PaginatedResponse.create(
        items=items,
        total=10,
        page=2,
        page_size=5,
    )
    data = response.model_dump()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["total_pages"] == 2


# ErrorResponse Tests
def test_error_response_creation():
    """Test error response creation."""
    error = ErrorResponse(
        error="NotFoundError",
    )
    assert error.error == "NotFoundError"
    assert error.details is None
    assert error.timestamp is not None


def test_error_response_with_details():
    """Test error response with details."""
    details = {"field": "email", "issue": "invalid format"}
    error = ErrorResponse(
        error="ValidationError",
        details=details,
    )
    assert error.error == "ValidationError"
    assert error.details == details


def test_error_response_serialization():
    """Test error response serialization."""
    error = ErrorResponse(
        error="TestError",
    )
    data = error.model_dump()
    assert data["error"] == "TestError"
    assert data["details"] is None
    assert "timestamp" in data


# MessageResponse Tests
def test_message_response_creation():
    """Test message response creation."""
    response = MessageResponse(message="Operation successful")
    assert response.message == "Operation successful"


def test_message_response_serialization():
    """Test message response serialization."""
    response = MessageResponse(message="Test message")
    data = response.model_dump()
    assert data["message"] == "Test message"
    assert data["data"] is None


# Type Aliases Tests
def test_money_amount_type():
    """Test MoneyAmount type (Decimal)."""
    amount: MoneyAmount = Decimal("100.50")
    assert isinstance(amount, Decimal)
    assert amount == Decimal("100.50")


def test_premium_amount_type():
    """Test PremiumAmount type (Decimal)."""
    premium: PremiumAmount = Decimal("500.00")
    assert isinstance(premium, Decimal)
    assert premium == Decimal("500.00")


def test_coverage_amount_type():
    """Test CoverageAmount type (Decimal)."""
    coverage: CoverageAmount = Decimal("100000.00")
    assert isinstance(coverage, Decimal)
    assert coverage == Decimal("100000.00")


def test_policy_number_type():
    """Test PolicyNumber type (str)."""
    policy_num: PolicyNumber = "POL-2024-001"
    assert isinstance(policy_num, str)
    assert policy_num == "POL-2024-001"


def test_email_type():
    """Test Email type (str)."""
    email: Email = "test@example.com"
    assert isinstance(email, str)
    assert email == "test@example.com"


def test_phone_number_type():
    """Test PhoneNumber type (str)."""
    phone: PhoneNumber = "+1234567890"
    assert isinstance(phone, str)
    assert phone == "+1234567890"


def test_risk_score_type():
    """Test RiskScore type (int 0-100)."""
    score: RiskScore = 75
    assert isinstance(score, int)
    assert score == 75


def test_decimal_precision():
    """Test Decimal precision for money amounts."""
    amount: MoneyAmount = Decimal("123.456")
    # Verify Decimal maintains precision
    assert str(amount) == "123.456"

    # Test arithmetic with precision
    result = amount + Decimal("0.001")
    assert str(result) == "123.457"


def test_decimal_from_string():
    """Test creating Decimal from string."""
    amount: MoneyAmount = Decimal("1234.56")
    assert amount == Decimal("1234.56")
    assert isinstance(amount, Decimal)


def test_decimal_from_float():
    """Test creating Decimal from float (be aware of precision issues)."""
    amount: MoneyAmount = Decimal(str(123.45))
    assert amount == Decimal("123.45")


def test_type_annotations_usage():
    """Test using type aliases in a schema."""

    class PriceSchema(BaseSchema):
        premium: PremiumAmount
        coverage: CoverageAmount
        risk_score: RiskScore

    schema = PriceSchema(
        premium=Decimal("500.00"),
        coverage=Decimal("100000.00"),
        risk_score=75,
    )
    assert schema.premium == Decimal("500.00")
    assert schema.coverage == Decimal("100000.00")
    assert schema.risk_score == 75


def test_complex_schema_with_all_features():
    """Test complex schema using all base components."""

    class ComplexSchema(BaseSchema, UUIDMixin, TimestampMixin):
        email: Email
        policy_number: PolicyNumber
        premium: PremiumAmount
        coverage: CoverageAmount

    custom_id = uuid4()
    now = datetime.now()
    schema = ComplexSchema(
        id=custom_id,
        created_at=now,
        updated_at=now,
        email="customer@example.com",
        policy_number="POL-2024-001",
        premium=Decimal("500.00"),
        coverage=Decimal("100000.00"),
    )

    assert schema.id == custom_id
    assert schema.created_at == now
    assert schema.updated_at == now
    assert schema.email == "customer@example.com"
    assert schema.policy_number == "POL-2024-001"
    assert schema.premium == Decimal("500.00")
    assert schema.coverage == Decimal("100000.00")

    # Test serialization
    data = schema.model_dump()
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "email" in data
    assert "policy_number" in data
    assert "premium" in data
    assert "coverage" in data
