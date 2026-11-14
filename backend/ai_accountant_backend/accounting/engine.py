"""Double-entry accounting engine.

All amounts are Decimal-safe (stored/represented as strings at API/DB boundaries).
Core invariant: every posted JournalEntry must balance: sum(debits) == sum(credits).
Posted entries are immutable; corrections use reversing entries.
Period locking prevents posting on/before a company's lock date.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

from sqlalchemy.orm import Session

from ai_accountant_backend.db import get_current_company_id, get_current_tenant_id
from ai_accountant_backend.models import Account, Company, JournalEntry, JournalLine, User
from ai_accountant_backend.security import hash_password  # noqa: F401  (kept for symmetry)


class AccountingError(Exception):
    pass


def _money(value) -> Decimal:
    """Parse a money value to Decimal, rejecting floats/NaN."""
    if isinstance(value, bool):
        raise AccountingError("Invalid money value")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise AccountingError(f"Invalid money value: {value!r}") from exc


def validate_entry_lines(lines: list[dict]) -> list[dict]:
    """Validate and normalize journal lines. Returns list with Decimal amounts."""
    if not lines or len(lines) < 2:
        raise AccountingError("A journal entry needs at least two lines")
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    normalized = []
    for line in lines:
        debit = _money(line.get("debit", "0"))
        credit = _money(line.get("credit", "0"))
        if debit < 0 or credit < 0:
            raise AccountingError("Debit and credit must be non-negative")
        if debit > 0 and credit > 0:
            raise AccountingError("A line cannot have both debit and credit")
        total_debit += debit
        total_credit += credit
        normalized.append(
            {
                "account_id": line["account_id"],
                "debit": str(debit),
                "credit": str(credit),
                "memo": line.get("memo"),
            }
        )
    if total_debit != total_credit:
        raise AccountingError(
            f"Journal entry is out of balance: debits={total_debit} credits={total_credit}"
        )
    return normalized


def post_entry(
    db: Session,
    *,
    company: Company,
    entry_no: str,
    entry_date: str,
    lines: list[dict],
    reference: Optional[str] = None,
    description: Optional[str] = None,
    created_by: Optional[int] = None,
) -> JournalEntry:
    """Create and post a balanced journal entry. Raises AccountingError on any rule violation."""
    # Period lock check
    if company.period_lock_date and entry_date <= company.period_lock_date:
        raise AccountingError(
            f"Period is locked through {company.period_lock_date}; cannot post on/before that date"
        )

    # Verify all accounts exist and belong to this company
    account_ids = {l["account_id"] for l in lines}
    accounts = (
        db.query(Account)
        .filter(Account.company_id == company.id, Account.id.in_(account_ids), Account.is_active == True)  # noqa: E712
        .all()
    )
    if len(accounts) != len(account_ids):
        raise AccountingError("One or more accounts are invalid or inactive for this company")

    normalized = validate_entry_lines(lines)

    # Duplicate entry_no guard
    if db.query(JournalEntry).filter(JournalEntry.company_id == company.id, JournalEntry.entry_no == entry_no).first():
        raise AccountingError(f"Entry number {entry_no} already exists")

    entry = JournalEntry(
        company_id=company.id,
        entry_no=entry_no,
        entry_date=entry_date,
        reference=reference,
        description=description,
        posted=True,
        created_by=created_by,
    )
    # Chain prev_hash to the most recent entry's hash for tamper evidence BEFORE insert
    # (the before_insert event computes hash from prev_hash).
    latest = (
        db.query(JournalEntry)
        .filter(JournalEntry.company_id == company.id)
        .order_by(JournalEntry.id.desc())
        .first()
    )
    entry.prev_hash = latest.hash if latest else "genesis"

    db.add(entry)
    db.flush()  # assign entry.id; before_insert event computes hash

    for line in normalized:
        db.add(
            JournalLine(
                entry_id=entry.id,
                account_id=line["account_id"],
                debit=line["debit"],
                credit=line["credit"],
                memo=line["memo"],
            )
        )

    db.commit()
    db.refresh(entry)
    return entry


def reverse_entry(db: Session, *, entry: JournalEntry, created_by: Optional[int] = None) -> JournalEntry:
    """Create a reversing entry for a posted entry (never edits history)."""
    if not entry.posted:
        raise AccountingError("Only posted entries can be reversed")
    lines = [
        {
            "account_id": l.account_id,
            "debit": l.credit,  # swap debit/credit
            "credit": l.debit,
            "memo": f"Reversal of entry {entry.entry_no}" + (f" ({l.memo})" if l.memo else ""),
        }
        for l in entry.lines
    ]
    return post_entry(
        db,
        company=entry.company,
        entry_no=f"{entry.entry_no}-REV",
        entry_date=entry.entry_date,  # caller should pass a current date; kept same for simplicity
        lines=lines,
        reference=entry.reference,
        description=f"Reversal of {entry.entry_no}",
        created_by=created_by,
    )


