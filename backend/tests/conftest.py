"""Pytest configuration: isolated in-memory SQLite, test client, seeded tenant/company.

Tests must NEVER touch the dev database (ai-accountant.db). They use an isolated
in-memory SQLite engine with StaticPool so every connection shares the same DB.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ai_accountant_backend.main import app
from ai_accountant_backend.db import get_db
from ai_accountant_backend.models import Base
from ai_accountant_backend.models.tenant import Tenant, User
from ai_accountant_backend.models.company import Company
from ai_accountant_backend.models.chart_of_accounts import Account
from ai_accountant_backend.models.tax_rule import TaxRule
from ai_accountant_backend.security import hash_password

# Isolated in-memory SQLite engine (independent of the dev DB).
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)


@event.listens_for(TEST_ENGINE, "connect")
def _fk_pragma(dbapi_conn, _record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSession = sessionmaker(bind=TEST_ENGINE, autoflush=False, autocommit=False, future=True)


def _override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    session = TestSession()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=TEST_ENGINE)


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
