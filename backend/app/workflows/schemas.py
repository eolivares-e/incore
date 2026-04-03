"""Schemas for cross-domain workflows."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.enums import (
    InvoiceStatus,
    PolicyStatus,
    QuoteStatus,
    UnderwritingStatus,
)


class QuoteToPolicyRequest(BaseModel):
    """Request to convert a quote to a policy through the full workflow.

    This workflow orchestrates:
    1. Quote validation (must be ACCEPTED)
    2. Underwriting review creation (if needed)
    3. Policy creation (if underwriting approved or auto-approved)
    4. Invoice generation
    """

    quote_id: UUID = Field(description="Quote ID to convert to policy")
    skip_underwriting: bool = Field(
        default=False,
        description="Skip underwriting for low-risk quotes (admin override)",
    )


class QuoteToPolicyResponse(BaseModel):
    """Response from quote-to-policy workflow."""

    success: bool = Field(description="Whether the workflow completed successfully")
    message: str = Field(description="Human-readable status message")

    # Quote info
    quote_id: UUID
    quote_number: str
    quote_status: QuoteStatus

    # Underwriting info (optional)
    underwriting_review_id: Optional[UUID] = None
    underwriting_decision: Optional[UnderwritingStatus] = None
    risk_score: Optional[Decimal] = None

    # Policy info (created if approved)
    policy_id: Optional[UUID] = None
    policy_number: Optional[str] = None
    policy_status: Optional[PolicyStatus] = None

    # Invoice info (created with policy)
    invoice_id: Optional[UUID] = None
    invoice_number: Optional[str] = None
    invoice_status: Optional[InvoiceStatus] = None
    invoice_amount: Optional[Decimal] = None

    # Workflow metadata
    workflow_started_at: datetime
    workflow_completed_at: datetime
    total_duration_seconds: float = Field(description="Total workflow execution time")

    class Config:
        from_attributes = True


class WorkflowStatusResponse(BaseModel):
    """Status of a workflow execution."""

    workflow_type: str
    status: str  # "pending", "in_progress", "completed", "failed"
    message: str
    created_at: datetime
    updated_at: datetime
    metadata: dict = Field(default_factory=dict)

    class Config:
        from_attributes = True
