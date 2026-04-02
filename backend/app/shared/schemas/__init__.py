"""Shared schemas package."""

from app.shared.schemas.base import (
    BaseSchema,
    ErrorDetail,
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
    TimestampMixin,
    UUIDMixin,
)

__all__ = [
    "BaseSchema",
    "TimestampMixin",
    "UUIDMixin",
    "PaginationParams",
    "PaginatedResponse",
    "ErrorDetail",
    "ErrorResponse",
    "MessageResponse",
]
