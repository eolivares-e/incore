"""Custom exceptions for the Insurance Core application."""

from typing import Any


class InsuranceCoreException(Exception):
    """Base exception for all Insurance Core errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(InsuranceCoreException):
    """Exception raised when a requested resource is not found."""

    def __init__(
        self, message: str = "Resource not found", details: dict[str, Any] | None = None
    ):
        super().__init__(message=message, status_code=404, details=details)


class ValidationException(InsuranceCoreException):
    """Exception raised when validation fails."""

    def __init__(
        self, message: str = "Validation error", details: dict[str, Any] | None = None
    ):
        super().__init__(message=message, status_code=400, details=details)


class AuthenticationException(InsuranceCoreException):
    """Exception raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message=message, status_code=401, details=details)


class AuthorizationException(InsuranceCoreException):
    """Exception raised when authorization fails."""

    def __init__(
        self,
        message: str = "You don't have permission to access this resource",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message=message, status_code=403, details=details)


class DuplicateException(InsuranceCoreException):
    """Exception raised when trying to create a duplicate resource."""

    def __init__(
        self,
        message: str = "Resource already exists",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message=message, status_code=409, details=details)


class BusinessRuleException(InsuranceCoreException):
    """Exception raised when a business rule is violated."""

    def __init__(
        self,
        message: str = "Business rule violation",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message=message, status_code=422, details=details)


class ExternalServiceException(InsuranceCoreException):
    """Exception raised when an external service call fails."""

    def __init__(
        self,
        message: str = "External service error",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message=message, status_code=502, details=details)
