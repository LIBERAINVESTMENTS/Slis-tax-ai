"""Tax preparation & filing center — approval-gated, never claims submission without proof."""
from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai_accountant_backend.db import get_db
from ai_accountant_backend.deps import get_current_user, require_role
from ai_accountant_backend.models import Company, TaxReturn, User
from ai_accountant_backend.tax.engine import (
    compute_corporate_income_tax,
    compute_personal_income_tax,
    compute_vat,
    compute_wage_tax,
    compute_withholding_tax,
    TaxUnverifiedError,
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

router = APIRouter(tags=["tax"])


class CalculateRequest(BaseModel):
    tax_type: str  # corporate_income_tax | personal_income_tax | vat | wage_tax | withholding_tax
    amount: str  # Decimal string
    rate_category: str | None = None
    company_id: int | None = None


class TaxReturnCreate(BaseModel):
    company_id: int | None = None  # NULL = personal return
    country: str = "SR"
    tax_type: str
    period_start: str
    period_end: str
    filing_deadline: str | None = None


class TaxReturnOut(BaseModel):
    id: int
    company_id: int | None
    country: str
    tax_type: str
    period_start: str
    period_end: str
    taxable_amount: str
    tax_owed: str
    tax_paid: str
    status: str
    approved_by_user_id: int | None
    approved_at: str | None
    submission_proof: str | None
    submitted_at: str | None
    filing_deadline: str | None


def _to_out(ret: TaxReturn) -> TaxReturnOut:
    return TaxReturnOut(
        id=ret.id,
        company_id=ret.company_id,
        country=ret.country,
        tax_type=ret.tax_type,
        period_start=ret.period_start,
        period_end=ret.period_end,
        taxable_amount=ret.taxable_amount,
        tax_owed=ret.tax_owed,
        tax_paid=ret.tax_paid,
        status=ret.status,
        approved_by_user_id=ret.approved_by_user_id,
        approved_at=ret.approved_at,
        submission_proof=ret.submission_proof,
        submitted_at=ret.submitted_at,
        filing_deadline=ret.filing_deadline,
    )


@router.post("/tax/calculate")
def calculate_tax(
    payload: CalculateRequest,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Calculate tax obligations using verified rules (deterministic — never LLM arithmetic)."""
    try:
        if payload.tax_type == "corporate_income_tax":
            result = compute_corporate_income_tax(db, payload.amount, country="SR")
        elif payload.tax_type == "personal_income_tax":
            result = compute_personal_income_tax(db, payload.amount, country="SR")
        elif payload.tax_type == "vat":
            result = compute_vat(db, payload.amount, payload.rate_category or "standard", country="SR")
        elif payload.tax_type == "wage_tax":
            result = compute_wage_tax(db, payload.amount, country="SR")
        elif payload.tax_type == "withholding_tax":
            result = compute_withholding_tax(db, payload.amount, "dividend", country="SR")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported tax type: {payload.tax_type}")
    except TaxUnverifiedError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"calculation": result, "note": "Deterministic calculation from verified rules; LLM never does money math."}


@router.post("/tax/returns", response_model=TaxReturnOut, status_code=201)
def create_tax_return(
    payload: TaxReturnCreate,
    user=Depends(require_role("owner", "admin")),
    db=Depends(get_db),
):
    if payload.company_id:
        company = db.query(Company).filter(Company.id == payload.company_id, Company.tenant_id == user.tenant_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
    ret = TaxReturn(
        company_id=payload.company_id,
        user_id=user.id,
        country=payload.country,
        tax_type=payload.tax_type,
        period_start=payload.period_start,
        period_end=payload.period_end,
        filing_deadline=payload.filing_deadline,
        status="draft",
    )
    db.add(ret)
    db.commit()
    db.refresh(ret)
    return _to_out(ret)


@router.get("/tax/returns", response_model=list[TaxReturnOut])
def list_tax_returns(user=Depends(get_current_user), db=Depends(get_db)):
    rows = db.query(TaxReturn).filter(TaxReturn.user_id == user.id).order_by(TaxReturn.created_at.desc()).all()
    return [_to_out(r) for r in rows]


@router.post("/tax/returns/{return_id}/approve", response_model=TaxReturnOut)
def approve_tax_return(
    return_id: int,
    user=Depends(require_role("owner", "admin")),
    db=Depends(get_db),
):
    """User explicitly authorizes filing. Required before submission."""
    ret = db.query(TaxReturn).filter(TaxReturn.id == return_id, TaxReturn.user_id == user.id).first()
    if not ret:
        raise HTTPException(status_code=404, detail="Tax return not found")
    if ret.status != "draft":
        raise HTTPException(status_code=400, detail=f"Return already in status {ret.status}")
    ret.status = "approved"
    ret.approved_by_user_id = user.id
    ret.approved_at = _utcnow()
    db.commit()
    db.refresh(ret)
    return _to_out(ret)


@router.post("/tax/returns/{return_id}/submit", response_model=TaxReturnOut)
def submit_tax_return(
    return_id: int,
    user=Depends(require_role("owner", "admin")),
    db=Depends(get_db),
):
    """Submit only after explicit approval. Records proof — never claims submission without it."""
    ret = db.query(TaxReturn).filter(TaxReturn.id == return_id, TaxReturn.user_id == user.id).first()
    if not ret:
        raise HTTPException(status_code=404, detail="Tax return not found")
    if ret.status != "approved":
        raise HTTPException(status_code=400, detail="Return must be approved before submission")
    # Official e-filing integration is a stub: record that submission was prepared and authorized.
    # A real integration would call the government portal here and store the acknowledgment.
    ret.status = "submitted"
    ret.submitted_at = _utcnow()
    ret.submission_proof = f"authorized_by_user_{user.id}_at_{ret.submitted_at}; e-filing integration not live (stub)"
    db.commit()
    db.refresh(ret)
    return _to_out(ret)


@router.get("/tax/returns/{return_id}/download")
def download_tax_return(
    return_id: int,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Prepare a downloadable tax return document (PDF/DOCX placeholder)."""
    ret = db.query(TaxReturn).filter(TaxReturn.id == return_id, TaxReturn.user_id == user.id).first()
    if not ret:
        raise HTTPException(status_code=404, detail="Tax return not found")
    return {
        "return_id": ret.id,
        "tax_type": ret.tax_type,
        "period": f"{ret.period_start} to {ret.period_end}",
        "tax_owed": ret.tax_owed,
        "status": ret.status,
        "download_url": f"/api/tax/returns/{return_id}/document.pdf",  # generated on demand
        "note": "Document generation (PDF/DOCX) implemented on demand; requires reportlab/python-docx.",
    }

