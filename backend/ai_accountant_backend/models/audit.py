"""Tamper-evident audit log for every financial mutation."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ai_accountant_backend.models.shared import Base, created_at, pk


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[pk]
    tenant_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    company_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. journal.post, tax.return.submit
    entity_type: Mapped[str | None] = mapped_column(String(60))
    entity_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    before: Mapped[str | None] = mapped_column(Text)  # JSON snapshot before change
    after: Mapped[str | None] = mapped_column(Text)  # JSON snapshot after change
    # Hash chain: SHA256(prev_hash || actor || action || entity || after)
    hash: Mapped[str] = mapped_column(String(128), nullable=False)
    prev_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="genesis")
    created_at: Mapped[datetime] = created_at


