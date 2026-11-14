"""Multi-country tax engine — deterministic, data-driven, source-verified.

Design principles (industry standard):
- Every jurisdiction's rates/brackets live as *data* (JURISDICTIONS below), so adding a new
  country means adding data, not writing new code.
- Every rule carries source_url, effective_date, and verified flag. Unverified rules raise
  TaxUnverifiedError and are never used for live calculation.
- All money math uses Decimal; LLMs never perform arithmetic.

Jurisdictions implemented:
- SR — Suriname (SRD): corporate 36%, VAT 10/5/25/0%, personal income progressive, dividend 25%
- NL — Netherlands (EUR): corporate 19%/25.8%, VAT 21/9/0%, Box 1 35.82/37.48/49.50%, dividend 15%
- US — United States (USD): corporate 21%, federal income 10–37%, FICA 7.65%, no federal VAT

Research basis: see TAX_RESEARCH.md.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlalchemy.orm import Session

from ai_accountant_backend.models import TaxRule


class TaxUnverifiedError(Exception):
    """Raised when a tax rule needed for calculation is not yet verified."""


class UnsupportedCountryError(Exception):
    """Raised when a country has no registered tax jurisdiction."""


def _money(value) -> Decimal:
    from decimal import InvalidOperation

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"Invalid money value: {value!r}") from exc


def _q(value: Decimal) -> Decimal:
    """Quantize to 2 decimal places (cents)."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Jurisdiction data (rates + brackets, each with source and verification info)
# ---------------------------------------------------------------------------

JURISDICTIONS: dict[str, dict] = {
    "SR": {
        "name": "Suriname",
        "currency": "SRD",
        "corporate": {
            "brackets": [(None, "36", True)],  # (ceiling_inclusive, rate_percent, verified); None = open top bracket
            "source_url": "https://eitisuriname.gov.sr/en/eiti-suriname-reports/eiti-suriname-report-2016/payments-to-the-ministry-of-finance-directorate-direct-and-indirect-taxes/",
            "effective_date": "2024-01-01",
            "verified": True,
        },
        "vat": {
            "standard": ("10", True, "https://trykintsugi.com/sales-tax-guides/latam/suriname", "2023-01-01"),
            "reduced": ("5", True, "https://vsbstia.org/", "2023-01-01"),
            "luxury": ("25", True, "https://vsbstia.org/", "2023-01-01"),
            "zero": ("0", True, "https://trykintsugi.com/sales-tax-guides/latam/suriname", "2023-01-01"),
            "registration_threshold": "1000000",
        },
        "personal": {
            "brackets": [
                # (ceiling_inclusive, rate_percent, verified)
                ("108000", "0", True),
                ("150000", "8", True),
                ("192000", "18", True),
                (None, "35", False),  # top bracket unverified
            ],
            "source_url": "https://vsbstia.org/",
            "effective_date": "2024-01-01",
            "verified": True,
        },
        "dividend_withholding": ("25", True, "https://eitisuriname.gov.sr/"),
    },
    "NL": {
        "name": "Netherlands",
        "currency": "EUR",
        "corporate": {
            "brackets": [
                ("200000", "19", True),
                (None, "25.8", True),
            ],
            "source_url": "https://www.kvk.nl/geldzaken/belastingtarieven-2025/",
            "effective_date": "2025-01-01",
            "verified": True,
        },
        "vat": {
            "standard": ("21", True, "https://www.government.nl/themes/taxes-benefits-and-allowances/vat/vat-rates-and-exemptions", "2025-01-01"),
            "reduced": ("9", True, "https://www.government.nl/themes/taxes-benefits-and-allowances/vat/vat-rates-and-exemptions", "2025-01-01"),
            "zero": ("0", True, "https://www.government.nl/themes/taxes-benefits-and-allowances/vat/vat-rates-and-exemptions", "2025-01-01"),
        },
        "personal": {
            "brackets": [
                ("38441", "35.82", True),
                ("76817", "37.48", True),
                (None, "49.50", True),
            ],
            "source_url": "https://www.dezaak.nl/financien/belastingen/overzicht-belastingtarieven-en-belastingschijven",
            "effective_date": "2025-01-01",
            "verified": True,
        },
        "dividend_withholding": ("15", True, "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/winst/dividendbelasting/als_u_dividend_uitkeert/"),
    },
    "US": {
        "name": "United States",
        "currency": "USD",
        "corporate": {
            "brackets": [(None, "21", True)],
            "source_url": "https://www.irs.gov/",
            "effective_date": "2018-01-01",
            "verified": True,
        },
        "vat": None,  # No federal VAT/sales tax in the US
        "personal": {
            # filing_status -> brackets
            "single": [
                ("11925", "10", True),
                ("48475", "12", True),
                ("103350", "22", True),
                ("197300", "24", True),
                ("250525", "32", True),
                ("626350", "35", True),
                (None, "37", True),
            ],
            "married_joint": [
                ("23850", "10", True),
                ("96950", "12", True),
                ("206700", "22", True),
                ("394600", "24", True),
                ("501050", "32", True),
                ("751600", "35", True),
                (None, "37", True),
            ],
            "standard_deduction": {"single": "15000", "married_joint": "30000"},
            "source_url": "https://taxsummaries.pwc.com/United-States/Individual/Taxes-on-personal-income",
            "effective_date": "2025-01-01",
            "verified": True,
        },
        "fica": {
            "social_security_rate": "6.2",
            "social_security_wage_base": "176100",
            "medicare_rate": "1.45",
            "source_url": "https://www.hrblock.com/tax-center/filing/fica-taxes/",
            "effective_date": "2025-01-01",
            "verified": True,
        },
    },
}


def get_jurisdiction(country: str) -> dict:
    jur = JURISDICTIONS.get(country.upper())
    if jur is None:
        raise UnsupportedCountryError(f"No tax jurisdiction registered for country '{country}'")
    return jur


def _get_rule(db: Session, country: str, tax_type: str, name: str) -> Optional[TaxRule]:
    return (
        db.query(TaxRule)
        .filter(
            TaxRule.country == country.upper(),
            TaxRule.tax_type == tax_type,
            TaxRule.name == name,
            TaxRule.is_active == True,  # noqa: E712
        )
        .order_by(TaxRule.effective_date.desc().nullslast())
        .first()
    )


def _require_verified(rule: Optional[TaxRule], context: str) -> TaxRule:
    if rule is None:
        raise TaxUnverifiedError(f"No tax rule found for {context}")
    if rule.verification_status != "verified":
        raise TaxUnverifiedError(
            f"Tax rule '{rule.name}' ({context}) is not verified "
            f"(status={rule.verification_status}); cannot use for live calculation. "
            f"Verify against {rule.source_url or 'official source'} before use."
        )
    return rule


def _progressive_tax(amount: Decimal, brackets: list) -> tuple[Decimal, list]:
    """Apply progressive brackets. Each bracket is (ceiling, rate, verified); None ceiling = open top.

    Returns (total_tax, breakdown). Raises TaxUnverifiedError if an unverified bracket is hit.
    """
    tax = Decimal("0")
    lower = Decimal("0")
    breakdown = []
    for ceiling, rate_s, verified in brackets:
        rate = _money(rate_s)
        if ceiling is None:
            if amount > lower:
                if not verified:
                    raise TaxUnverifiedError(
                        f"Top tax bracket rate ({rate_s}%) and ceiling are unverified; "
                        "cannot compute live tax above the last verified bracket."
                    )
                chunk = amount - lower
                tax += chunk * rate / Decimal("100")
                breakdown.append({"from": str(lower), "to": None, "rate": rate_s,
                                  "amount": str(chunk), "tax": str(_q(chunk * rate / Decimal("100"))),
                                  "verified": verified})
            break
        ceiling_d = _money(ceiling)
        if amount <= lower:
            break
        chunk = min(amount, ceiling_d) - lower
        if chunk > 0:
            tax += chunk * rate / Decimal("100")
            breakdown.append({"from": str(lower), "to": str(ceiling_d), "rate": rate_s,
                              "amount": str(chunk), "tax": str(_q(chunk * rate / Decimal("100"))),
                              "verified": verified})
        lower = ceiling_d
        if amount <= ceiling_d:
            break
    return tax, breakdown


# ---------------------------------------------------------------------------
# Corporate income tax
# ---------------------------------------------------------------------------
def compute_corporate_income_tax(db: Session, taxable_profit, country: str = "SR") -> dict:
    taxable_profit = _money(taxable_profit)
    jur = get_jurisdiction(country)
    corp = jur["corporate"]
    tax, breakdown = _progressive_tax(taxable_profit, corp["brackets"])
    return {
        "country": country.upper(),
        "country_name": jur["name"],
        "currency": jur["currency"],
        "tax_type": "corporate_income_tax",
        "taxable_amount": str(_q(taxable_profit)),
        "tax_owed": str(_q(tax)),
        "breakdown": breakdown,
        "source_url": corp["source_url"],
        "effective_date": corp["effective_date"],
        "verified": corp["verified"],
    }


# ---------------------------------------------------------------------------
# VAT / sales tax
# ---------------------------------------------------------------------------
def compute_vat(db: Session, amount, rate_category: str = "standard", country: str = "SR") -> dict:
    amount = _money(amount)
    jur = get_jurisdiction(country)
    if jur["vat"] is None:
        raise TaxUnverifiedError(
            f"{jur['name']} has no federal VAT/sales tax (state-level only in the US)."
        )
    if rate_category not in jur["vat"]:
        raise ValueError(f"Unknown VAT rate category '{rate_category}' for {country}")
    rate_s, verified, source, effective = jur["vat"][rate_category]
    if not verified:
        raise TaxUnverifiedError(f"VAT rate category '{rate_category}' is unverified for {country}")
    rate = _money(rate_s)
    vat = _q(amount * rate / Decimal("100"))
    result = {
        "country": country.upper(),
        "country_name": jur["name"],
        "currency": jur["currency"],
        "tax_type": "vat",
        "amount": str(_q(amount)),
        "rate_category": rate_category,
        "rate": str(rate),
        "vat": str(vat),
        "total": str(_q(amount + vat)),
        "source_url": source,
        "effective_date": effective,
        "verified": verified,
    }
    if "registration_threshold" in jur["vat"]:
        result["registration_threshold"] = jur["vat"]["registration_threshold"]
    return result


# ---------------------------------------------------------------------------
# Personal income tax
# ---------------------------------------------------------------------------
def compute_personal_income_tax(
    db: Session, net_income, country: str = "SR", filing_status: str = "single"
) -> dict:
    net_income = _money(net_income)
    jur = get_jurisdiction(country)
    personal = jur["personal"]

    if country.upper() == "US":
        # US uses filing status + standard deduction before brackets
        status_brackets = personal.get(filing_status)
        if status_brackets is None:
            raise ValueError(f"Unknown filing status '{filing_status}' for US")
        deduction = _money(personal["standard_deduction"][filing_status])
        taxable = net_income - deduction
        if taxable < 0:
            taxable = Decimal("0")
        tax, breakdown = _progressive_tax(taxable, status_brackets)
        return {
            "country": "US",
            "country_name": jur["name"],
            "currency": jur["currency"],
            "tax_type": "personal_income_tax",
            "filing_status": filing_status,
            "gross_income": str(_q(net_income)),
            "standard_deduction": str(_q(deduction)),
            "taxable_income": str(_q(taxable)),
            "tax_owed": str(_q(tax)),
            "breakdown": breakdown,
            "source_url": personal["source_url"],
            "effective_date": personal["effective_date"],
            "verified": personal["verified"],
        }

    # SR / NL: direct progressive brackets on net income
    tax, breakdown = _progressive_tax(net_income, personal["brackets"])
    return {
        "country": country.upper(),
        "country_name": jur["name"],
        "currency": jur["currency"],
        "tax_type": "personal_income_tax",
        "taxable_amount": str(_q(net_income)),
        "tax_owed": str(_q(tax)),
        "breakdown": breakdown,
        "source_url": personal["source_url"],
        "effective_date": personal["effective_date"],
        "verified": personal["verified"],
    }


# ---------------------------------------------------------------------------
# Wage / payroll tax
# ---------------------------------------------------------------------------
def compute_wage_tax(db: Session, annual_salary, country: str = "SR") -> dict:
    annual_salary = _money(annual_salary)
    jur = get_jurisdiction(country)

    if country.upper() == "US":
        fica = jur["fica"]
        ss_rate = _money(fica["social_security_rate"])
        wage_base = _money(fica["social_security_wage_base"])
        med_rate = _money(fica["medicare_rate"])
        ss_wages = min(annual_salary, wage_base)
        ss_tax = _q(ss_wages * ss_rate / Decimal("100"))
        med_tax = _q(annual_salary * med_rate / Decimal("100"))
        total = _q(ss_tax + med_tax)
        return {
            "country": "US",
            "country_name": jur["name"],
            "currency": jur["currency"],
            "tax_type": "fica_payroll_tax",
            "annual_salary": str(_q(annual_salary)),
            "social_security_tax": str(ss_tax),
            "medicare_tax": str(med_tax),
            "tax_owed": str(total),
            "note": "Employee share (6.2% SS up to wage base + 1.45% Medicare). Employer matches.",
            "source_url": fica["source_url"],
            "effective_date": fica["effective_date"],
            "verified": fica["verified"],
        }

    # SR / NL: wage tax follows personal income brackets
    result = compute_personal_income_tax(db, annual_salary, country=country)
    result["tax_type"] = "wage_tax"
    result["annual_salary"] = result.pop("taxable_amount", str(_q(annual_salary)))
    return result


# ---------------------------------------------------------------------------
# Withholding tax (dividend)
# ---------------------------------------------------------------------------
def compute_withholding_tax(
    db: Session, amount, withholding_type: str = "dividend", country: str = "SR"
) -> dict:
    amount = _money(amount)
    jur = get_jurisdiction(country)
    if withholding_type != "dividend":
        raise ValueError(f"Unknown withholding type: {withholding_type}")
    rate_s, verified, source = jur["dividend_withholding"]
    if not verified:
        raise TaxUnverifiedError(
            f"Dividend withholding rate for {jur['name']} is unverified; not for live use."
        )
    rate = _money(rate_s)
    tax = _q(amount * rate / Decimal("100"))
    return {
        "country": country.upper(),
        "country_name": jur["name"],
        "currency": jur["currency"],
        "tax_type": "withholding_tax",
        "withholding_type": withholding_type,
        "amount": str(_q(amount)),
        "rate": str(rate),
        "tax_owed": str(tax),
        "source_url": source,
        "verified": verified,
    }


def list_supported_countries() -> list[dict]:
    return [
        {"code": code, "name": jur["name"], "currency": jur["currency"],
         "has_vat": jur["vat"] is not None}
        for code, jur in sorted(JURISDICTIONS.items())
    ]


def list_unverified_rules(db: Session, country: str = "SR") -> list[dict]:
    """Return tax rules that need verification before live use."""
    rows = (
        db.query(TaxRule)
        .filter(
            TaxRule.country == country.upper(),
            TaxRule.verification_status == "pending",
            TaxRule.is_active == True,  # noqa: E712
        )
        .all()
    )
    return [
        {
            "id": r.id,
            "tax_type": r.tax_type,
            "name": r.name,
            "rate": r.rate,
            "source_url": r.source_url,
            "effective_date": r.effective_date,
            "last_verified_date": r.last_verified_date,
        }
        for r in rows
    ]
