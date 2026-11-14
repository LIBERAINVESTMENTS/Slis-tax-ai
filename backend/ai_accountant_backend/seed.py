"""Seed the database with a demo tenant, user, company, chart of accounts, and verified Suriname tax rules.

Run: .venv\Scripts\python -m app.seed
"""
from __future__ import annotations

from ai_accountant_backend.db import SessionLocal, engine
from ai_accountant_backend.models import Base
from ai_accountant_backend.models.tenant import Tenant, User
from ai_accountant_backend.models.company import Company
from ai_accountant_backend.models.chart_of_accounts import Account
from ai_accountant_backend.models.tax_rule import TaxRule
from ai_accountant_backend.security import hash_password


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Demo tenant + owner user
        tenant = Tenant(name="Demo User", slug="demo-user", is_active=True)
        db.add(tenant)
        db.flush()
        user = User(
            tenant_id=tenant.id,
            email="owner@demo.test",
            password_hash=hash_password("password123"),
            full_name="Demo Owner",
            role="owner",
            is_active=True,
        )
        db.add(user)
        db.flush()

        # Demo company (Suriname)
        company = Company(
            tenant_id=tenant.id,
            name="Demo N.V.",
            slug="demo-nv",
            country="SR",
            currency="SRD",
            fiscal_year_start_month=1,
            tax_regime="suriname_corporate",
            is_active=True,
        )
        db.add(company)
        db.flush()

        # Chart of accounts (Suriname-style)
        accounts = [
            ("1000", "Cash", "asset", "cash", "SRD"),
            ("1100", "Bank account", "asset", "bank", "SRD"),
            ("1200", "Accounts receivable", "asset", "receivable", "SRD"),
            ("1300", "Inventory", "asset", "inventory", "SRD"),
            ("1400", "Fixed assets", "asset", "fixed_asset", "SRD"),
            ("2000", "Accounts payable", "liability", "payable", "SRD"),
            ("2100", "VAT payable", "liability", "payable", "SRD"),
            ("2200", "Payroll tax payable", "liability", "payable", "SRD"),
            ("3000", "Equity", "equity", "equity", "SRD"),
            ("3100", "Retained earnings", "equity", "equity", "SRD"),
            ("4000", "Revenue", "revenue", "revenue", "SRD"),
            ("4100", "Sales revenue", "revenue", "revenue", "SRD"),
            ("5000", "Cost of goods sold", "expense", "cogs", "SRD"),
            ("5100", "Salaries expense", "expense", "expense", "SRD"),
            ("5200", "Rent expense", "expense", "expense", "SRD"),
            ("5300", "Utilities expense", "expense", "expense", "SRD"),
            ("5400", "VAT expense", "expense", "expense", "SRD"),
            ("6000", "Depreciation expense", "expense", "expense", "SRD"),
        ]
        for code, name, typ, subtype, currency in accounts:
            db.add(Account(company_id=company.id, code=code, name=name, type=typ, subtype=subtype, currency=currency))

        # Verified Suriname tax rules
        rules = [
            # Corporate income tax 36% — VERIFIED (EITI Suriname / Income Tax Act 1922)
            TaxRule(
                country="SR", tax_type="corporate_income_tax", name="corporate_income_tax_rate",
                rate="36", basis="taxable_profit",
                source_url="https://eitisuriname.gov.sr/en/eiti-suriname-reports/eiti-suriname-report-2016/payments-to-the-ministry-of-finance-directorate-direct-and-indirect-taxes/",
                effective_date="2024-01-01", last_verified_date="2026-11-13",
                verification_status="verified", is_active=True,
            ),
            # VAT standard 10% — VERIFIED (Kintsugi/VSB, in force since 2023-01-01)
            TaxRule(
                country="SR", tax_type="vat", name="vat_standard_rate",
                rate="10", basis="taxable_turnover",
                source_url="https://trykintsugi.com/sales-tax-guides/latam/suriname",
                effective_date="2023-01-01", last_verified_date="2026-11-13",
                verification_status="verified", is_active=True,
            ),
            # VAT reduced 5%
            TaxRule(
                country="SR", tax_type="vat", name="vat_reduced_rate",
                rate="5", basis="reduced_categories",
                source_url="https://vsbstia.org/wp-content/uploads/2025/06/Brochure-Detail-en-Groothandel_01-mei-2025.pdf",
                effective_date="2023-01-01", last_verified_date="2026-11-13",
                verification_status="verified", is_active=True,
            ),
            # VAT luxury 25%
            TaxRule(
                country="SR", tax_type="vat", name="vat_luxury_rate",
                rate="25", basis="luxury_goods",
                source_url="https://vsbstia.org/wp-content/uploads/2025/06/Brochure-Detail-en-Groothandel_01-mei-2025.pdf",
                effective_date="2023-01-01", last_verified_date="2026-11-13",
                verification_status="verified", is_active=True,
            ),
            # VAT zero 0% (exports)
            TaxRule(
                country="SR", tax_type="vat", name="vat_zero_rate",
                rate="0", basis="exports",
                source_url="https://trykintsugi.com/sales-tax-guides/latam/suriname",
                effective_date="2023-01-01", last_verified_date="2026-11-13",
                verification_status="verified", is_active=True,
            ),
            # Personal income tax — tax-free threshold SRD 108,000 — VERIFIED (Staatsbesluit 11 Jan 2024)
            TaxRule(
                country="SR", tax_type="personal_income_tax", name="personal_income_tax_rate",
                rate="progressive", basis="net_income",
                source_url="https://vsbstia.org/wp-content/uploads/2024/01/S.B.-2024-no.-3-STAATSBESLUIT-11-januari-2024-uitvoering-art-52-h-Inkomstenbelasting-1922-G.B.-1921-no.-112-gewijzigd-S.B.-2022-no.-150.pdf",
                effective_date="2024-01-01", last_verified_date="2026-11-13",
                verification_status="verified", is_active=True,
            ),
            # Wage tax 8% first bracket — VERIFIED (Staatsbesluit 11 Jan 2024)
            TaxRule(
                country="SR", tax_type="wage_tax", name="wage_tax_first_bracket",
                rate="8", basis="taxable_annual_salary_above_threshold",
                source_url="https://dna.sr/media/396877/SB_2024___2.PDF",
                effective_date="2024-01-01", last_verified_date="2026-11-13",
                verification_status="verified", is_active=True,
            ),
        ]
        for r in rules:
            db.add(r)
        db.commit()
        print("Seed complete.")
        print(f"  tenant: {tenant.id} ({tenant.slug})")
        print(f"  user: {user.email} / password123")
        print(f"  company: {company.id} ({company.name})")
        print(f"  accounts: {len(accounts)}")
        print(f"  tax rules: {len(rules)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

