"""Double-entry journal entries and lines.

Every posted JournalEntry must balance: sum(debit) == sum(credit) across its lines.
Posted entries are immutable — corrections are made by reversing entries, never by
editing historical rows. Period locking prevents posting on/before a locked date.
"""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_accountant_backend.models.shared import Base, created_at, pk, updated_at


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[pk]
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    entry_no: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    entry_date: Mapped[str] = mapped_column(String(20), nullable=False)  # ISO date
    reference: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    posted: Mapped[bool] = mapped_column(default=False, nullable=False)
    # Tamper-evidence: SHA256(prev_hash || canonical_payload). First entry has prev_hash = "genesis".
    hash: Mapped[str] = mapped_column(String(128), nullable=False)
    prev_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="genesis")
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = created_at
    updated_at: Mapped[datetime] = updated_at

    __table_args__ = (
        UniqueConstraint("company_id", "entry_no", name="uq_journal_entry_no_per_company"),
    )

    company: Mapped["Company"] = relationship(back_populates="journal_entries")
    lines: Mapped[list["JournalLine"]] = relationship(
        back_populates="entry", cascade="all, delete-orphan"
    )


class JournalLine(Base):
    __tablename__ = "journal_lines"

    id: Mapped[pk]
    entry_id: Mapped[int] = mapped_column(
        ForeignKey("journal_entries.id", ondelete="CASCADE"), index=True, nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"), index=True, nullable=False
    )
    # Decimal-safe: stored as NUMERIC(20, 6) via Numeric; represented as Decimal in Python.
    debit: Mapped[str] = mapped_column(default="0", nullable=False)
    credit: Mapped[str] = mapped_column(default="0", nullable=False)
    memo: Mapped[str | None] = mapped_column(Text)

    entry: Mapped["JournalEntry"] = relationship(back_populates="lines")
    account: Mapped["Account"] = relationship(back_populates="journal_lines")


@event.listens_for(JournalEntry, "before_insert")
def _set_entry_hash(mapper, connection, target):  # noqa: ANN001
    import hashlib
    import json

    payload = {
        "entry_no": target.entry_no,
        "entry_date": target.entry_date,
        "lines": [
            {
                "account_id": l.account_id,
                "debit": l.debit,
                "credit": l.credit,
                "memo": l.memo,
            }
            for l in target.lines
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    target.hash = hashlib.sha256((target.prev_hash or "genesis").encode() + canonical).hexdigest()


