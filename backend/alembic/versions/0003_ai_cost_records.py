"""Add AI cost/token accounting table."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_ai_cost_records"
down_revision = "0002_tax_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_cost_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("agent", sa.String(length=60), nullable=True),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("tier", sa.String(length=20), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_ai_cost_records_tenant_id", "ai_cost_records", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("ai_cost_records")

