"""Journal entry endpoints backed by the double-entry accounting engine."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ai_accountant_backend.db import get_db
from ai_accountant_backend.deps import get_current_user, require_role
from ai_accountant_backend.models import Company, JournalEntry
from ai_accountant_backend.schemas import JournalEntryCreate, JournalEntryOut

router = APIRouter(tags=["journal"])

# Import engine lazily to avoid a circular import at module load (engine imports models).
from ai_accountant_backend.accounting.engine import AccountingError, post_entry, reverse_entry  # noqa: E402

@router.post("/companies/{company_id}/journal", response_model=JournalEntryOut, status_code=201)
def create_journal_entry(
    company_id: int,
    payload: JournalEntryCreate,
    user=Depends(require_role("owner", "admin", "employee")),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    try:
        entry = post_entry(
            db,
            company=company,
            entry_no=payload.entry_no,
            entry_date=payload.entry_date,
            lines=[l.model_dump() for l in payload.lines],
            reference=payload.reference,
            description=payload.description,
            created_by=user.id,
        )
    except AccountingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return JournalEntryOut(
        id=entry.id,
        entry_no=entry.entry_no,
        entry_date=entry.entry_date,
        posted=entry.posted,
        hash=entry.hash,
        prev_hash=entry.prev_hash,
    )


@router.post("/journal/{entry_id}/reverse", response_model=JournalEntryOut, status_code=201)
def reverse_journal_entry(
    entry_id: int,
    user=Depends(require_role("owner", "admin")),
    db: Session = Depends(get_db),
):
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    company = db.query(Company).filter(Company.id == entry.company_id).first()
    try:
        rev = reverse_entry(db, entry=entry, created_by=user.id)
    except AccountingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return JournalEntryOut(
        id=rev.id,
        entry_no=rev.entry_no,
        entry_date=rev.entry_date,
        posted=rev.posted,
        hash=rev.hash,
        prev_hash=rev.prev_hash,
    )


@router.get("/companies/{company_id}/journal/{entry_id}", response_model=JournalEntryOut)
def get_journal_entry(
    company_id: int,
    entry_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = (
        db.query(JournalEntry)
        .filter(JournalEntry.id == entry_id, JournalEntry.company_id == company_id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return JournalEntryOut(
        id=entry.id,
        entry_no=entry.entry_no,
        entry_date=entry.entry_date,
        posted=entry.posted,
        hash=entry.hash,
        prev_hash=entry.prev_hash,
    )


