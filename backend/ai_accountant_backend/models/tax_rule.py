"""Tax rules — country-specific, with source/effective/verification metadata.

Every rule carries source_url, effective_date, expiry_date, last_verified_date, and
verification_status so the platform never invents rates and can distinguish current
legislation from proposed/outdated rules.
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ai_accountant_backend.models.shared import Base, created_at, pk, updated_at


class TaxRule(Base):
    __tablename__ = "tax_rules"

    id: Mapped[pk]
    country: Mapped[str] = mapped_column(String(10), index=True, nullable=False)  # ISO e.g. "SR"
    tax_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False)  # corporate_income_tax, vat, wage_tax, withholding_tax, personal_income_tax
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    rate: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Decimal string or bracket spec as JSON
    basis: Mapped[str | None] = mapped_column(String(100), nullable=True)  # what the rate applies to
    source_url: Mapped[str | None] = mapped_column(Text)
    effective_date: Mapped[str | None] = mapped_column(String(20))  # ISO date
    expiry_date: Mapped[str | None] = mapped_column(String(20))
    last_verified_date: Mapped[str | None] = mapped_column(String(20))
    verification_status: Mapped[str] = mapped_column(String(20), default="verified")  # verified | pending | outdated | proposed
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = created_at
    updated_at: Mapped[datetime] = updated_at

