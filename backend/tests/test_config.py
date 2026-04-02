"""Tests for core configuration."""

from app.core.config import settings


def test_settings_loaded():
    """Test that settings are loaded correctly."""
    assert settings.PROJECT_NAME == "Insurance Core API"
    assert settings.VERSION == "0.1.0"
    assert settings.API_V1_STR == "/api/v1"


def test_database_settings():
    """Test database configuration settings."""
    assert settings.DATABASE_URL is not None
    assert "postgresql+asyncpg" in settings.DATABASE_URL
    assert settings.DATABASE_POOL_SIZE > 0
    assert settings.DATABASE_MAX_OVERFLOW > 0


def test_jwt_settings():
    """Test JWT configuration settings."""
    assert settings.JWT_SECRET_KEY is not None
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS > 0


def test_security_settings():
    """Test security configuration settings."""
    assert settings.PASSWORD_MIN_LENGTH >= 8
    assert settings.BCRYPT_ROUNDS >= 10


def test_cors_settings():
    """Test CORS configuration settings."""
    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert len(settings.ALLOWED_ORIGINS) > 0
