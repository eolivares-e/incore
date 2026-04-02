"""Policies domain.

This domain handles insurance policies and their coverages.
"""

from app.domains.policies.models import Coverage, Policy
from app.domains.policies.repository import PolicyRepository
from app.domains.policies.router import router
from app.domains.policies.schemas import (
    CoverageCreate,
    CoverageResponse,
    CoverageUpdate,
    PolicyCreate,
    PolicyFilterParams,
    PolicyResponse,
    PolicyUpdate,
)
from app.domains.policies.service import PolicyService

__all__ = [
    # Models
    "Policy",
    "Coverage",
    # Schemas
    "PolicyCreate",
    "PolicyUpdate",
    "PolicyResponse",
    "PolicyFilterParams",
    "CoverageCreate",
    "CoverageUpdate",
    "CoverageResponse",
    # Service
    "PolicyService",
    # Repository
    "PolicyRepository",
    # Router
    "router",
]
