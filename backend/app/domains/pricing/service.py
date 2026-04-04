"""Service layer for Pricing business logic.

This module contains the business logic for the Pricing domain,
including risk assessment, premium calculation, quote generation,
and quote-to-policy conversion.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.domains.policies.repository import PolicyRepository
from app.domains.policies.schemas import CoverageCreate, PolicyCreate
from app.domains.policy_holders.repository import PolicyHolderRepository
from app.domains.pricing.repository import PricingRuleRepository, QuoteRepository
from app.domains.pricing.schemas import (
    QuoteAcceptRequest,
    QuoteCreate,
    QuoteFilterParams,
    QuoteResponse,
    QuoteUpdate,
)
from app.shared.enums import PolicyType, QuoteStatus, RiskLevel
from app.shared.schemas.base import PaginatedResponse, PaginationParams


class PricingEngine:
    """Pricing engine for risk assessment and premium calculation.

    This class implements the core pricing logic for insurance quotes,
    including risk level calculation and premium determination.
    """

    def calculate_risk_level(
        self,
        policy_holder_age: int,
        coverage_amount: Decimal,
        policy_type: PolicyType,
    ) -> tuple[RiskLevel, dict[str, Any]]:
        """Calculate risk level based on policyholder attributes and coverage.

        Risk scoring system (0-100 scale):
        - Age factors:
          * Young drivers (<25): +20 points
          * Senior drivers (>70): +20 points
        - Coverage factors:
          * High coverage (>$1M): +15 points
          * Very high coverage (>$5M): +30 points
        - Policy type adjustments:
          * AUTO: +10 base points
          * LIFE: +5 base points

        Risk levels:
        - LOW: 0-30 points
        - MEDIUM: 31-50 points
        - HIGH: 51-70 points
        - VERY_HIGH: 71-100 points

        Args:
            policy_holder_age: Age of the policy holder
            coverage_amount: Requested coverage amount
            policy_type: Type of insurance policy

        Returns:
            Tuple of (RiskLevel, risk_factors_dict)
        """
        risk_score = 0
        risk_factors = {
            "age": policy_holder_age,
            "coverage_amount": float(coverage_amount),
            "policy_type": policy_type if isinstance(policy_type, str) else policy_type.value,
        }

        # Age-based risk
        if policy_holder_age < 25:
            risk_score += 20
            risk_factors["age_risk_score"] = 20
            risk_factors["age_risk_reason"] = "young_driver"
        elif policy_holder_age > 70:
            risk_score += 20
            risk_factors["age_risk_score"] = 20
            risk_factors["age_risk_reason"] = "senior_driver"
        else:
            risk_factors["age_risk_score"] = 0
            risk_factors["age_risk_reason"] = "standard"

        # Coverage amount-based risk
        if coverage_amount > Decimal("5000000.00"):
            risk_score += 30
            risk_factors["coverage_risk_score"] = 30
            risk_factors["coverage_risk_reason"] = "very_high_coverage"
        elif coverage_amount > Decimal("1000000.00"):
            risk_score += 15
            risk_factors["coverage_risk_score"] = 15
            risk_factors["coverage_risk_reason"] = "high_coverage"
        else:
            risk_factors["coverage_risk_score"] = 0
            risk_factors["coverage_risk_reason"] = "standard"

        # Policy type adjustments
        policy_type_adjustments = {
            PolicyType.AUTO: 10,
            PolicyType.LIFE: 5,
            PolicyType.HOME: 0,
            PolicyType.HEALTH: 0,
        }
        type_adjustment = policy_type_adjustments.get(policy_type, 0)
        risk_score += type_adjustment
        risk_factors["policy_type_adjustment"] = type_adjustment

        # Total risk score
        risk_factors["total_risk_score"] = risk_score

        # Determine risk level
        if risk_score <= 30:
            risk_level = RiskLevel.LOW
        elif risk_score <= 50:
            risk_level = RiskLevel.MEDIUM
        elif risk_score <= 70:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH

        return risk_level, risk_factors

    def calculate_premium(
        self,
        base_premium: Decimal,
        coverage_amount: Decimal,
        risk_factors: dict[str, Any],
        multiplier_factors: dict[str, Any],
    ) -> Decimal:
        """Calculate annual premium based on base premium and risk factors.

        Formula:
        premium = base_premium + (coverage_amount / 100000 * coverage_multiplier)

        Additional multipliers applied based on risk factors:
        - Young driver multiplier (age < 25)
        - Senior driver multiplier (age > 70)

        Args:
            base_premium: Base annual premium from pricing rule
            coverage_amount: Requested coverage amount
            risk_factors: Risk factors from calculate_risk_level()
            multiplier_factors: Multiplier factors from pricing rule

        Returns:
            Calculated annual premium amount
        """
        premium = base_premium

        # Coverage amount multiplier
        coverage_per_100k = multiplier_factors.get("coverage_per_100k", 0.05)
        coverage_units = coverage_amount / Decimal("100000.00")
        premium += coverage_units * Decimal(str(coverage_per_100k)) * base_premium

        # Age-based multipliers
        age_risk_reason = risk_factors.get("age_risk_reason")
        if age_risk_reason == "young_driver":
            young_multiplier = Decimal(
                str(multiplier_factors.get("young_driver_multiplier", 1.2))
            )
            premium *= young_multiplier
        elif age_risk_reason == "senior_driver":
            senior_multiplier = Decimal(
                str(multiplier_factors.get("senior_driver_multiplier", 1.15))
            )
            premium *= senior_multiplier

        # Round to 2 decimal places
        return premium.quantize(Decimal("0.01"))


class QuoteService:
    """Service for Quote business logic.

    Handles quote generation, acceptance/rejection, and orchestrates
    pricing engine and repository operations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize service with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.repository = QuoteRepository(session)
        self.pricing_rule_repository = PricingRuleRepository(session)
        self.policy_holder_repository = PolicyHolderRepository(session)
        self.policy_repository = PolicyRepository(session)
        self.pricing_engine = PricingEngine()
        self.session = session

    def _generate_quote_number(
        self, year: int, policy_type: PolicyType, sequence: int
    ) -> str:
        """Generate a quote number in format: QTE-YYYY-TYPE-NNNNN.

        Args:
            year: Year (e.g., 2026)
            policy_type: Policy type enum
            sequence: Sequence number (will be zero-padded to 5 digits)

        Returns:
            Generated quote number

        Examples:
            QTE-2026-AUTO-00001
            QTE-2026-HEALTH-00042
            QTE-2026-LIFE-99999
        """
        pt = policy_type if isinstance(policy_type, str) else policy_type.value
        return f"QTE-{year}-{pt.upper()}-{sequence:05d}"

    async def _get_next_quote_number(self, policy_type: PolicyType) -> str:
        """Get the next available quote number for a given type.

        Args:
            policy_type: Policy type

        Returns:
            Next available quote number
        """
        current_year = datetime.now().year
        latest_sequence = await self.repository.get_latest_quote_number_sequence(
            year=current_year,
            policy_type=policy_type,
        )
        next_sequence = latest_sequence + 1
        return self._generate_quote_number(current_year, policy_type, next_sequence)

    async def create_quote(self, data: QuoteCreate) -> QuoteResponse:
        """Create a new insurance quote with automated risk assessment and pricing.

        Business rules:
        - Policy holder must exist
        - Pricing rule must exist for policy type and calculated risk level
        - Quote is valid for 30 days from creation
        - Quote starts in ACTIVE status
        - Premium and risk level are calculated automatically

        Args:
            data: Quote creation data

        Returns:
            Created quote with calculated premium and risk assessment

        Raises:
            NotFoundException: If policy holder or pricing rule not found
            ValidationException: If business rules are violated
        """
        # Verify policy holder exists
        policy_holder = await self.policy_holder_repository.get_by_id(
            data.policy_holder_id
        )
        if not policy_holder:
            raise NotFoundException(
                resource="PolicyHolder",
                resource_id=str(data.policy_holder_id),
            )

        # Calculate risk level
        risk_level, risk_factors = self.pricing_engine.calculate_risk_level(
            policy_holder_age=policy_holder.age,
            coverage_amount=data.requested_coverage_amount,
            policy_type=data.policy_type,
        )

        # Get pricing rule for this policy type and risk level
        pricing_rule = await self.pricing_rule_repository.get_active_rule(
            policy_type=data.policy_type,
            risk_level=risk_level,
        )
        if not pricing_rule:
            raise NotFoundException(
                resource="PricingRule",
                resource_id=f"{data.policy_type}/{risk_level}",
                message=f"No active pricing rule found for {data.policy_type} policy with {risk_level} risk level",
            )

        # Calculate premium
        calculated_premium = self.pricing_engine.calculate_premium(
            base_premium=pricing_rule.base_premium,
            coverage_amount=data.requested_coverage_amount,
            risk_factors=risk_factors,
            multiplier_factors=pricing_rule.multiplier_factors,
        )

        # Add pricing rule info to risk factors
        risk_factors["pricing_rule_id"] = str(pricing_rule.id)
        risk_factors["base_premium"] = float(pricing_rule.base_premium)
        risk_factors["calculated_premium"] = float(calculated_premium)

        # Generate quote number
        quote_number = await self._get_next_quote_number(data.policy_type)

        # Calculate valid_until (30 days from now)
        valid_until = date.today() + timedelta(days=30)

        # Create quote
        quote = await self.repository.create(
            data=data,
            quote_number=quote_number,
            calculated_premium=float(calculated_premium),
            risk_level=risk_level,
            risk_factors=risk_factors,
            valid_until=valid_until,
        )

        # Set status to ACTIVE
        quote.status = QuoteStatus.ACTIVE
        await self.session.commit()
        await self.session.refresh(quote)

        return QuoteResponse.model_validate(quote)

    async def get_quote(self, quote_id: UUID) -> QuoteResponse:
        """Get a quote by ID.

        Args:
            quote_id: UUID of the quote

        Returns:
            Quote data

        Raises:
            NotFoundException: If quote not found
        """
        quote = await self.repository.get_by_id(quote_id)
        if not quote:
            raise NotFoundException(
                resource="Quote",
                resource_id=str(quote_id),
            )

        return QuoteResponse.model_validate(quote)

    async def get_quote_by_number(self, quote_number: str) -> QuoteResponse:
        """Get a quote by quote number.

        Args:
            quote_number: Quote number

        Returns:
            Quote data

        Raises:
            NotFoundException: If quote not found
        """
        quote = await self.repository.get_by_quote_number(quote_number)
        if not quote:
            raise NotFoundException(
                resource="Quote",
                resource_id=quote_number,
            )

        return QuoteResponse.model_validate(quote)

    async def get_quotes(
        self,
        pagination: PaginationParams,
        filters: QuoteFilterParams,
    ) -> PaginatedResponse[QuoteResponse]:
        """Get a paginated list of quotes with optional filters.

        Args:
            pagination: Pagination parameters
            filters: Filter parameters

        Returns:
            Paginated list of quotes
        """
        # Get total count for pagination
        total = await self.repository.count(
            policy_holder_id=filters.policy_holder_id,
            policy_type=filters.policy_type,
            status=filters.status,
            risk_level=filters.risk_level,
            is_active=filters.is_active,
            search=filters.search,
        )

        # Get quotes
        quotes = await self.repository.get_all(
            skip=pagination.offset,
            limit=pagination.limit,
            policy_holder_id=filters.policy_holder_id,
            policy_type=filters.policy_type,
            status=filters.status,
            risk_level=filters.risk_level,
            is_active=filters.is_active,
            search=filters.search,
        )

        # Convert to response schemas
        items = [QuoteResponse.model_validate(q) for q in quotes]

        return PaginatedResponse.create(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def update_quote(
        self,
        quote_id: UUID,
        data: QuoteUpdate,
    ) -> QuoteResponse:
        """Update a quote.

        Business rules:
        - Quote must exist
        - Can only update quotes in DRAFT or ACTIVE status
        - Cannot update ACCEPTED, REJECTED, EXPIRED, or CONVERTED quotes

        Args:
            quote_id: UUID of the quote to update
            data: Update data

        Returns:
            Updated quote

        Raises:
            NotFoundException: If quote not found
            ValidationException: If business rules are violated
        """
        # Check if quote exists
        quote = await self.repository.get_by_id(quote_id)
        if not quote:
            raise NotFoundException(
                resource="Quote",
                resource_id=str(quote_id),
            )

        # Check if quote can be updated
        updatable_statuses = {QuoteStatus.DRAFT, QuoteStatus.ACTIVE}
        if quote.status not in updatable_statuses:
            raise ValidationException(
                message=f"Cannot update quote with status {quote.status.value}",
                details={"current_status": quote.status.value},
            )

        # Update quote
        updated_quote = await self.repository.update(quote_id, data)
        return QuoteResponse.model_validate(updated_quote)

    async def delete_quote(self, quote_id: UUID) -> None:
        """Soft delete a quote.

        Business rules:
        - Quote must exist
        - Sets is_active to False

        Args:
            quote_id: UUID of the quote to delete

        Raises:
            NotFoundException: If quote not found
        """
        success = await self.repository.delete(quote_id)
        if not success:
            raise NotFoundException(
                resource="Quote",
                resource_id=str(quote_id),
            )

    async def accept_quote(
        self,
        quote_id: UUID,
        data: QuoteAcceptRequest,
    ) -> dict[str, Any]:
        """Accept a quote and convert it to an active policy.

        Business rules:
        - Quote must exist and be in ACTIVE or PENDING status
        - Quote must not be expired
        - Creates a policy with status ACTIVE
        - Creates basic coverage based on quote details
        - Updates quote status to CONVERTED_TO_POLICY

        Args:
            quote_id: UUID of the quote to accept
            data: Policy details (start_date, end_date, etc.)

        Returns:
            Dict with quote and created policy information

        Raises:
            NotFoundException: If quote not found
            ValidationException: If business rules are violated
        """
        # Get quote
        quote = await self.repository.get_by_id(quote_id)
        if not quote:
            raise NotFoundException(
                resource="Quote",
                resource_id=str(quote_id),
            )

        # Validate quote can be accepted
        if quote.status not in {QuoteStatus.ACTIVE, QuoteStatus.PENDING}:
            raise ValidationException(
                message=f"Cannot accept quote with status {quote.status.value}",
                details={"current_status": quote.status.value},
            )

        # Check if quote is expired
        if quote.is_expired:
            raise ValidationException(
                message="Cannot accept expired quote",
                details={
                    "valid_until": str(quote.valid_until),
                    "days_expired": abs(quote.days_until_expiry),
                },
            )

        # Create policy from quote
        # Generate policy number
        from app.domains.policies.service import PolicyService

        policy_service = PolicyService(self.session)

        # Create basic coverage based on quote
        coverage = CoverageCreate(
            coverage_type="LIABILITY",  # Default coverage type
            coverage_name=f"{str(quote.policy_type).capitalize()} Coverage",
            coverage_amount=quote.requested_coverage_amount,
            deductible=Decimal("0.00"),
            description=f"Coverage converted from quote {quote.quote_number}",
        )

        # Create policy
        policy_data = PolicyCreate(
            policyholder_id=quote.policy_holder_id,
            policy_type=quote.policy_type,
            premium_amount=quote.calculated_premium,
            start_date=data.start_date,
            end_date=data.end_date,
            description=data.description
            or f"Policy converted from quote {quote.quote_number}",
            notes=data.notes,
            coverages=[coverage],
        )

        policy = await policy_service.create_policy(policy_data)

        # Activate the policy immediately
        await policy_service.activate_policy(policy.id)

        # Update quote status to CONVERTED_TO_POLICY
        quote.status = QuoteStatus.CONVERTED_TO_POLICY
        await self.session.commit()

        return {
            "quote": QuoteResponse.model_validate(quote),
            "policy": policy,
        }

    async def reject_quote(self, quote_id: UUID) -> QuoteResponse:
        """Reject a quote.

        Business rules:
        - Quote must exist and be in ACTIVE or PENDING status
        - Updates quote status to REJECTED

        Args:
            quote_id: UUID of the quote to reject

        Returns:
            Updated quote

        Raises:
            NotFoundException: If quote not found
            ValidationException: If business rules are violated
        """
        # Get quote
        quote = await self.repository.get_by_id(quote_id)
        if not quote:
            raise NotFoundException(
                resource="Quote",
                resource_id=str(quote_id),
            )

        # Validate quote can be rejected
        if quote.status not in {QuoteStatus.ACTIVE, QuoteStatus.PENDING}:
            raise ValidationException(
                message=f"Cannot reject quote with status {quote.status.value}",
                details={"current_status": quote.status.value},
            )

        # Update quote status to REJECTED
        quote.status = QuoteStatus.REJECTED
        await self.session.commit()
        await self.session.refresh(quote)

        return QuoteResponse.model_validate(quote)
