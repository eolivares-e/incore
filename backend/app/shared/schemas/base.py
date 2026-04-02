"""Base Pydantic schemas for the insurance domain.

This module provides base classes and mixins that are used across all domain schemas.
"""

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Base Configuration
# ============================================================================


class BaseSchema(BaseModel):
    """Base schema with common configuration for all Pydantic models.

    This provides sensible defaults for all schemas in the application.
    """

    model_config = ConfigDict(
        # Use enum values instead of enum instances in responses
        use_enum_values=True,
        # Validate on assignment
        validate_assignment=True,
        # Allow population by field name
        populate_by_name=True,
        # Strict mode for better type safety
        strict=False,
        # JSON schema extra
        json_schema_extra={"example": {}},
    )


# ============================================================================
# Mixins
# ============================================================================


class TimestampMixin(BaseModel):
    """Mixin for models with creation and update timestamps."""

    created_at: datetime = Field(
        description="Timestamp when the record was created",
        examples=["2024-01-15T10:30:00Z"],
    )
    updated_at: datetime = Field(
        description="Timestamp when the record was last updated",
        examples=["2024-01-15T14:45:00Z"],
    )


class UUIDMixin(BaseModel):
    """Mixin for models with UUID primary key."""

    id: UUID = Field(
        description="Unique identifier (UUID)",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


# ============================================================================
# Pagination
# ============================================================================


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)",
        examples=[1, 2, 3],
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (max 100)",
        examples=[10, 20, 50],
    )
    order_by: str | None = Field(
        default=None,
        description="Field to order by (prefix with - for descending)",
        examples=["created_at", "-updated_at", "name"],
    )

    @property
    def offset(self) -> int:
        """Calculate the offset for database queries."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get the limit for database queries."""
        return self.page_size


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Usage:
        PaginatedResponse[PolicyResponse](
            items=[policy1, policy2],
            total=100,
            page=1,
            page_size=20,
        )
    """

    items: list[T] = Field(
        description="List of items in the current page",
    )
    total: int = Field(
        ge=0,
        description="Total number of items across all pages",
        examples=[100, 0, 42],
    )
    page: int = Field(
        ge=1,
        description="Current page number",
        examples=[1, 2, 3],
    )
    page_size: int = Field(
        ge=1,
        description="Number of items per page",
        examples=[10, 20, 50],
    )
    total_pages: int = Field(
        ge=0,
        description="Total number of pages",
        examples=[5, 1, 0],
    )

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """Factory method to create a paginated response.

        Args:
            items: List of items for the current page
            total: Total number of items
            page: Current page number
            page_size: Items per page

        Returns:
            PaginatedResponse instance with calculated total_pages
        """
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


# ============================================================================
# Error Responses
# ============================================================================


class ErrorDetail(BaseModel):
    """Detailed error information."""

    field: str | None = Field(
        default=None,
        description="Field name that caused the error (if applicable)",
        examples=["email", "premium_amount"],
    )
    message: str = Field(
        description="Error message",
        examples=["Invalid email format", "Value must be greater than 0"],
    )
    code: str | None = Field(
        default=None,
        description="Error code for programmatic handling",
        examples=["INVALID_FORMAT", "VALUE_TOO_LOW"],
    )


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str = Field(
        description="Main error message",
        examples=["Validation error", "Resource not found"],
    )
    details: list[ErrorDetail] | dict | None = Field(
        default=None,
        description="Additional error details",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the error occurred",
    )


# ============================================================================
# Success Responses
# ============================================================================


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str = Field(
        description="Response message",
        examples=["Operation completed successfully", "Policy created"],
    )
    data: dict | None = Field(
        default=None,
        description="Optional additional data",
    )
