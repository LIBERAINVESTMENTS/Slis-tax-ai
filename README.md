# Slis Tax AI

AI-powered accounting, tax, and financial management platform. Combines the capabilities of
QuickBooks/Xero, a professional accountant, a tax consultant, and a CFO in one system.

**Suriname tax first**, with an architecture built for adding more countries without rebuilding.

## Features

- **Double-entry accounting engine** — chart of accounts, general ledger, balanced journal
  entries (debits must equal credits), immutable posted entries, period locking, tamper-evident
  SHA-256 hash chain.
- **Personal & business finance** — multiple companies per user, strictly isolated per tenant.
- **Suriname tax engine** — corporate income tax (36%), VAT/BTW (10%/5%/25%/0%), personal
  income tax, wage/payroll tax, withholding tax. Every rule records its source, effective date,
  and verification date; unverified brackets are blocked from live calculation.
- **AI agent workforce** — Master coordinator plus Accountant, Tax, CFO, Personal Finance,
  Document, and Audit agents. Provider-agnostic LLM layer (OpenRouter, OpenAI, Anthropic,
  Moonshot, DeepSeek, Ollama) with tiered routing, cost tracking, and a deterministic offline
  `mock` provider.
- **Tax preparation & filing center** — collect info → detect missing docs → calculate →
  schedules → downloadable return → explicit approval → submission (never claims submission
  without proof).
- **Security** — JWT auth, MFA (TOTP), RBAC, multi-tenant isolation, audit logs, encrypted
  secrets.
- **Modern dashboard** — Next.js 15 + React 19 + Tailwind, dark/light theme, responsive.

## Stack

- **Backend:** FastAPI + SQLAlchemy + Alembic, PostgreSQL (pgvector) via Docker, SQLite for local dev
- **Frontend:** Next.js 15 + React 19 + Tailwind CSS
- **Money:** Python `Decimal` everywhere (never floats); LLMs never do arithmetic

## Quickstart

### Local dev (SQLite, zero dependencies)

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m ai_accountant_backend.seed
.venv\Scripts\python -m uvicorn ai_accountant_backend.main:app --port 8000
```

```bash
# Frontend (separate terminal)
cd frontend
pnpm install
pnpm dev        # http://localhost:3000
```

Sign in with the demo owner: **owner@demo.test / password123**

### Docker (Postgres + pgvector + backend + frontend)

```bash
docker compose up --build
# backend: http://localhost:8000/health
# frontend: http://localhost:3000
```

## Testing

```bash
cd backend
.venv\Scripts\python -m pytest -q
```

Covers double-entry balance validation, journal reversal, Suriname tax calculations, and
unverified-rule rejection.

## Still required to go live

| Item | Status |
|------|--------|
| LLM API key (OpenRouter/OpenAI/Anthropic/Moonshot/DeepSeek/Ollama) | Optional — `mock` provider works offline |
| OCR service (AWS Textract / Azure Form Recognizer / Google Document AI) | Not configured |
| SMTP/SMS provider (MFA delivery, notifications) | Not configured |
| Suriname Belastingdienst e-filing credentials | Stub only |
| Official confirmation of Suriname brackets above SRD 192,000, wage brackets, employer social rates, filing deadlines, accounting standards | Pending — flagged `verification_status='pending'` |

**Important:** tax rules marked `pending` are never used for live calculations. Always verify
rates against official sources before filing.

## License

Proprietary — all rights reserved.
