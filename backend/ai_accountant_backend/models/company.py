"""Company model — multiple business entities per user/tenant, strictly isolated."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_accountant_backend.models.shared import Base, created_at, pk, updated_at


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[pk]
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)  # owning user's tenant
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    country: Mapped[str] = mapped_column(String(10), default="SR", nullable=False)  # ISO country; Suriname = SR
    currency: Mapped[str] = mapped_column(String(10), default="SRD", nullable=False)
    fiscal_year_start_month: Mapped[int] = mapped_column(default=1, nullable=False)  # 1=January
    tax_regime: Mapped[str | None] = mapped_column(String(100))  # e.g. "suriname_corporate"
    period_lock_date: Mapped[str | None] = mapped_column(String(20))  # ISO date; no posting on/before
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    accounts: Mapped[list["Account"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )



