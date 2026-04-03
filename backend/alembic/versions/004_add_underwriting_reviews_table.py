"""add underwriting_reviews table

Revision ID: 004
Revises: 003
Create Date: 2026-04-02 21:35:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create underwriting_status_enum (risk_level_enum already exists from migration 003)
    op.execute(
        "CREATE TYPE underwriting_status_enum AS ENUM ("
        "'pending', 'in_review', 'approved', 'rejected', "
        "'requires_manual_review', 'conditionally_approved')"
    )

    # Create underwriting_reviews table
    op.create_table(
        "underwriting_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "in_review",
                "approved",
                "rejected",
                "requires_manual_review",
                "conditionally_approved",
                name="underwriting_status_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "risk_level",
            postgresql.ENUM(
                "low",
                "medium",
                "high",
                "very_high",
                name="risk_level_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column(
            "risk_assessment", postgresql.JSONB(), nullable=False, server_default="{}"
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        # Primary key
        sa.PrimaryKeyConstraint("id", name="underwriting_reviews_pkey"),
        # Foreign key constraints
        sa.ForeignKeyConstraint(
            ["quote_id"],
            ["quotes.id"],
            name="underwriting_reviews_quote_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["policy_id"],
            ["policies.id"],
            name="underwriting_reviews_policy_id_fkey",
            ondelete="CASCADE",
        ),
        # Check constraints
        sa.CheckConstraint(
            "risk_score >= 0 AND risk_score <= 100",
            name="ck_underwriting_reviews_risk_score_range",
        ),
        sa.CheckConstraint(
            "(quote_id IS NOT NULL AND policy_id IS NULL) OR (quote_id IS NULL AND policy_id IS NOT NULL)",
            name="ck_underwriting_reviews_quote_or_policy",
        ),
    )

    # Create indexes
    op.create_index("ix_underwriting_reviews_id", "underwriting_reviews", ["id"])
    op.create_index(
        "ix_underwriting_reviews_quote_id", "underwriting_reviews", ["quote_id"]
    )
    op.create_index(
        "ix_underwriting_reviews_policy_id", "underwriting_reviews", ["policy_id"]
    )
    op.create_index(
        "ix_underwriting_reviews_reviewer_id", "underwriting_reviews", ["reviewer_id"]
    )
    op.create_index(
        "ix_underwriting_reviews_status", "underwriting_reviews", ["status"]
    )
    op.create_index(
        "ix_underwriting_reviews_risk_level", "underwriting_reviews", ["risk_level"]
    )
    op.create_index(
        "ix_underwriting_reviews_risk_score", "underwriting_reviews", ["risk_score"]
    )
    op.create_index(
        "ix_underwriting_reviews_created_at", "underwriting_reviews", ["created_at"]
    )
    op.create_index(
        "ix_underwriting_reviews_status_risk_level",
        "underwriting_reviews",
        ["status", "risk_level"],
    )
    op.create_index(
        "ix_underwriting_reviews_quote_id_status",
        "underwriting_reviews",
        ["quote_id", "status"],
    )
    op.create_index(
        "ix_underwriting_reviews_policy_id_status",
        "underwriting_reviews",
        ["policy_id", "status"],
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(
        "ix_underwriting_reviews_policy_id_status", table_name="underwriting_reviews"
    )
    op.drop_index(
        "ix_underwriting_reviews_quote_id_status", table_name="underwriting_reviews"
    )
    op.drop_index(
        "ix_underwriting_reviews_status_risk_level", table_name="underwriting_reviews"
    )
    op.drop_index(
        "ix_underwriting_reviews_created_at", table_name="underwriting_reviews"
    )
    op.drop_index(
        "ix_underwriting_reviews_risk_score", table_name="underwriting_reviews"
    )
    op.drop_index(
        "ix_underwriting_reviews_risk_level", table_name="underwriting_reviews"
    )
    op.drop_index("ix_underwriting_reviews_status", table_name="underwriting_reviews")
    op.drop_index(
        "ix_underwriting_reviews_reviewer_id", table_name="underwriting_reviews"
    )
    op.drop_index(
        "ix_underwriting_reviews_policy_id", table_name="underwriting_reviews"
    )
    op.drop_index("ix_underwriting_reviews_quote_id", table_name="underwriting_reviews")
    op.drop_index("ix_underwriting_reviews_id", table_name="underwriting_reviews")

    # Drop table
    op.drop_table("underwriting_reviews")

    # Drop underwriting_status_enum
    op.execute("DROP TYPE underwriting_status_enum")
