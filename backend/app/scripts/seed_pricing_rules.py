"""Seed initial pricing rules.

This script creates the initial set of pricing rules for all combinations of
policy types and risk levels.

Run this after applying migration 003:
    python -m app.scripts.seed_pricing_rules
"""

import asyncio
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.database import Base

# Import all models to register them
from app.domains.policy_holders.models import PolicyHolder  # noqa: F401
from app.domains.policies.models import Coverage, Policy  # noqa: F401
from app.domains.pricing.models import PricingRule, Quote  # noqa: F401
from app.domains.pricing.repository import PricingRuleRepository
from app.domains.pricing.schemas import PricingRuleCreate
from app.shared.enums import PolicyType, RiskLevel


async def seed_pricing_rules():
    """Seed initial pricing rules for all policy types and risk levels."""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # Get a session
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker

        async_session_maker = sessionmaker(
            conn, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session_maker() as session:
            repository = PricingRuleRepository(session)

            # Define pricing rules for each policy type and risk level
            rules = [
                # AUTO Insurance
                PricingRuleCreate(
                    name="Auto - Low Risk",
                    description="Base pricing for low-risk auto insurance policies",
                    policy_type=PolicyType.AUTO,
                    risk_level=RiskLevel.LOW,
                    base_premium=Decimal("800.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.05,
                        "young_driver_multiplier": 1.2,
                        "senior_driver_multiplier": 1.15,
                    },
                ),
                PricingRuleCreate(
                    name="Auto - Medium Risk",
                    description="Base pricing for medium-risk auto insurance policies",
                    policy_type=PolicyType.AUTO,
                    risk_level=RiskLevel.MEDIUM,
                    base_premium=Decimal("1200.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.06,
                        "young_driver_multiplier": 1.3,
                        "senior_driver_multiplier": 1.2,
                    },
                ),
                PricingRuleCreate(
                    name="Auto - High Risk",
                    description="Base pricing for high-risk auto insurance policies",
                    policy_type=PolicyType.AUTO,
                    risk_level=RiskLevel.HIGH,
                    base_premium=Decimal("1800.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.08,
                        "young_driver_multiplier": 1.5,
                        "senior_driver_multiplier": 1.3,
                    },
                ),
                PricingRuleCreate(
                    name="Auto - Very High Risk",
                    description="Base pricing for very high-risk auto insurance policies",
                    policy_type=PolicyType.AUTO,
                    risk_level=RiskLevel.VERY_HIGH,
                    base_premium=Decimal("2500.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.10,
                        "young_driver_multiplier": 1.8,
                        "senior_driver_multiplier": 1.5,
                    },
                ),
                # HOME Insurance
                PricingRuleCreate(
                    name="Home - Low Risk",
                    description="Base pricing for low-risk home insurance policies",
                    policy_type=PolicyType.HOME,
                    risk_level=RiskLevel.LOW,
                    base_premium=Decimal("600.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.04,
                        "young_driver_multiplier": 1.0,
                        "senior_driver_multiplier": 1.0,
                    },
                ),
                PricingRuleCreate(
                    name="Home - Medium Risk",
                    description="Base pricing for medium-risk home insurance policies",
                    policy_type=PolicyType.HOME,
                    risk_level=RiskLevel.MEDIUM,
                    base_premium=Decimal("900.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.05,
                        "young_driver_multiplier": 1.0,
                        "senior_driver_multiplier": 1.0,
                    },
                ),
                PricingRuleCreate(
                    name="Home - High Risk",
                    description="Base pricing for high-risk home insurance policies",
                    policy_type=PolicyType.HOME,
                    risk_level=RiskLevel.HIGH,
                    base_premium=Decimal("1400.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.07,
                        "young_driver_multiplier": 1.0,
                        "senior_driver_multiplier": 1.0,
                    },
                ),
                PricingRuleCreate(
                    name="Home - Very High Risk",
                    description="Base pricing for very high-risk home insurance policies",
                    policy_type=PolicyType.HOME,
                    risk_level=RiskLevel.VERY_HIGH,
                    base_premium=Decimal("2000.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.09,
                        "young_driver_multiplier": 1.0,
                        "senior_driver_multiplier": 1.0,
                    },
                ),
                # LIFE Insurance
                PricingRuleCreate(
                    name="Life - Low Risk",
                    description="Base pricing for low-risk life insurance policies",
                    policy_type=PolicyType.LIFE,
                    risk_level=RiskLevel.LOW,
                    base_premium=Decimal("400.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.03,
                        "young_driver_multiplier": 0.8,
                        "senior_driver_multiplier": 1.5,
                    },
                ),
                PricingRuleCreate(
                    name="Life - Medium Risk",
                    description="Base pricing for medium-risk life insurance policies",
                    policy_type=PolicyType.LIFE,
                    risk_level=RiskLevel.MEDIUM,
                    base_premium=Decimal("700.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.04,
                        "young_driver_multiplier": 0.9,
                        "senior_driver_multiplier": 1.8,
                    },
                ),
                PricingRuleCreate(
                    name="Life - High Risk",
                    description="Base pricing for high-risk life insurance policies",
                    policy_type=PolicyType.LIFE,
                    risk_level=RiskLevel.HIGH,
                    base_premium=Decimal("1200.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.06,
                        "young_driver_multiplier": 1.0,
                        "senior_driver_multiplier": 2.2,
                    },
                ),
                PricingRuleCreate(
                    name="Life - Very High Risk",
                    description="Base pricing for very high-risk life insurance policies",
                    policy_type=PolicyType.LIFE,
                    risk_level=RiskLevel.VERY_HIGH,
                    base_premium=Decimal("2000.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.08,
                        "young_driver_multiplier": 1.2,
                        "senior_driver_multiplier": 3.0,
                    },
                ),
                # HEALTH Insurance
                PricingRuleCreate(
                    name="Health - Low Risk",
                    description="Base pricing for low-risk health insurance policies",
                    policy_type=PolicyType.HEALTH,
                    risk_level=RiskLevel.LOW,
                    base_premium=Decimal("300.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.02,
                        "young_driver_multiplier": 0.9,
                        "senior_driver_multiplier": 1.4,
                    },
                ),
                PricingRuleCreate(
                    name="Health - Medium Risk",
                    description="Base pricing for medium-risk health insurance policies",
                    policy_type=PolicyType.HEALTH,
                    risk_level=RiskLevel.MEDIUM,
                    base_premium=Decimal("500.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.03,
                        "young_driver_multiplier": 1.0,
                        "senior_driver_multiplier": 1.6,
                    },
                ),
                PricingRuleCreate(
                    name="Health - High Risk",
                    description="Base pricing for high-risk health insurance policies",
                    policy_type=PolicyType.HEALTH,
                    risk_level=RiskLevel.HIGH,
                    base_premium=Decimal("900.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.05,
                        "young_driver_multiplier": 1.1,
                        "senior_driver_multiplier": 2.0,
                    },
                ),
                PricingRuleCreate(
                    name="Health - Very High Risk",
                    description="Base pricing for very high-risk health insurance policies",
                    policy_type=PolicyType.HEALTH,
                    risk_level=RiskLevel.VERY_HIGH,
                    base_premium=Decimal("1500.00"),
                    multiplier_factors={
                        "coverage_per_100k": 0.07,
                        "young_driver_multiplier": 1.2,
                        "senior_driver_multiplier": 2.5,
                    },
                ),
            ]

            # Create all pricing rules
            print(f"Creating {len(rules)} pricing rules...")
            for rule_data in rules:
                rule = await repository.create(rule_data)
                print(f"  ✓ Created: {rule.name}")

            await session.commit()
            print(f"\n✓ Successfully created {len(rules)} pricing rules!")


if __name__ == "__main__":
    asyncio.run(seed_pricing_rules())
