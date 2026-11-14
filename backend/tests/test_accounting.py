"""Tests for the double-entry accounting engine."""
from __future__ import annotations

from ai_accountant_backend.accounting.engine import AccountingError, post_entry, reverse_entry
from ai_accountant_backend.models import Account


def _bank_and_revenue_ids(db, company):
    bank = db.query(Account).filter(Account.company_id == company.id, Account.code == "1100").first()
    revenue = db.query(Account).filter(Account.company_id == company.id, Account.code == "4100").first()
    return bank.id, revenue.id


def test_balanced_entry_posts(tenant_user_company, db):
    _tenant, user, company = tenant_user_company
    bank_id, rev_id = _bank_and_revenue_ids(db, company)
    lines = [
        {"account_id": bank_id, "debit": "1000.00", "credit": "0", "memo": "sale"},
        {"account_id": rev_id, "debit": "0", "credit": "1000.00", "memo": "revenue"},
    ]
    entry = post_entry(db, company=company, entry_no="JE-001", entry_date="2024-01-15", lines=lines, created_by=user.id)
    assert entry.posted is True
    assert entry.entry_no == "JE-001"
    assert entry.hash != "genesis"


def test_out_of_balance_entry_rejected(tenant_user_company, db):
    _tenant, _user, company = tenant_user_company
    bank_id, rev_id = _bank_and_revenue_ids(db, company)
    lines = [
        {"account_id": bank_id, "debit": "1000.00", "credit": "0"},
        {"account_id": rev_id, "debit": "0", "credit": "500.00"},
    ]
    try:
        post_entry(db, company=company, entry_no="JE-002", entry_date="2024-01-15", lines=lines)
        assert False, "Should have raised AccountingError"
    except AccountingError as exc:
        assert "out of balance" in str(exc)


def test_duplicate_entry_no_rejected(tenant_user_company, db):
    _tenant, _user, company = tenant_user_company
    bank_id, rev_id = _bank_and_revenue_ids(db, company)
    lines = [
        {"account_id": bank_id, "debit": "100.00", "credit": "0"},
        {"account_id": rev_id, "debit": "0", "credit": "100.00"},
    ]
    post_entry(db, company=company, entry_no="JE-DUP", entry_date="2024-01-15", lines=lines)
    try:
        post_entry(db, company=company, entry_no="JE-DUP", entry_date="2024-01-16", lines=lines)
        assert False, "Should have raised AccountingError"
    except AccountingError as exc:
        assert "already exists" in str(exc)


def test_reversal_swaps_debit_credit(tenant_user_company, db):
    _tenant, user, company = tenant_user_company
    bank_id, rev_id = _bank_and_revenue_ids(db, company)
    lines = [
        {"account_id": bank_id, "debit": "200.00", "credit": "0", "memo": "office"},
        {"account_id": rev_id, "debit": "0", "credit": "200.00", "memo": "cash"},
    ]
    entry = post_entry(db, company=company, entry_no="JE-REV", entry_date="2024-02-01", lines=lines, created_by=user.id)
    rev = reverse_entry(db, entry=entry, created_by=user.id)
    assert rev.lines[0].debit == "0" and rev.lines[0].credit == "200.00"
    assert rev.lines[1].debit == "200.00" and rev.lines[1].credit == "0"


def test_hash_covers_line_data(tenant_user_company, db):
    """The tamper-evidence hash must change when line amounts change."""
    _tenant, user, company = tenant_user_company
    bank_id, rev_id = _bank_and_revenue_ids(db, company)
    entry_a = post_entry(
        db,
        company=company,
        entry_no="JE-H1",
        entry_date="2024-03-01",
        lines=[
            {"account_id": bank_id, "debit": "100.00", "credit": "0"},
            {"account_id": rev_id, "debit": "0", "credit": "100.00"},
        ],
        created_by=user.id,
    )
    entry_b = post_entry(
        db,
        company=company,
        entry_no="JE-H2",
        entry_date="2024-03-01",
        lines=[
            {"account_id": bank_id, "debit": "999.00", "credit": "0"},
            {"account_id": rev_id, "debit": "0", "credit": "999.00"},
        ],
        created_by=user.id,
    )
    assert entry_a.hash != entry_b.hash
    # The second entry's prev_hash must chain to the first entry's hash.
    assert entry_b.prev_hash == entry_a.hash

