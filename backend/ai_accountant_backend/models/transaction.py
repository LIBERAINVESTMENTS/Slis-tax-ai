"""Imported bank/card transactions awaiting matching to journal entries."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_accountant_backend.models.shared import Base, created_at, pk, updated_at


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[pk]
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(200))  # bank statement transaction id
    date: Mapped[str] = mapped_column(String(20), nullable=False)  # ISO date
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[str] = mapped_column(nullable=False)  # Decimal string; positive = credit to account
    currency: Mapped[str] = mapped_column(String(10), default="SRD", nullable=False)
    matched: Mapped[bool] = mapped_column(default=False, nullable=False)
    journal_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entries.id"), nullable=True
    )
    source_document_id: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]



