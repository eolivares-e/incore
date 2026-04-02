"""Tests for custom exceptions."""

from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    BusinessRuleException,
    DuplicateException,
    ExternalServiceException,
    InsuranceCoreError,
    NotFoundException,
    ValidationException,
)


def test_base_exception():
    """Test base InsuranceCoreError."""
    exc = InsuranceCoreError(
        message="Test error",
        status_code=500,
        details={"key": "value"},
    )

    assert exc.message == "Test error"
    assert exc.status_code == 500
    assert exc.details == {"key": "value"}
    assert str(exc) == "Test error"


def test_not_found_exception():
    """Test NotFoundException."""
    exc = NotFoundException(message="User not found", details={"user_id": "123"})

    assert exc.message == "User not found"
    assert exc.status_code == 404
    assert exc.details == {"user_id": "123"}


def test_validation_exception():
    """Test ValidationException."""
    exc = ValidationException(message="Invalid email", details={"field": "email"})

    assert exc.message == "Invalid email"
    assert exc.status_code == 400
    assert exc.details == {"field": "email"}


def test_authentication_exception():
    """Test AuthenticationException."""
    exc = AuthenticationException(message="Invalid credentials")

    assert exc.message == "Invalid credentials"
    assert exc.status_code == 401


def test_authorization_exception():
    """Test AuthorizationException."""
    exc = AuthorizationException(message="Access denied")

    assert exc.message == "Access denied"
    assert exc.status_code == 403


def test_duplicate_exception():
    """Test DuplicateException."""
    exc = DuplicateException(message="Email already exists")

    assert exc.message == "Email already exists"
    assert exc.status_code == 409


def test_business_rule_exception():
    """Test BusinessRuleException."""
    exc = BusinessRuleException(message="Policy cannot be renewed")

    assert exc.message == "Policy cannot be renewed"
    assert exc.status_code == 422


def test_external_service_exception():
    """Test ExternalServiceException."""
    exc = ExternalServiceException(message="Stripe API error")

    assert exc.message == "Stripe API error"
    assert exc.status_code == 502


def test_exception_with_default_message():
    """Test exceptions with default messages."""
    exc = NotFoundException()
    assert exc.message == "Resource not found"
    assert exc.status_code == 404
    assert exc.details == {}
