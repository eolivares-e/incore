"""Tests for core security module."""

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    validate_password_strength,
    verify_password,
    verify_token,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "TestPassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_password_strength_validation():
    """Test password strength validation."""
    # Valid password
    is_valid, error = validate_password_strength("ValidPass123")
    assert is_valid is True
    assert error == ""

    # Too short
    is_valid, error = validate_password_strength("Short1")
    assert is_valid is False
    assert "at least" in error

    # No digit
    is_valid, error = validate_password_strength("NoDigitPass")
    assert is_valid is False
    assert "digit" in error

    # No uppercase
    is_valid, error = validate_password_strength("nouppercase123")
    assert is_valid is False
    assert "uppercase" in error

    # No lowercase
    is_valid, error = validate_password_strength("NOLOWERCASE123")
    assert is_valid is False
    assert "lowercase" in error


def test_create_access_token():
    """Test JWT access token creation."""
    user_id = "test-user-123"
    token = create_access_token(subject=user_id)

    assert token is not None
    assert isinstance(token, str)

    # Verify token can be decoded
    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["sub"] == user_id
    assert "exp" in payload


def test_create_refresh_token():
    """Test JWT refresh token creation."""
    user_id = "test-user-123"
    token = create_refresh_token(subject=user_id)

    assert token is not None
    assert isinstance(token, str)

    # Verify token can be decoded
    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_verify_token():
    """Test JWT token verification."""
    user_id = "test-user-123"
    token = create_access_token(subject=user_id)

    # Valid token
    verified_user_id = verify_token(token)
    assert verified_user_id == user_id

    # Invalid token
    invalid_user_id = verify_token("invalid.token.here")
    assert invalid_user_id is None


def test_verify_token_with_wrong_secret():
    """Test token verification fails with wrong secret."""
    user_id = "test-user-123"

    # Create token with different secret
    fake_token = jwt.encode(
        {"sub": user_id, "exp": 9999999999},
        "wrong-secret-key",
        algorithm=settings.JWT_ALGORITHM,
    )

    # Should fail verification
    verified_user_id = verify_token(fake_token)
    assert verified_user_id is None
