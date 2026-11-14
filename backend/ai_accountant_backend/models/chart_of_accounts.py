"""Chart of accounts — account definitions per company."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_accountant_backend.models.shared import Base, created_at, pk, updated_at


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[pk]
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False)  # e.g. "1000", "4100"
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # asset | liability | equity | revenue | expense
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    # bank | cash | receivable | payable | inventory | fixed_asset | equity | revenue | expense | ...
    subtype: Mapped[str | None] = mapped_column(String(40))
    currency: Mapped[str] = mapped_column(String(10), default="SRD", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    company: Mapped["Company"] = relationship(back_populates="accounts")
    journal_lines: Mapped[list["JournalLine"]] = relationship(back_populates="account")



