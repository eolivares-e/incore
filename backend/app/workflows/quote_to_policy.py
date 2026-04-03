"""Quote-to-Policy workflow orchestration.

This workflow demonstrates cross-domain integration by orchestrating:
1. Quote validation and acceptance
2. Underwriting review (if required)
3. Policy creation
4. Invoice generation

This is a key business process that ties together multiple domains.
"""

import time
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.core.logging import get_logger
from app.domains.billing.repository import InvoiceRepository
from app.domains.billing.schemas import InvoiceCreate
from app.domains.policies.repository import PolicyRepository
from app.domains.policies.schemas import CoverageCreate, PolicyCreate
from app.domains.pricing.repository import QuoteRepository
from app.domains.underwriting.repository import UnderwritingRepository
from app.domains.underwriting.schemas import UnderwritingReviewCreate
from app.shared.enums import (
    CoverageType,
    QuoteStatus,
    UnderwritingStatus,
)
from app.workflows.schemas import QuoteToPolicyRequest, QuoteToPolicyResponse

logger = get_logger(__name__)


class QuoteToPolicyWorkflow:
    """Orchestrates the conversion of an accepted quote to a policy.

    This workflow handles:
    - Quote validation
    - Risk assessment and underwriting
    - Policy creation with coverages
    - Invoice generation for first payment
    """

    def __init__(self, session: AsyncSession):
        """Initialize workflow with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self.quote_repo = QuoteRepository(session)
        self.underwriting_repo = UnderwritingRepository(session)
        self.policy_repo = PolicyRepository(session)
        self.invoice_repo = InvoiceRepository(session)

    async def execute(self, request: QuoteToPolicyRequest) -> QuoteToPolicyResponse:
        """Execute the quote-to-policy workflow.

        Args:
            request: Workflow request with quote ID

        Returns:
            Workflow response with created resources

        Raises:
            ValidationException: If quote is invalid or workflow fails
        """
        start_time = time.time()
        workflow_started_at = datetime.utcnow()

        logger.info(
            "workflow_started",
            workflow_type="quote_to_policy",
            quote_id=str(request.quote_id),
        )

        # Step 1: Validate quote
        quote = await self._validate_quote(request.quote_id)

        # Step 2: Create or skip underwriting review
        underwriting_review = None
        if not request.skip_underwriting:
            underwriting_review = await self._create_underwriting_review(quote)

            # Check if underwriting was rejected
            if underwriting_review.status == UnderwritingStatus.REJECTED:
                workflow_completed_at = datetime.utcnow()
                duration = time.time() - start_time

                logger.warning(
                    "workflow_rejected_by_underwriting",
                    quote_id=str(quote.id),
                    risk_score=str(underwriting_review.risk_score),
                )

                return QuoteToPolicyResponse(
                    success=False,
                    message="Quote rejected by underwriting review",
                    quote_id=quote.id,
                    quote_number=quote.quote_number,
                    quote_status=quote.status,
                    underwriting_review_id=underwriting_review.id,
                    underwriting_decision=underwriting_review.status,
                    risk_score=underwriting_review.risk_score,
                    workflow_started_at=workflow_started_at,
                    workflow_completed_at=workflow_completed_at,
                    total_duration_seconds=duration,
                )

        # Step 3: Create policy
        policy = await self._create_policy_from_quote(quote)

        # Step 4: Update quote status to CONVERTED_TO_POLICY
        quote.status = QuoteStatus.CONVERTED_TO_POLICY
        quote.converted_to_policy_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(quote)

        # Step 5: Generate invoice for first payment
        invoice = await self._generate_invoice(policy)

        workflow_completed_at = datetime.utcnow()
        duration = time.time() - start_time

        logger.info(
            "workflow_completed",
            workflow_type="quote_to_policy",
            quote_id=str(quote.id),
            policy_id=str(policy.id),
            invoice_id=str(invoice.id),
            duration_seconds=round(duration, 2),
        )

        return QuoteToPolicyResponse(
            success=True,
            message="Quote successfully converted to policy",
            quote_id=quote.id,
            quote_number=quote.quote_number,
            quote_status=quote.status,
            underwriting_review_id=(
                underwriting_review.id if underwriting_review else None
            ),
            underwriting_decision=(
                underwriting_review.status if underwriting_review else None
            ),
            risk_score=(
                underwriting_review.risk_score if underwriting_review else None
            ),
            policy_id=policy.id,
            policy_number=policy.policy_number,
            policy_status=policy.status,
            invoice_id=invoice.id,
            invoice_number=invoice.invoice_number,
            invoice_status=invoice.status,
            invoice_amount=invoice.total_amount,
            workflow_started_at=workflow_started_at,
            workflow_completed_at=workflow_completed_at,
            total_duration_seconds=duration,
        )

    async def _validate_quote(self, quote_id: UUID):
        """Validate quote is ready for conversion.

        Args:
            quote_id: Quote ID

        Returns:
            Quote instance

        Raises:
            ValidationException: If quote is not found or not accepted
        """
        quote = await self.quote_repo.get_by_id(quote_id)
        if not quote:
            raise ValidationException(f"Quote not found: {quote_id}", details={})

        if quote.status != QuoteStatus.ACCEPTED:
            raise ValidationException(
                f"Quote must be ACCEPTED to convert to policy. "
                f"Current status: {quote.status.value}",
                details={"quote_id": str(quote.id), "status": quote.status.value},
            )

        if not quote.is_active:
            raise ValidationException(
                "Quote is inactive and cannot be converted",
                details={"quote_id": str(quote.id)},
            )

        logger.debug(
            "quote_validated",
            quote_id=str(quote.id),
            quote_number=quote.quote_number,
        )

        return quote

    async def _create_underwriting_review(self, quote):
        """Create underwriting review for the quote.

        Args:
            quote: Quote instance

        Returns:
            UnderwritingReview instance
        """
        review_data = UnderwritingReviewCreate(
            quote_id=quote.id,
            policy_id=None,  # Policy not created yet
            # reviewer_id will be set by service if needed
        )

        # Use underwriting service to create review with risk scoring
        from app.domains.underwriting.service import UnderwritingService

        underwriting_service = UnderwritingService(self.session)
        review = await underwriting_service.create_review(review_data)

        logger.info(
            "underwriting_review_created",
            review_id=str(review.id),
            quote_id=str(quote.id),
            status=review.status.value,
            risk_score=str(review.risk_score),
        )

        return review

    async def _create_policy_from_quote(self, quote):
        """Create a policy from an accepted quote.

        Args:
            quote: Quote instance

        Returns:
            Policy instance
        """
        # Calculate policy dates
        start_date = datetime.utcnow().date()
        end_date = start_date + timedelta(days=365)  # 1 year policy

        # Determine default coverages based on policy type
        coverages = self._get_default_coverages(quote)

        # Create policy
        policy_data = PolicyCreate(
            policy_holder_id=quote.policy_holder_id,
            policy_type=quote.policy_type,
            premium=quote.final_premium,
            start_date=start_date,
            end_date=end_date,
            coverages=coverages,
        )

        policy = await self.policy_repo.create(policy_data)

        logger.info(
            "policy_created_from_quote",
            policy_id=str(policy.id),
            policy_number=policy.policy_number,
            quote_id=str(quote.id),
            premium=str(quote.final_premium),
        )

        return policy

    def _get_default_coverages(self, quote) -> list[CoverageCreate]:
        """Generate default coverages based on policy type.

        Args:
            quote: Quote instance

        Returns:
            List of coverage create schemas
        """
        from app.shared.enums import PolicyType

        coverages = []

        # Basic liability coverage for all types
        coverages.append(
            CoverageCreate(
                coverage_type=CoverageType.LIABILITY,
                coverage_amount=Decimal("100000.00"),
                deductible=Decimal("500.00"),
            )
        )

        # Type-specific coverages
        if quote.policy_type == PolicyType.AUTO:
            coverages.append(
                CoverageCreate(
                    coverage_type=CoverageType.COLLISION,
                    coverage_amount=Decimal("50000.00"),
                    deductible=Decimal("1000.00"),
                )
            )
        elif quote.policy_type == PolicyType.HOME:
            coverages.append(
                CoverageCreate(
                    coverage_type=CoverageType.PROPERTY,
                    coverage_amount=Decimal("300000.00"),
                    deductible=Decimal("2000.00"),
                )
            )
        elif quote.policy_type == PolicyType.HEALTH:
            coverages.append(
                CoverageCreate(
                    coverage_type=CoverageType.MEDICAL,
                    coverage_amount=Decimal("1000000.00"),
                    deductible=Decimal("5000.00"),
                )
            )

        return coverages

    async def _generate_invoice(self, policy):
        """Generate invoice for policy's first payment.

        Args:
            policy: Policy instance

        Returns:
            Invoice instance
        """
        # Calculate due date (30 days from now)
        due_date = datetime.utcnow().date() + timedelta(days=30)

        invoice_data = InvoiceCreate(
            policy_id=policy.id,
            due_date=due_date,
            amount=policy.premium,
            description=f"First year premium for policy {policy.policy_number}",
        )

        invoice = await self.invoice_repo.create(invoice_data)

        logger.info(
            "invoice_generated",
            invoice_id=str(invoice.id),
            invoice_number=invoice.invoice_number,
            policy_id=str(policy.id),
            amount=str(invoice.total_amount),
        )

        return invoice
