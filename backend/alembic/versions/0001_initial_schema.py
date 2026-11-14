"""Initial schema for AI Accountant.

Creates tenants, users, companies, chart of accounts, journal entries/lines,
imported transactions, and audit log.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_tenants_slug"),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="employee"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("totp_secret", sa.String(length=200), nullable=True),
        sa.Column("mfa_recovery_codes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=10), nullable=False, server_default="SR"),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="SRD"),
        sa.Column("fiscal_year_start_month", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("tax_regime", sa.String(length=100), nullable=True),
        sa.Column("period_lock_date", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_companies_tenant_id", "companies", ["tenant_id"])
    op.create_index("ix_companies_slug", "companies", ["slug"])

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("subtype", sa.String(length=40), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="SRD"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_accounts_company_id", "accounts", ["company_id"])

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("entry_no", sa.String(length=50), nullable=False),
        sa.Column("entry_date", sa.String(length=20), nullable=False),
        sa.Column("reference", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("posted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("hash", sa.String(length=128), nullable=False),
        sa.Column("prev_hash", sa.String(length=128), nullable=False, server_default="genesis"),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("company_id", "entry_no", name="uq_journal_entries_entry_no_per_company"),
    )
    op.create_index("ix_journal_entries_company_id", "journal_entries", ["company_id"])

    op.create_table(
        "journal_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("debit", sa.String(), nullable=False, server_default="0"),
        sa.Column("credit", sa.String(), nullable=False, server_default="0"),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["entry_id"], ["journal_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_journal_lines_entry_id", "journal_lines", ["entry_id"])
    op.create_index("ix_journal_lines_account_id", "journal_lines", ["account_id"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=200), nullable=True),
        sa.Column("date", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.String(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="SRD"),
        sa.Column("matched", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("journal_entry_id", sa.Integer(), nullable=True),
        sa.Column("source_document_id", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_transactions_company_id", "transactions", ["company_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=60), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("before", sa.Text(), nullable=True),
        sa.Column("after", sa.Text(), nullable=True),
        sa.Column("hash", sa.String(length=128), nullable=False),
        sa.Column("prev_hash", sa.String(length=128), nullable=False, server_default="genesis"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])
    op.create_index("ix_audit_logs_company_id", "audit_logs", ["company_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("transactions")
    op.drop_table("journal_lines")
    op.drop_table("journal_entries")
    op.drop_table("accounts")
    op.drop_table("companies")
    op.drop_table("users")
    op.drop_table("tenants")

