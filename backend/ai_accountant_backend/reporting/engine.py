"""Financial reporting engine — deterministic statements computed from journal entries.

Produces industry-standard financial statements:
- Income statement (Profit & Loss): revenue − expenses
- Balance sheet: assets = liabilities + equity
- Cash flow statement: change in cash/bank accounts

All calculations are Decimal-safe and derived directly from posted journal lines;
nothing is estimated or fetched from an LLM.
"""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from ai_accountant_backend.models import Account, Company, JournalEntry, JournalLine

_NORMAL_DEBIT = {"asset", "expense"}  # these accounts increase with debits
_NORMAL_CREDIT = {"liability", "equity", "revenue"}  # increase with credits


def _money(value) -> Decimal:
    from decimal import InvalidOperation

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


def _account_balances(db: Session, company: Company) -> dict[int, Decimal]:
    """Net signed balance per account: debits − credits (positive = debit balance)."""
    rows = (
        db.query(Account.id, Account.type, JournalLine.debit, JournalLine.credit)
        .join(JournalLine, JournalLine.account_id == Account.id)
        .join(JournalEntry, JournalEntry.id == JournalLine.entry_id)
        .filter(JournalEntry.company_id == company.id, JournalEntry.posted == True)  # noqa: E712
        .all()
    )
    balances: dict[int, Decimal] = {}
    for account_id, _type, debit, credit in rows:
        bal = balances.get(account_id, Decimal("0"))
        bal += _money(debit) - _money(credit)
        balances[account_id] = bal
    return balances


def _net_balance(account: Account, signed: Decimal) -> Decimal:
    """Return the natural (positive) balance based on the account's normal side."""
    if account.type in _NORMAL_CREDIT:
        return -signed  # credit-normal
    return signed  # debit-normal


def _group_balance(db: Session, company: Company, account_type: str) -> Decimal:
    accounts = db.query(Account).filter(Account.company_id == company.id, Account.type == account_type).all()
    balances = _account_balances(db, company)
    total = Decimal("0")
    for acc in accounts:
        signed = balances.get(acc.id, Decimal("0"))
        total += _net_balance(acc, signed)
    return total


def income_statement(db: Session, company: Company, period_start: str | None = None, period_end: str | None = None) -> dict:
    """Profit & Loss: revenues − expenses."""
    q = (
        db.query(JournalLine, Account)
        .join(JournalEntry, JournalEntry.id == JournalLine.entry_id)
        .join(Account, Account.id == JournalLine.account_id)
        .filter(JournalEntry.company_id == company.id, JournalEntry.posted == True)  # noqa: E712
    )
    if period_start:
        q = q.filter(JournalEntry.entry_date >= period_start)
    if period_end:
        q = q.filter(JournalEntry.entry_date <= period_end)

    revenue = Decimal("0")
    expenses = Decimal("0")
    revenue_detail: dict[str, Decimal] = {}
    expense_detail: dict[str, Decimal] = {}
    for line, acc in q.all():
        # Natural balance: revenue increases with credit, expense with debit.
        amount = _money(line.credit) - _money(line.debit)
        if acc.type == "revenue":
            revenue += amount
            revenue_detail[acc.name] = revenue_detail.get(acc.name, Decimal("0")) + amount
        elif acc.type == "expense":
            # expenses are debit-normal: debit − credit
            amount = _money(line.debit) - _money(line.credit)
            expenses += amount
            expense_detail[acc.name] = expense_detail.get(acc.name, Decimal("0")) + amount

    net_income = revenue - expenses
    return {
        "company": company.name,
        "currency": company.currency,
        "statement": "income_statement",
        "period_start": period_start,
        "period_end": period_end,
        "revenue": str(revenue),
        "expenses": str(expenses),
        "net_income": str(net_income),
        "revenue_detail": {k: str(v) for k, v in revenue_detail.items()},
        "expense_detail": {k: str(v) for k, v in expense_detail.items()},
    }


def balance_sheet(db: Session, company: Company) -> dict:
    """Balance sheet: assets = liabilities + equity."""
    assets = _group_balance(db, company, "asset")
    liabilities = _group_balance(db, company, "liability")
    equity = _group_balance(db, company, "equity")
    # Include retained earnings (net income) in equity for the demo.
    net_income = Decimal(income_statement(db, company)["net_income"])
    total_equity = equity + net_income
    return {
        "company": company.name,
        "currency": company.currency,
        "statement": "balance_sheet",
        "assets": str(assets),
        "liabilities": str(liabilities),
        "equity": str(total_equity),
        "liabilities_plus_equity": str(liabilities + total_equity),
        "balanced": (assets - (liabilities + total_equity)) == Decimal("0"),
    }


def cash_flow_statement(db: Session, company: Company) -> dict:
    """Cash flow: net change in cash/bank accounts over the period."""
    cash_accounts = (
        db.query(Account)
        .filter(
            Account.company_id == company.id,
            Account.type == "asset",
            Account.subtype.in_(["cash", "bank"]),
        )
        .all()
    )
    balances = _account_balances(db, company)
    cash_in = Decimal("0")
    cash_out = Decimal("0")
    opening = Decimal("0")
    closing = Decimal("0")
    for acc in cash_accounts:
        signed = balances.get(acc.id, Decimal("0"))
        # debit-normal: positive signed balance = cash on hand
        closing += signed
    # For a simple cash flow view, treat net change in cash accounts.
    net_change = closing - opening
    return {
        "company": company.name,
        "currency": company.currency,
        "statement": "cash_flow",
        "cash_in": str(cash_in),
        "cash_out": str(cash_out),
        "net_cash_flow": str(net_change),
        "cash_balance": str(closing),
    }


def financial_statements(db: Session, company: Company) -> dict:
    """Bundle all three statements."""
    return {
        "income_statement": income_statement(db, company),
        "balance_sheet": balance_sheet(db, company),
        "cash_flow": cash_flow_statement(db, company),
    }
