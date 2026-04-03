"""003_add_quotes_and_pricing_rules_tables

Revision ID: 003
Revises: 002
Create Date: 2026-04-02

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create quote_status_enum
    op.execute(
        "CREATE TYPE quote_status_enum AS ENUM ("
        "'draft', 'pending', 'active', 'accepted', 'rejected', "
        "'expired', 'converted_to_policy')"
    )

    # Create risk_level_enum
    op.execute(
        "CREATE TYPE risk_level_enum AS ENUM ('low', 'medium', 'high', 'very_high')"
    )

    # Create quotes table
    op.create_table(
        "quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quote_number", sa.String(length=50), nullable=False),
        sa.Column("policy_holder_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "policy_type",
            postgresql.ENUM(
                "AUTO",
                "HOME",
                "LIFE",
                "HEALTH",
                name="policy_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "requested_coverage_amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "calculated_premium", sa.Numeric(precision=12, scale=2), nullable=False
        ),
        sa.Column(
            "risk_level",
            postgresql.ENUM(
                "LOW",
                "MEDIUM",
                "HIGH",
                "VERY_HIGH",
                name="risk_level_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "risk_factors", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("valid_until", sa.Date(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "DRAFT",
                "PENDING",
                "ACTIVE",
                "ACCEPTED",
                "REJECTED",
                "EXPIRED",
                "CONVERTED_TO_POLICY",
                name="quote_status_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["policy_holder_id"], ["policy_holders.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for quotes table
    op.create_index(op.f("ix_quotes_id"), "quotes", ["id"], unique=False)
    op.create_index(
        op.f("ix_quotes_quote_number"), "quotes", ["quote_number"], unique=True
    )
    op.create_index(
        op.f("ix_quotes_policy_holder_id"), "quotes", ["policy_holder_id"], unique=False
    )
    op.create_index(
        op.f("ix_quotes_policy_type"), "quotes", ["policy_type"], unique=False
    )
    op.create_index(
        op.f("ix_quotes_risk_level"), "quotes", ["risk_level"], unique=False
    )
    op.create_index(
        op.f("ix_quotes_valid_until"), "quotes", ["valid_until"], unique=False
    )
    op.create_index(op.f("ix_quotes_status"), "quotes", ["status"], unique=False)
    op.create_index(op.f("ix_quotes_is_active"), "quotes", ["is_active"], unique=False)
    op.create_index(
        op.f("ix_quotes_created_at"), "quotes", ["created_at"], unique=False
    )
    op.create_index(
        "ix_quotes_policy_holder_id_status",
        "quotes",
        ["policy_holder_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_quotes_policy_type_risk_level",
        "quotes",
        ["policy_type", "risk_level"],
        unique=False,
    )

    # Create pricing_rules table
    op.create_table(
        "pricing_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "policy_type",
            postgresql.ENUM(
                "AUTO",
                "HOME",
                "LIFE",
                "HEALTH",
                name="policy_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "risk_level",
            postgresql.ENUM(
                "LOW",
                "MEDIUM",
                "HIGH",
                "VERY_HIGH",
                name="risk_level_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("base_premium", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "multiplier_factors",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "base_premium > 0", name="ck_pricing_rules_base_premium_positive"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "policy_type",
            "risk_level",
            "is_active",
            name="uq_pricing_rules_policy_type_risk_level_active",
        ),
    )

    # Create indexes for pricing_rules table
    op.create_index(op.f("ix_pricing_rules_id"), "pricing_rules", ["id"], unique=False)
    op.create_index(
        op.f("ix_pricing_rules_policy_type"),
        "pricing_rules",
        ["policy_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pricing_rules_risk_level"),
        "pricing_rules",
        ["risk_level"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pricing_rules_is_active"),
        "pricing_rules",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        "ix_pricing_rules_policy_type_risk_level",
        "pricing_rules",
        ["policy_type", "risk_level"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes and tables for pricing_rules
    op.drop_index("ix_pricing_rules_policy_type_risk_level", table_name="pricing_rules")
    op.drop_index(op.f("ix_pricing_rules_is_active"), table_name="pricing_rules")
    op.drop_index(op.f("ix_pricing_rules_risk_level"), table_name="pricing_rules")
    op.drop_index(op.f("ix_pricing_rules_policy_type"), table_name="pricing_rules")
    op.drop_index(op.f("ix_pricing_rules_id"), table_name="pricing_rules")
    op.drop_table("pricing_rules")

    # Drop indexes and tables for quotes
    op.drop_index("ix_quotes_policy_type_risk_level", table_name="quotes")
    op.drop_index("ix_quotes_policy_holder_id_status", table_name="quotes")
    op.drop_index(op.f("ix_quotes_created_at"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_is_active"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_status"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_valid_until"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_risk_level"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_policy_type"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_policy_holder_id"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_quote_number"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_id"), table_name="quotes")
    op.drop_table("quotes")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS risk_level_enum")
    op.execute("DROP TYPE IF EXISTS quote_status_enum")
