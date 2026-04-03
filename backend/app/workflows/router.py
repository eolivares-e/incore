"""API router for cross-domain workflows."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domains.users.models import User, UserRole
from app.domains.users.router import require_role
from app.workflows.quote_to_policy import QuoteToPolicyWorkflow
from app.workflows.schemas import (
    QuoteToPolicyRequest,
    QuoteToPolicyResponse,
)

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post(
    "/quote-to-policy",
    response_model=QuoteToPolicyResponse,
    status_code=status.HTTP_200_OK,
    summary="Convert quote to policy (Quote-to-Policy workflow)",
    description="""Execute the complete Quote-to-Policy workflow.

**Workflow Steps:**
1. Validate quote (must be ACCEPTED)
2. Create underwriting review (if not skipped)
3. Create policy with coverages (if approved)
4. Generate invoice for first payment
5. Update quote status to CONVERTED_TO_POLICY

**Authentication:** Required (AGENT role)

**Access Control:**
- Only AGENT and ADMIN users can execute workflows
- CUSTOMER users must work with agents

**Business Rules:**
- Quote must be in ACCEPTED status
- Low-risk quotes may skip underwriting (with admin override)
- High-risk quotes always require underwriting approval
- Policy is only created if underwriting approves
- Invoice is automatically generated with 30-day due date
""",
)
async def execute_quote_to_policy_workflow(
    request: QuoteToPolicyRequest,
    current_user: User = Depends(require_role([UserRole.AGENT, UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
) -> QuoteToPolicyResponse:
    """Execute the quote-to-policy workflow.

    This endpoint orchestrates multiple domains to convert an accepted
    quote into an active policy with automatic underwriting and invoicing.

    Args:
        request: Workflow request with quote_id
        current_user: Authenticated user (AGENT or ADMIN)
        db: Database session

    Returns:
        Workflow response with created policy and invoice details

    Raises:
        ValidationException: If quote is invalid or workflow fails
        AuthorizationException: If user lacks permission
    """
    workflow = QuoteToPolicyWorkflow(db)
    return await workflow.execute(request)
