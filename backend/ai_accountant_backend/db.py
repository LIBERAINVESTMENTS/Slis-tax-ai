"""Database engine, session, and tenant/company-scoped session management."""
from __future__ import annotations

from contextvars import ContextVar
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from ai_accountant_backend.config import settings

# Re-export the models' declarative base so `Base.metadata.create_all()` sees every
# registered model. (Do NOT define a second base here — that would silently produce an
# empty metadata and create no tables.)
from ai_accountant_backend.models.shared import Base  # noqa: E402

# Current tenant/company context for the active request. Every repository query MUST
# filter by these so a user can never read another user's or company's rows.
_current_tenant_id: ContextVar[int | None] = ContextVar("current_tenant_id", default=None)
_current_company_id: ContextVar[int | None] = ContextVar("current_company_id", default=None)

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_current_tenant(tenant_id: int | None) -> None:
    _current_tenant_id.set(tenant_id)


def get_current_tenant_id() -> int | None:
    return _current_tenant_id.get()


def set_current_company(company_id: int | None) -> None:
    _current_company_id.set(company_id)


def get_current_company_id() -> int | None:
    return _current_company_id.get()


class Scope:
    """Context manager for a tenant/company-bound unit of work (used by jobs/webhooks/agents)."""

    def __init__(self, tenant_id: int | None, company_id: int | None) -> None:
        self.tenant_id = tenant_id
        self.company_id = company_id
        self._t = None
        self._c = None

    def __enter__(self) -> "Scope":
        self._t = _current_tenant_id.set(self.tenant_id)
        self._c = _current_company_id.set(self.company_id)
        return self

    def __exit__(self, *exc) -> None:
        _current_tenant_id.reset(self._t)
        _current_company_id.reset(self._c)


# Enforce a foreign key constraint for SQLite (useful in tests) where possible.
if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _record):  # noqa: ANN001
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


