"""Financial reporting API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ai_accountant_backend.db import get_db
from ai_accountant_backend.deps import get_current_user
from ai_accountant_backend.models import Company, User
from ai_accountant_backend.reporting.engine import (
    balance_sheet,
    cash_flow_statement,
    financial_statements,
    income_statement,
)

router = APIRouter(tags=["reports"])


def _require_company(company_id: int, user: User, db: Session) -> Company:
    company = (
        db.query(Company)
        .filter(Company.id == company_id, Company.tenant_id == user.tenant_id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/companies/{company_id}/reports/income-statement")
def get_income_statement(
    company_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    period_start: str | None = None,
    period_end: str | None = None,
):
    company = _require_company(company_id, user, db)
    return income_statement(db, company, period_start, period_end)


@router.get("/companies/{company_id}/reports/balance-sheet")
def get_balance_sheet(
    company_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = _require_company(company_id, user, db)
    return balance_sheet(db, company)


@router.get("/companies/{company_id}/reports/cash-flow")
def get_cash_flow(
    company_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = _require_company(company_id, user, db)
    return cash_flow_statement(db, company)


@router.get("/companies/{company_id}/reports")
def get_financial_statements(
    company_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = _require_company(company_id, user, db)
    return financial_statements(db, company)
