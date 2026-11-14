"""Suriname tax engine — deterministic calculation functions.

All money math uses Decimal. Rates are loaded from the `tax_rules` table (which carries
source_url, effective_date, last_verified_date, verification_status). Rules flagged
verification_status='pending' are NOT used for live calculation; they return a warning
instead.

Research basis (see SURINAME_TAX_RESEARCH.md):
- Corporate income tax: 36% (Income Tax Act of 1922; EITI Suriname / Ministry of Finance) — VERIFIED
- VAT (BTW): 10% standard since 2023-01-01; 25% luxury; 5% reduced; 0% exports; threshold SRD 1,000,000 — VERIFIED (Kintsugi/VSB)
- Personal income tax: tax-free SRD 108,000; brackets from Staatsbesluit 11 Jan 2024 — brackets above SRD 192,000 PENDING
- Wage/payroll tax: tax-free SRD 108,000; 8% first bracket to SRD 42,000; top 35% — brackets between PENDING
- Withholding: dividend 25% (NV); treaty 7.5% PENDING

Never invent rates. When a bracket/rate is unverified, raise TaxUnverifiedError.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlalchemy.orm import Session

from ai_accountant_backend.models import TaxRule


class TaxUnverifiedError(Exception):
    """Raised when a tax rule needed for calculation is not yet verified."""


def _get_rule(db: Session, country: str, tax_type: str, name: str) -> Optional[TaxRule]:
    return (
        db.query(TaxRule)
        .filter(
            TaxRule.country == country,
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
# Corporate income tax — Suriname: 36% flat on taxable profit (VERIFIED)
# ---------------------------------------------------------------------------
def compute_corporate_income_tax(db: Session, taxable_profit: Decimal, country: str = "SR") -> dict:
    taxable_profit = _money(taxable_profit)
    rule = _require_verified(
        _get_rule(db, country, "corporate_income_tax", "corporate_income_tax_rate"),
        "corporate income tax",
    )
    rate = _money(rule.rate)
    tax = _q(taxable_profit * rate / Decimal("100"))
    return {
        "country": country,
        "tax_type": "corporate_income_tax",
        "taxable_amount": str(_q(taxable_profit)),
        "rate": str(rate),
        "tax_owed": str(tax),
        "rule_id": rule.id,
        "source_url": rule.source_url,
        "effective_date": rule.effective_date,
        "last_verified_date": rule.last_verified_date,
    }


# ---------------------------------------------------------------------------
# Personal income tax — Suriname: progressive brackets (Staatsbesluit 11 Jan 2024)
# Tax-free threshold SRD 108,000. Brackets above SRD 192,000 unverified.
# ---------------------------------------------------------------------------
# Bracket ceilings (SRD) and rates. Ceilings above 192,000 are marked unverified.
_PERSONAL_INCOME_BRACKETS = [
    # (ceiling_inclusive_srd, rate_percent, verified)
    (Decimal("108000"), Decimal("0"), True),
    (Decimal("150000"), Decimal("8"), True),
    (Decimal("192000"), Decimal("18"), True),
    # Top bracket ceiling not confirmed from gazette — rate 35% referenced but unverified
    (None, Decimal("35"), False),
]


def compute_personal_income_tax(
    db: Session, net_income: Decimal, country: str = "SR"
) -> dict:
    net_income = _money(net_income)
    tax = Decimal("0")
    lower = Decimal("0")
    breakdown = []
    for ceiling, rate, verified in _PERSONAL_INCOME_BRACKETS:
        if ceiling is None:
            # top open bracket
            if net_income > lower:
                if not verified:
                    raise TaxUnverifiedError(
                        "Top personal income tax bracket rate (35%) and ceiling are unverified "
                        "against the Staatsblad; cannot compute live personal income tax above SRD 192,000."
                    )
                chunk = net_income - lower
                tax += chunk * rate / Decimal("100")
                breakdown.append(
                    {
                        "from": str(lower),
                        "to": None,
                        "rate": str(rate),
                        "amount": str(chunk),
                        "tax": str(_q(chunk * rate / Decimal("100"))),
                        "verified": verified,
                    }
                )
            break
        if net_income <= lower:
            break
        chunk = min(net_income, ceiling) - lower
        if chunk > 0:
            tax += chunk * rate / Decimal("100")
            breakdown.append(
                {
                    "from": str(lower),
                    "to": str(ceiling),
                    "rate": str(rate),
                    "amount": str(chunk),
                    "tax": str(_q(chunk * rate / Decimal("100"))),
                    "verified": verified,
                }
            )
        lower = ceiling
        if net_income <= ceiling:
            break

    # DB-backed rate check: ensure at least one verified rule exists
    rule = _get_rule(db, country, "personal_income_tax", "personal_income_tax_rate")
    if rule is None or rule.verification_status != "verified":
        raise TaxUnverifiedError(
            "No verified personal income tax rule in database; cannot compute live tax."
        )

    return {
        "country": country,
        "tax_type": "personal_income_tax",
        "taxable_amount": str(_q(net_income)),
        "tax_owed": str(_q(tax)),
        "breakdown": breakdown,
        "source_url": rule.source_url,
        "effective_date": rule.effective_date,
        "last_verified_date": rule.last_verified_date,
    }


# ---------------------------------------------------------------------------
# VAT / BTW — Suriname: 10% standard (since 2023-01-01), 25% luxury, 5% reduced, 0%
# Registration threshold SRD 1,000,000/year (VERIFIED)
# ---------------------------------------------------------------------------
_VAT_RATES = {
    "standard": (Decimal("10"), True),
    "reduced": (Decimal("5"), True),
    "luxury": (Decimal("25"), True),
    "zero": (Decimal("0"), True),
}


def compute_vat(db: Session, amount: Decimal, rate_category: str = "standard", country: str = "SR") -> dict:
    amount = _money(amount)
    if rate_category not in _VAT_RATES:
        raise ValueError(f"Unknown VAT rate category: {rate_category}")
    rate, verified = _VAT_RATES[rate_category]
    if not verified:
        raise TaxUnverifiedError(f"VAT rate category '{rate_category}' is unverified")
    vat = _q(amount * rate / Decimal("100"))
    return {
        "country": country,
        "tax_type": "vat",
        "amount": str(_q(amount)),
        "rate_category": rate_category,
        "rate": str(rate),
        "vat": str(vat),
        "total": str(_q(amount + vat)),
        "registration_threshold_srd": "1000000",
        "verified": verified,
    }


# ---------------------------------------------------------------------------
# Wage / payroll tax — Suriname (Staatsbesluit 11 Jan 2024, art. 18a)
# Tax-free SRD 108,000/year; 8% on first SRD 42,000; brackets above unverified.
# ---------------------------------------------------------------------------
def compute_wage_tax(db: Session, annual_salary: Decimal, country: str = "SR") -> dict:
    annual_salary = _money(annual_salary)
    tax = Decimal("0")
    breakdown = []
    # Apply tax-free threshold first
    taxable = annual_salary - Decimal("108000")
    if taxable <= 0:
        return {
            "country": country,
            "tax_type": "wage_tax",
            "annual_salary": str(_q(annual_salary)),
            "tax_owed": "0",
            "breakdown": [{"from": "0", "to": "108000", "rate": "0", "amount": str(_q(annual_salary)), "tax": "0", "verified": True}],
            "note": "Below annual tax-free threshold of SRD 108,000",
        }
    chunk = min(taxable, Decimal("42000"))
    tax += chunk * Decimal("8") / Decimal("100")
    breakdown.append(
        {
            "from": "108000",
            "to": "150000",
            "rate": "8",
            "amount": str(_q(chunk)),
            "tax": str(_q(chunk * Decimal("8") / Decimal("100"))),
            "verified": True,
        }
    )
    remaining = taxable - chunk
    if remaining > 0:
        raise TaxUnverifiedError(
            "Wage tax brackets above SRD 150,000 annual taxable are unverified against the Staatsblad; "
            "cannot compute live wage tax above that point."
        )
    return {
        "country": country,
        "tax_type": "wage_tax",
        "annual_salary": str(_q(annual_salary)),
        "tax_owed": str(_q(tax)),
        "breakdown": breakdown,
    }


# ---------------------------------------------------------------------------
# Withholding tax — Suriname: dividend 25% (NV); treaty 7.5% PENDING
# ---------------------------------------------------------------------------
def compute_withholding_tax(db: Session, amount: Decimal, withholding_type: str = "dividend", country: str = "SR") -> dict:
    amount = _money(amount)
    if withholding_type == "dividend":
        rate = Decimal("25")
        verified = True
        note = "Dividend withholding 25% (NV); branch exempt; treaty rate unverified"
    elif withholding_type == "dividend_treaty":
        rate = Decimal("7.5")
        verified = False
        note = "Suriname-Netherlands treaty dividend rate 7.5% — UNVERIFIED, not for live use"
    else:
        raise ValueError(f"Unknown withholding type: {withholding_type}")
    if not verified:
        raise TaxUnverifiedError(note)
    tax = _q(amount * rate / Decimal("100"))
    return {
        "country": country,
        "tax_type": "withholding_tax",
        "withholding_type": withholding_type,
        "amount": str(_q(amount)),
        "rate": str(rate),
        "tax_owed": str(tax),
        "verified": verified,
        "note": note,
    }


def list_unverified_rules(db: Session, country: str = "SR") -> list[dict]:
    """Return tax rules that need verification before live use."""
    rows = (
        db.query(TaxRule)
        .filter(TaxRule.country == country, TaxRule.verification_status == "pending", TaxRule.is_active == True)  # noqa: E712
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

