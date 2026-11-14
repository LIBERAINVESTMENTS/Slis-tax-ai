"""Tax returns and filings — approval-gated, never claims submission without proof."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ai_accountant_backend.models.shared import Base, created_at, pk, updated_at


class TaxReturn(Base):
    __tablename__ = "tax_returns"

    id: Mapped[pk]
    company_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)  # NULL = personal return
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    country: Mapped[str] = mapped_column(String(10), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(40), nullable=False)
    period_start: Mapped[str] = mapped_column(String(20), nullable=False)  # ISO date
    period_end: Mapped[str] = mapped_column(String(20), nullable=False)
    # Calculated amounts (Decimal strings)
    taxable_amount: Mapped[str] = mapped_column(default="0", nullable=False)
    tax_owed: Mapped[str] = mapped_column(default="0", nullable=False)
    tax_paid: Mapped[str] = mapped_column(default="0", nullable=False)
    # Status: draft | submitted | accepted | rejected
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    # User approval: requires explicit authorization before any submission
    approved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Submission proof: only set when an authorized submission actually occurred
    submission_proof: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[str | None] = mapped_column(String(20), nullable=True)
    filing_deadline: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = created_at
    updated_at: Mapped[datetime] = updated_at

