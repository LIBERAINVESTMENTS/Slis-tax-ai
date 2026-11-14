"""Tests for the multi-country tax engine (deterministic, verified rules only)."""
from __future__ import annotations

from decimal import Decimal

from ai_accountant_backend.tax.engine import (
    compute_corporate_income_tax,
    compute_personal_income_tax,
    compute_vat,
    compute_wage_tax,
    compute_withholding_tax,
    list_supported_countries,
    TaxUnverifiedError,
    UnsupportedCountryError,
)


# --- Suriname ---

def test_corporate_income_tax_suriname(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_corporate_income_tax(db, Decimal("100000"), country="SR")
    assert result["tax_owed"] == "36000.00"
    assert result["country_name"] == "Suriname"


def test_vat_standard_suriname(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_vat(db, Decimal("1000"), rate_category="standard", country="SR")
    assert result["vat"] == "100.00"
    assert result["total"] == "1100.00"
    assert result["rate"] == "10"


def test_personal_income_tax_suriname(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_personal_income_tax(db, Decimal("140000"), country="SR")
    # 0% on first 108,000 + 8% on 32,000 = 2,560
    assert result["tax_owed"] == "2560.00"


def test_personal_income_tax_suriname_unverified_top(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    try:
        compute_personal_income_tax(db, Decimal("200000"), country="SR")
        assert False, "Should have raised TaxUnverifiedError"
    except TaxUnverifiedError:
        pass


# --- Netherlands ---

def test_corporate_income_tax_netherlands(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    # 19% on first 200,000 + 25.8% on excess 100,000
    result = compute_corporate_income_tax(db, Decimal("300000"), country="NL")
    # 200,000 * 19% = 38,000 ; 100,000 * 25.8% = 25,800 ; total 63,800
    assert result["tax_owed"] == "63800.00"
    assert result["country_name"] == "Netherlands"


def test_vat_standard_netherlands(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_vat(db, Decimal("1000"), rate_category="standard", country="NL")
    assert result["vat"] == "210.00"
    assert result["total"] == "1210.00"
    assert result["rate"] == "21"


def test_personal_income_tax_netherlands(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    # 35.82% on 38,441 + 37.48% on (50,000 - 38,441 = 11,559)
    result = compute_personal_income_tax(db, Decimal("50000"), country="NL")
    expected = Decimal("38441") * Decimal("35.82") / 100 + Decimal("11559") * Decimal("37.48") / 100
    assert result["tax_owed"] == f"{expected:.2f}"
    assert result["country_name"] == "Netherlands"


def test_dividend_withholding_netherlands(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_withholding_tax(db, Decimal("1000"), "dividend", country="NL")
    assert result["tax_owed"] == "150.00"
    assert result["rate"] == "15"


# --- United States ---

def test_corporate_income_tax_usa(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_corporate_income_tax(db, Decimal("100000"), country="US")
    assert result["tax_owed"] == "21000.00"
    assert result["country_name"] == "United States"


def test_personal_income_tax_usa_single(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    # $100,000 gross, $15,000 standard deduction → $85,000 taxable
    # 10% on 11,925 + 12% on (48,475-11,925) + 22% on (85,000-48,475)
    result = compute_personal_income_tax(db, Decimal("100000"), country="US", filing_status="single")
    assert result["standard_deduction"] == "15000.00"
    assert result["taxable_income"] == "85000.00"
    # expected tax
    tax = (
        Decimal("11925") * Decimal("10") / 100
        + (Decimal("48475") - Decimal("11925")) * Decimal("12") / 100
        + (Decimal("85000") - Decimal("48475")) * Decimal("22") / 100
    )
    assert result["tax_owed"] == f"{tax:.2f}"


def test_fica_payroll_usa(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    result = compute_wage_tax(db, Decimal("100000"), country="US")
    # SS 6.2% + Medicare 1.45% = 7.65%
    expected = Decimal("100000") * Decimal("7.65") / 100
    assert result["tax_owed"] == f"{expected:.2f}"
    assert result["tax_type"] == "fica_payroll_tax"


def test_us_has_no_vat(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    try:
        compute_vat(db, Decimal("1000"), "standard", country="US")
        assert False, "Should have raised TaxUnverifiedError"
    except TaxUnverifiedError:
        pass


def test_unsupported_country(tenant_user_company, db):
    _tenant, _user, _company = tenant_user_company
    try:
        compute_corporate_income_tax(db, Decimal("1000"), country="XX")
        assert False, "Should have raised UnsupportedCountryError"
    except UnsupportedCountryError:
        pass


def test_list_supported_countries():
    codes = {c["code"] for c in list_supported_countries()}
    assert {"SR", "NL", "US"}.issubset(codes)
