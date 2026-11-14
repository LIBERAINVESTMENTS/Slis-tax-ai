"""Chart of accounts endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ai_accountant_backend.db import get_db
from ai_accountant_backend.deps import get_current_user, require_role
from ai_accountant_backend.models import Account, Company
from ai_accountant_backend.schemas import AccountCreate, AccountOut

router = APIRouter(tags=["accounts"])


def _require_company(company_id: int, user, db: Session) -> Company:
    company = db.query(Company).filter(Company.id == company_id, Company.tenant_id == user.tenant_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/companies/{company_id}/accounts", response_model=list[AccountOut])
def list_accounts(company_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    _require_company(company_id, user, db)
    rows = db.query(Account).filter(Account.company_id == company_id).order_by(Account.code).all()
    return [
        AccountOut(
            id=a.id,
            code=a.code,
            name=a.name,
            type=a.type,
            subtype=a.subtype,
            currency=a.currency,
            is_active=a.is_active,
            description=a.description,
        )
        for a in rows
    ]


@router.post("/companies/{company_id}/accounts", response_model=AccountOut, status_code=201)
def create_account(
    company_id: int,
    payload: AccountCreate,
    user=Depends(require_role("owner", "admin")),
    db: Session = Depends(get_db),
):
    _require_company(company_id, user, db)
    if db.query(Account).filter(Account.company_id == company_id, Account.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Account code already exists")
    account = Account(
        company_id=company_id,
        code=payload.code,
        name=payload.name,
        type=payload.type,
        subtype=payload.subtype,
        currency=payload.currency,
        description=payload.description,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return AccountOut(
        id=account.id,
        code=account.code,
        name=account.name,
        type=account.type,
        subtype=account.subtype,
        currency=account.currency,
        is_active=account.is_active,
        description=account.description,
    )


