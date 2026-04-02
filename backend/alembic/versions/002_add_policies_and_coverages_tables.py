"""002_add_policies_and_coverages_tables

Revision ID: 002
Revises: 001
Create Date: 2026-04-02

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create policy_type_enum
    op.execute(
        "CREATE TYPE policy_type_enum AS ENUM ('AUTO', 'HOME', 'LIFE', 'HEALTH', 'TRAVEL')"
    )

    # Create policy_status_enum
    op.execute(
        "CREATE TYPE policy_status_enum AS ENUM ('DRAFT', 'PENDING_APPROVAL', 'ACTIVE', 'SUSPENDED', 'EXPIRED', 'CANCELLED', 'PENDING_RENEWAL')"
    )

    # Create coverage_type_enum
    op.execute(
        "CREATE TYPE coverage_type_enum AS ENUM ("
        "'LIABILITY', 'COLLISION', 'COMPREHENSIVE', 'PERSONAL_INJURY_PROTECTION', "
        "'UNINSURED_MOTORIST', 'DWELLING', 'PERSONAL_PROPERTY', 'LIABILITY_HOME', "
        "'ADDITIONAL_LIVING_EXPENSES', 'DEATH_BENEFIT', 'ACCIDENTAL_DEATH', "
        "'CRITICAL_ILLNESS', 'MEDICAL', 'DENTAL', 'VISION', 'PRESCRIPTION', "
        "'MENTAL_HEALTH', 'OTHER')"
    )

    # Create policies table
    op.create_table(
        "policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("policy_number", sa.String(length=50), nullable=False),
        sa.Column("policyholder_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "policy_type",
            postgresql.ENUM(
                "AUTO",
                "HOME",
                "LIFE",
                "HEALTH",
                "TRAVEL",
                name="policy_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "DRAFT",
                "PENDING_APPROVAL",
                "ACTIVE",
                "SUSPENDED",
                "EXPIRED",
                "CANCELLED",
                "PENDING_RENEWAL",
                name="policy_status_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("premium_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["policyholder_id"], ["policy_holders.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_policies_end_date"), "policies", ["end_date"], unique=False
    )
    op.create_index(op.f("ix_policies_id"), "policies", ["id"], unique=False)
    op.create_index(
        op.f("ix_policies_is_active"), "policies", ["is_active"], unique=False
    )
    op.create_index(
        op.f("ix_policies_policy_number"), "policies", ["policy_number"], unique=True
    )
    op.create_index(
        op.f("ix_policies_policy_type"), "policies", ["policy_type"], unique=False
    )
    op.create_index(
        op.f("ix_policies_policyholder_id"),
        "policies",
        ["policyholder_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_policies_start_date"), "policies", ["start_date"], unique=False
    )
    op.create_index(op.f("ix_policies_status"), "policies", ["status"], unique=False)

    # Create coverages table
    op.create_table(
        "coverages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "coverage_type",
            postgresql.ENUM(
                "LIABILITY",
                "COLLISION",
                "COMPREHENSIVE",
                "PERSONAL_INJURY_PROTECTION",
                "UNINSURED_MOTORIST",
                "DWELLING",
                "PERSONAL_PROPERTY",
                "LIABILITY_HOME",
                "ADDITIONAL_LIVING_EXPENSES",
                "DEATH_BENEFIT",
                "ACCIDENTAL_DEATH",
                "CRITICAL_ILLNESS",
                "MEDICAL",
                "DENTAL",
                "VISION",
                "PRESCRIPTION",
                "MENTAL_HEALTH",
                "OTHER",
                name="coverage_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("coverage_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("coverage_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("deductible", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["policy_id"], ["policies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_coverages_coverage_type"), "coverages", ["coverage_type"], unique=False
    )
    op.create_index(op.f("ix_coverages_id"), "coverages", ["id"], unique=False)
    op.create_index(
        op.f("ix_coverages_is_active"), "coverages", ["is_active"], unique=False
    )
    op.create_index(
        op.f("ix_coverages_policy_id"), "coverages", ["policy_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes and tables
    op.drop_index(op.f("ix_coverages_policy_id"), table_name="coverages")
    op.drop_index(op.f("ix_coverages_is_active"), table_name="coverages")
    op.drop_index(op.f("ix_coverages_id"), table_name="coverages")
    op.drop_index(op.f("ix_coverages_coverage_type"), table_name="coverages")
    op.drop_table("coverages")
    op.drop_index(op.f("ix_policies_status"), table_name="policies")
    op.drop_index(op.f("ix_policies_start_date"), table_name="policies")
    op.drop_index(op.f("ix_policies_policyholder_id"), table_name="policies")
    op.drop_index(op.f("ix_policies_policy_type"), table_name="policies")
    op.drop_index(op.f("ix_policies_policy_number"), table_name="policies")
    op.drop_index(op.f("ix_policies_is_active"), table_name="policies")
    op.drop_index(op.f("ix_policies_id"), table_name="policies")
    op.drop_index(op.f("ix_policies_end_date"), table_name="policies")
    op.drop_table("policies")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS coverage_type_enum")
    op.execute("DROP TYPE IF EXISTS policy_status_enum")
    op.execute("DROP TYPE IF EXISTS policy_type_enum")
