"""rename payment metadata column

Revision ID: 983338379ccf
Revises: e61487a312a2
Create Date: 2026-04-03 00:14:44.613072

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "983338379ccf"
down_revision: Union[str, None] = "e61487a312a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename metadata column to payment_metadata
    op.alter_column("payments", "metadata", new_column_name="payment_metadata")


def downgrade() -> None:
    # Rename back to metadata
    op.alter_column("payments", "payment_metadata", new_column_name="metadata")
