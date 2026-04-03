"""Repository for Pricing data access.

This module implements the Repository pattern for the Pricing domain,
providing an abstraction layer over database operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.pricing.models import PricingRule, Quote
from app.domains.pricing.schemas import (
    PricingRuleCreate,
    PricingRuleUpdate,
    QuoteCreate,
    QuoteUpdate,
)
from app.shared.enums import PolicyType, QuoteStatus, RiskLevel


class QuoteRepository:
    """Repository for Quote database operations.

    Implements the Repository pattern to abstract database queries
    and provide a clean interface for data access.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self,
        data: QuoteCreate,
        quote_number: str,
        calculated_premium: float,
        risk_level: RiskLevel,
        risk_factors: dict,
        valid_until: str,
    ) -> Quote:
        """Create a new quote.

        Args:
            data: Quote creation data
            quote_number: Generated quote number
            calculated_premium: Calculated premium amount
            risk_level: Calculated risk level
            risk_factors: Risk factors used in calculation
            valid_until: Date until which quote is valid

        Returns:
            Created Quote instance
        """
        quote_data = data.model_dump()
        quote = Quote(
            **quote_data,
            quote_number=quote_number,
            calculated_premium=calculated_premium,
            risk_level=risk_level,
            risk_factors=risk_factors,
            valid_until=valid_until,
        )

        self.session.add(quote)
        await self.session.commit()
        await self.session.refresh(quote)
        return quote

    async def get_by_id(self, quote_id: UUID) -> Optional[Quote]:
        """Get a quote by ID.

        Args:
            quote_id: UUID of the quote

        Returns:
            Quote instance if found, None otherwise
        """
        stmt = select(Quote).where(Quote.id == quote_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_quote_number(self, quote_number: str) -> Optional[Quote]:
        """Get a quote by quote number.

        Args:
            quote_number: Quote number

        Returns:
            Quote instance if found, None otherwise
        """
        stmt = select(Quote).where(Quote.quote_number == quote_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        policy_holder_id: Optional[UUID] = None,
        policy_type: Optional[PolicyType] = None,
        status: Optional[QuoteStatus] = None,
        risk_level: Optional[RiskLevel] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> list[Quote]:
        """Get all quotes with optional filtering.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            policy_holder_id: Filter by policy holder ID
            policy_type: Filter by policy type
            status: Filter by quote status
            risk_level: Filter by risk level
            is_active: Filter by active status
            search: Search term for quote_number

        Returns:
            List of Quote instances
        """
        stmt = select(Quote)

        # Apply filters
        if policy_holder_id:
            stmt = stmt.where(Quote.policy_holder_id == policy_holder_id)

        if policy_type:
            stmt = stmt.where(Quote.policy_type == policy_type)

        if status:
            stmt = stmt.where(Quote.status == status)

        if risk_level:
            stmt = stmt.where(Quote.risk_level == risk_level)

        if is_active is not None:
            stmt = stmt.where(Quote.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(Quote.quote_number.ilike(search_pattern))

        # Apply pagination and ordering
        stmt = stmt.order_by(Quote.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        policy_holder_id: Optional[UUID] = None,
        policy_type: Optional[PolicyType] = None,
        status: Optional[QuoteStatus] = None,
        risk_level: Optional[RiskLevel] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count quotes with optional filtering.

        Args:
            policy_holder_id: Filter by policy holder ID
            policy_type: Filter by policy type
            status: Filter by quote status
            risk_level: Filter by risk level
            is_active: Filter by active status
            search: Search term for quote_number

        Returns:
            Total count of matching quotes
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(Quote)

        # Apply same filters as get_all
        if policy_holder_id:
            stmt = stmt.where(Quote.policy_holder_id == policy_holder_id)

        if policy_type:
            stmt = stmt.where(Quote.policy_type == policy_type)

        if status:
            stmt = stmt.where(Quote.status == status)

        if risk_level:
            stmt = stmt.where(Quote.risk_level == risk_level)

        if is_active is not None:
            stmt = stmt.where(Quote.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(Quote.quote_number.ilike(search_pattern))

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(
        self,
        quote_id: UUID,
        data: QuoteUpdate,
    ) -> Optional[Quote]:
        """Update a quote.

        Args:
            quote_id: UUID of the quote to update
            data: Update data (only provided fields will be updated)

        Returns:
            Updated Quote instance if found, None otherwise
        """
        quote = await self.get_by_id(quote_id)
        if not quote:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(quote, field, value)

        await self.session.commit()
        await self.session.refresh(quote)
        return quote

    async def delete(self, quote_id: UUID) -> bool:
        """Soft delete a quote (set is_active to False).

        Args:
            quote_id: UUID of the quote to delete

        Returns:
            True if deleted, False if not found
        """
        quote = await self.get_by_id(quote_id)
        if not quote:
            return False

        quote.is_active = False
        await self.session.commit()
        return True

    async def get_latest_quote_number_sequence(
        self, year: int, policy_type: PolicyType
    ) -> int:
        """Get the latest quote number sequence for a given year and type.

        Args:
            year: Year (e.g., 2026)
            policy_type: Policy type

        Returns:
            Latest sequence number (0 if none exist)
        """
        # Query for quotes with pattern QTE-{year}-{type}-
        pattern = f"QTE-{year}-{policy_type.value.upper()}-%"
        stmt = (
            select(Quote.quote_number)
            .where(Quote.quote_number.like(pattern))
            .order_by(Quote.quote_number.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        latest = result.scalar_one_or_none()

        if not latest:
            return 0

        # Extract sequence number from quote_number (last 5 digits)
        try:
            sequence = int(latest.split("-")[-1])
            return sequence
        except (ValueError, IndexError):
            return 0


class PricingRuleRepository:
    """Repository for PricingRule database operations.

    Implements the Repository pattern to abstract database queries
    and provide a clean interface for data access.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, data: PricingRuleCreate) -> PricingRule:
        """Create a new pricing rule.

        Args:
            data: PricingRule creation data

        Returns:
            Created PricingRule instance
        """
        rule = PricingRule(**data.model_dump())
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def get_by_id(self, rule_id: UUID) -> Optional[PricingRule]:
        """Get a pricing rule by ID.

        Args:
            rule_id: UUID of the pricing rule

        Returns:
            PricingRule instance if found, None otherwise
        """
        stmt = select(PricingRule).where(PricingRule.id == rule_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_rule(
        self,
        policy_type: PolicyType,
        risk_level: RiskLevel,
    ) -> Optional[PricingRule]:
        """Get the active pricing rule for a policy type and risk level.

        Args:
            policy_type: Policy type
            risk_level: Risk level

        Returns:
            Active PricingRule instance if found, None otherwise
        """
        stmt = select(PricingRule).where(
            and_(
                PricingRule.policy_type == policy_type,
                PricingRule.risk_level == risk_level,
                PricingRule.is_active == True,  # noqa: E712
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        policy_type: Optional[PolicyType] = None,
        risk_level: Optional[RiskLevel] = None,
        is_active: Optional[bool] = None,
    ) -> list[PricingRule]:
        """Get all pricing rules with optional filtering.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            policy_type: Filter by policy type
            risk_level: Filter by risk level
            is_active: Filter by active status

        Returns:
            List of PricingRule instances
        """
        stmt = select(PricingRule)

        # Apply filters
        if policy_type:
            stmt = stmt.where(PricingRule.policy_type == policy_type)

        if risk_level:
            stmt = stmt.where(PricingRule.risk_level == risk_level)

        if is_active is not None:
            stmt = stmt.where(PricingRule.is_active == is_active)

        # Apply pagination and ordering
        stmt = stmt.order_by(
            PricingRule.policy_type,
            PricingRule.risk_level,
            PricingRule.created_at.desc(),
        )
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        policy_type: Optional[PolicyType] = None,
        risk_level: Optional[RiskLevel] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count pricing rules with optional filtering.

        Args:
            policy_type: Filter by policy type
            risk_level: Filter by risk level
            is_active: Filter by active status

        Returns:
            Total count of matching pricing rules
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(PricingRule)

        # Apply same filters as get_all
        if policy_type:
            stmt = stmt.where(PricingRule.policy_type == policy_type)

        if risk_level:
            stmt = stmt.where(PricingRule.risk_level == risk_level)

        if is_active is not None:
            stmt = stmt.where(PricingRule.is_active == is_active)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(
        self,
        rule_id: UUID,
        data: PricingRuleUpdate,
    ) -> Optional[PricingRule]:
        """Update a pricing rule.

        Args:
            rule_id: UUID of the pricing rule to update
            data: Update data (only provided fields will be updated)

        Returns:
            Updated PricingRule instance if found, None otherwise
        """
        rule = await self.get_by_id(rule_id)
        if not rule:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def delete(self, rule_id: UUID) -> bool:
        """Soft delete a pricing rule (set is_active to False).

        Args:
            rule_id: UUID of the pricing rule to delete

        Returns:
            True if deleted, False if not found
        """
        rule = await self.get_by_id(rule_id)
        if not rule:
            return False

        rule.is_active = False
        await self.session.commit()
        return True
