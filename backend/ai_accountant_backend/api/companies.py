"""Company management endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ai_accountant_backend.db import get_db, set_current_company
from ai_accountant_backend.deps import get_current_user, require_role
from ai_accountant_backend.models import Company, User
from ai_accountant_backend.schemas import CompanyCreate, CompanyOut, CompanyUpdate

router = APIRouter(tags=["companies"])


def _to_out(company: Company) -> CompanyOut:
    return CompanyOut(
        id=company.id,
        name=company.name,
        slug=company.slug,
        country=company.country,
        currency=company.currency,
        fiscal_year_start_month=company.fiscal_year_start_month,
        tax_regime=company.tax_regime,
        period_lock_date=company.period_lock_date,
        is_active=company.is_active,
    )


@router.get("/companies", response_model=list[CompanyOut])
def list_companies(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Company).filter(Company.tenant_id == user.tenant_id).all()
    return [_to_out(c) for c in rows]


@router.post("/companies", response_model=CompanyOut, status_code=201)
def create_company(
    payload: CompanyCreate,
    user: User = Depends(require_role("owner", "admin")),
    db: Session = Depends(get_db),
):
    if db.query(Company).filter(Company.slug == payload.slug, Company.tenant_id == user.tenant_id).first():
        raise HTTPException(status_code=400, detail="Company slug already exists")
    company = Company(
        tenant_id=user.tenant_id,
        name=payload.name,
        slug=payload.slug,
        country=payload.country,
        currency=payload.currency,
        fiscal_year_start_month=payload.fiscal_year_start_month,
        tax_regime=payload.tax_regime,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return _to_out(company)


@router.get("/companies/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id, Company.tenant_id == user.tenant_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return _to_out(company)


@router.patch("/companies/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: int,
    payload: CompanyUpdate,
    user: User = Depends(require_role("owner", "admin")),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id, Company.tenant_id == user.tenant_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return _to_out(company)


@router.post("/companies/{company_id}/select")
def select_company(
    company_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bind the current request/session to a company for business-accounting operations."""
    company = db.query(Company).filter(Company.id == company_id, Company.tenant_id == user.tenant_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    set_current_company(company_id)
    return {"company_id": company_id, "name": company.name}


