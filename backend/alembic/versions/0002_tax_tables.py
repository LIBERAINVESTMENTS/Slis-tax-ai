"""Add tax rules and tax returns tables."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_tax_tables"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tax_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("country", sa.String(length=10), nullable=False),
        sa.Column("tax_type", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("rate", sa.String(length=50), nullable=True),
        sa.Column("basis", sa.String(length=100), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("effective_date", sa.String(length=20), nullable=True),
        sa.Column("expiry_date", sa.String(length=20), nullable=True),
        sa.Column("last_verified_date", sa.String(length=20), nullable=True),
        sa.Column("verification_status", sa.String(length=20), nullable=False, server_default="verified"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tax_rules_country", "tax_rules", ["country"])
    op.create_index("ix_tax_rules_tax_type", "tax_rules", ["tax_type"])

    op.create_table(
        "tax_returns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("country", sa.String(length=10), nullable=False),
        sa.Column("tax_type", sa.String(length=40), nullable=False),
        sa.Column("period_start", sa.String(length=20), nullable=False),
        sa.Column("period_end", sa.String(length=20), nullable=False),
        sa.Column("taxable_amount", sa.String(), nullable=False, server_default="0"),
        sa.Column("tax_owed", sa.String(), nullable=False, server_default="0"),
        sa.Column("tax_paid", sa.String(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("approved_by_user_id", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.String(length=20), nullable=True),
        sa.Column("submission_proof", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.String(length=20), nullable=True),
        sa.Column("filing_deadline", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_tax_returns_company_id", "tax_returns", ["company_id"])
    op.create_index("ix_tax_returns_user_id", "tax_returns", ["user_id"])


def downgrade() -> None:
    op.drop_table("tax_returns")
    op.drop_table("tax_rules")

