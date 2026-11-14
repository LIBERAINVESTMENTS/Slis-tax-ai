"""Pytest configuration: in-memory SQLite, test client, seeded tenant/company."""
from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from ai_accountant_backend.main import app
from ai_accountant_backend.db import SessionLocal, engine
from ai_accountant_backend.models import Base
from ai_accountant_backend.models.tenant import Tenant, User
from ai_accountant_backend.models.company import Company
from ai_accountant_backend.models.chart_of_accounts import Account
from ai_accountant_backend.models.tax_rule import TaxRule
from ai_accountant_backend.security import hash_password


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def tenant_user_company(db):
    tenant = Tenant(name="Test Tenant", slug="test-tenant", is_active=True)
    db.add(tenant)
    db.flush()
    user = User(
        tenant_id=tenant.id,
        email="owner@test.test",
        password_hash=hash_password("password123"),
        full_name="Owner",
        role="owner",
        is_active=True,
    )
    db.add(user)
    db.flush()
    company = Company(
        tenant_id=tenant.id,
        name="Test Co",
        slug="test-co",
        country="SR",
        currency="SRD",
        is_active=True,
    )
    db.add(company)
    db.flush()
    # Chart of accounts
    for code, name, typ, sub in [
        ("1100", "Bank", "asset", "bank"),
        ("4100", "Sales", "revenue", "revenue"),
        ("5100", "Salaries", "expense", "expense"),
        ("2000", "AP", "liability", "payable"),
    ]:
        db.add(Account(company_id=company.id, code=code, name=name, type=typ, subtype=sub, currency="SRD"))
    # Verified tax rules
    db.add(TaxRule(country="SR", tax_type="corporate_income_tax", name="corporate_income_tax_rate",
                   rate="36", basis="profit", source_url="https://eitisuriname.gov.sr/",
                   effective_date="2024-01-01", last_verified_date="2026-11-13",
                   verification_status="verified", is_active=True))
    db.add(TaxRule(country="SR", tax_type="vat", name="vat_standard_rate",
                   rate="10", basis="turnover", source_url="https://trykintsugi.com/sales-tax-guides/latam/suriname",
                   effective_date="2023-01-01", last_verified_date="2026-11-13",
                   verification_status="verified", is_active=True))
    db.add(TaxRule(country="SR", tax_type="personal_income_tax", name="personal_income_tax_rate",
                   rate="progressive", basis="net_income", source_url="https://vsbstia.org/sr-bracket",
                   effective_date="2024-01-01", last_verified_date="2026-11-13",
                   verification_status="verified", is_active=True))
    db.commit()
    return tenant, user, company


@pytest.fixture
def client():
    return TestClient(app)

