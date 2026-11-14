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

from ai_accountant_backend.models import Account, Company, JournalEntry, JournalLine


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


def _compute_entry_hash(prev_hash: str, entry: JournalEntry, lines: list[JournalLine]) -> str:
    """Compute the tamper-evidence hash covering the full entry payload."""
    import hashlib
    import json

    payload = {
        "entry_no": entry.entry_no,
        "entry_date": entry.entry_date,
        "reference": entry.reference,
        "description": entry.description,
        "lines": [
            {
                "account_id": l.account_id,
                "debit": l.debit,
                "credit": l.credit,
                "memo": l.memo,
            }
            for l in lines
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256((prev_hash or "genesis").encode() + canonical).hexdigest()


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

    # Chain prev_hash to the most recent entry's hash for tamper evidence.
    latest = (
        db.query(JournalEntry)
        .filter(JournalEntry.company_id == company.id)
        .order_by(JournalEntry.id.desc())
        .first()
    )
    prev_hash = latest.hash if latest else "genesis"

    # Build line objects first so the tamper-evidence hash covers the complete payload.
    line_objs = [
        JournalLine(
            account_id=line["account_id"],
            debit=line["debit"],
            credit=line["credit"],
            memo=line["memo"],
        )
        for line in normalized
    ]

    entry = JournalEntry(
        company_id=company.id,
        entry_no=entry_no,
        entry_date=entry_date,
        reference=reference,
        description=description,
        posted=True,
        created_by=created_by,
        prev_hash=prev_hash,
    )
    entry.hash = _compute_entry_hash(prev_hash, entry, line_objs)
    entry.lines = line_objs

    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def reverse_entry(
    db: Session,
    *,
    entry: JournalEntry,
    created_by: Optional[int] = None,
    reversal_date: Optional[str] = None,
) -> JournalEntry:
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
        entry_date=reversal_date or entry.entry_date,
        lines=lines,
        reference=entry.reference,
        description=f"Reversal of {entry.entry_no}",
        created_by=created_by,
    )


