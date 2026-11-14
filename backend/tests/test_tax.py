"""Tests for the Suriname tax engine (deterministic, verified rules only)."""
from __future__ import annotations

from decimal import Decimal

from ai_accountant_backend.tax.engine import (
    compute_corporate_income_tax,
    compute_personal_income_tax,
    compute_vat,
    compute_wage_tax,
    TaxUnverifiedError,
)


def test_corporate_income_tax_36_percent(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_corporate_income_tax(db, Decimal("100000"), country="SR")
    assert result["tax_owed"] == "36000.00"
    assert result["rate"] == "36"


def test_vat_standard_10_percent(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_vat(db, Decimal("1000"), rate_category="standard", country="SR")
    assert result["vat"] == "100.00"
    assert result["total"] == "1100.00"
    assert result["rate"] == "10"


def test_personal_income_tax_verified_bracket(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_personal_income_tax(db, Decimal("140000"), country="SR")
    # 0% on first 108,000 + 8% on 32,000 = 2,560
    assert result["tax_owed"] == "2560.00"


def test_personal_income_tax_above_verified_unverified(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    try:
        compute_personal_income_tax(db, Decimal("200000"), country="SR")
        assert False, "Should have raised TaxUnverifiedError"
    except TaxUnverifiedError:
        pass


def test_wage_tax_verified_bracket(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_wage_tax(db, Decimal("150000"), country="SR")
    # taxable = 150,000 - 108,000 = 42,000; 8% = 3,360
    assert result["tax_owed"] == "3360.00"


def test_wage_tax_above_verified_unverified(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    try:
        compute_wage_tax(db, Decimal("200000"), country="SR")
        assert False, "Should have raised TaxUnverifiedError"
    except TaxUnverifiedError:
        pass

