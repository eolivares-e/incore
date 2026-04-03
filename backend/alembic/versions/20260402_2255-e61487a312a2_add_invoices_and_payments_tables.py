"""add invoices and payments tables

Revision ID: e61487a312a2
Revises: 004
Create Date: 2026-04-02 22:55:07.928791

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e61487a312a2"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE invoice_status_enum AS ENUM (
                'draft', 'pending', 'sent', 'paid', 'overdue', 
                'partially_paid', 'cancelled', 'refunded'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE payment_method_enum AS ENUM (
                'credit_card', 'debit_card', 'bank_transfer', 
                'cash', 'check', 'digital_wallet'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE payment_status_enum AS ENUM (
                'pending', 'processing', 'completed', 'failed',
                'refunded', 'partially_refunded', 'cancelled'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create invoices table
    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_number", sa.String(length=50), nullable=False),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_due", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "amount_paid",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("paid_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft",
                "pending",
                "sent",
                "paid",
                "overdue",
                "partially_paid",
                "cancelled",
                "refunded",
                name="invoice_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount_due > 0", name="check_invoice_amount_due_positive"),
        sa.CheckConstraint(
            "amount_paid >= 0", name="check_invoice_amount_paid_non_negative"
        ),
        sa.CheckConstraint(
            "amount_paid <= amount_due",
            name="check_invoice_amount_paid_not_exceeds_due",
        ),
        sa.ForeignKeyConstraint(["policy_id"], ["policies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invoices_id", "invoices", ["id"], unique=False)
    op.create_index(
        "ix_invoices_invoice_number", "invoices", ["invoice_number"], unique=True
    )
    op.create_index("ix_invoices_policy_id", "invoices", ["policy_id"], unique=False)
    op.create_index("ix_invoices_due_date", "invoices", ["due_date"], unique=False)
    op.create_index("ix_invoices_status", "invoices", ["status"], unique=False)

    # Create payments table
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "payment_method",
            postgresql.ENUM(
                "credit_card",
                "debit_card",
                "bank_transfer",
                "cash",
                "check",
                "digital_wallet",
                name="payment_method_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("payment_date", sa.DateTime(), nullable=False),
        sa.Column("transaction_id", sa.String(length=100), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(length=100), nullable=True),
        sa.Column("stripe_charge_id", sa.String(length=100), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "processing",
                "completed",
                "failed",
                "refunded",
                "partially_refunded",
                "cancelled",
                name="payment_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount > 0", name="check_payment_amount_positive"),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payments_id", "payments", ["id"], unique=False)
    op.create_index("ix_payments_invoice_id", "payments", ["invoice_id"], unique=False)
    op.create_index(
        "ix_payments_payment_date", "payments", ["payment_date"], unique=False
    )
    op.create_index("ix_payments_status", "payments", ["status"], unique=False)
    op.create_index(
        "ix_payments_transaction_id", "payments", ["transaction_id"], unique=True
    )
    op.create_index(
        "ix_payments_stripe_payment_intent_id",
        "payments",
        ["stripe_payment_intent_id"],
        unique=True,
    )


def downgrade() -> None:
    # Drop payments table
    op.drop_index("ix_payments_stripe_payment_intent_id", table_name="payments")
    op.drop_index("ix_payments_transaction_id", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_payment_date", table_name="payments")
    op.drop_index("ix_payments_invoice_id", table_name="payments")
    op.drop_index("ix_payments_id", table_name="payments")
    op.drop_table("payments")

    # Drop invoices table
    op.drop_index("ix_invoices_status", table_name="invoices")
    op.drop_index("ix_invoices_due_date", table_name="invoices")
    op.drop_index("ix_invoices_policy_id", table_name="invoices")
    op.drop_index("ix_invoices_invoice_number", table_name="invoices")
    op.drop_index("ix_invoices_id", table_name="invoices")
    op.drop_table("invoices")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS payment_status_enum")
    op.execute("DROP TYPE IF EXISTS payment_method_enum")
    op.execute("DROP TYPE IF EXISTS invoice_status_enum")
