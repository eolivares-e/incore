"""Add policy_holders table

Revision ID: 001
Revises:
Create Date: 2026-04-02

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create gender enum
    op.execute(
        "CREATE TYPE gender_enum AS ENUM ('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY')"
    )

    # Create identification_type enum
    op.execute(
        "CREATE TYPE identification_type_enum AS ENUM ('PASSPORT', 'DRIVER_LICENSE', 'NATIONAL_ID', 'SSN')"
    )

    # Create policy_holders table
    op.create_table(
        "policy_holders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column(
            "gender",
            postgresql.ENUM(
                "MALE",
                "FEMALE",
                "OTHER",
                "PREFER_NOT_TO_SAY",
                name="gender_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("street_address", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("zip_code", sa.String(length=10), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column(
            "identification_type",
            postgresql.ENUM(
                "PASSPORT",
                "DRIVER_LICENSE",
                "NATIONAL_ID",
                "SSN",
                name="identification_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("identification_number", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_policy_holders_id"), "policy_holders", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_policy_holders_first_name"),
        "policy_holders",
        ["first_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_policy_holders_last_name"),
        "policy_holders",
        ["last_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_policy_holders_email"), "policy_holders", ["email"], unique=True
    )
    op.create_index(
        op.f("ix_policy_holders_identification_number"),
        "policy_holders",
        ["identification_number"],
        unique=False,
    )
    op.create_index(
        op.f("ix_policy_holders_is_active"),
        "policy_holders",
        ["is_active"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index(op.f("ix_policy_holders_is_active"), table_name="policy_holders")
    op.drop_index(
        op.f("ix_policy_holders_identification_number"), table_name="policy_holders"
    )
    op.drop_index(op.f("ix_policy_holders_email"), table_name="policy_holders")
    op.drop_index(op.f("ix_policy_holders_last_name"), table_name="policy_holders")
    op.drop_index(op.f("ix_policy_holders_first_name"), table_name="policy_holders")
    op.drop_index(op.f("ix_policy_holders_id"), table_name="policy_holders")

    # Drop table
    op.drop_table("policy_holders")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS identification_type_enum")
    op.execute("DROP TYPE IF EXISTS gender_enum")
