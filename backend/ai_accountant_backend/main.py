"""FastAPI application entrypoint for AI Accountant."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_accountant_backend.config import settings
from ai_accountant_backend.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For local SQLite development convenience, create tables on boot. Production uses Alembic.
    if settings.environment in ("development", "test") and settings.database_url.startswith("sqlite"):
        import ai_accountant_backend.models  # noqa: F401  (register all models)

        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from ai_accountant_backend.api import (  # noqa: E402
    auth,
    companies,
    accounts,
    journal,
    tax,
    documents,
    ai,
)

API = settings.api_prefix
app.include_router(auth.router, prefix=API)
app.include_router(companies.router, prefix=API)
app.include_router(accounts.router, prefix=API)
app.include_router(journal.router, prefix=API)
app.include_router(tax.router, prefix=API)
app.include_router(documents.router, prefix=API)
app.include_router(ai.router, prefix=API)


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}


