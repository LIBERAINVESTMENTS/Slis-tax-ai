# AI Accountant

AI-powered accounting and financial management platform combining QuickBooks/Xero-style bookkeeping,
an AI accountant, tax consultant, and CFO. Suriname tax first, with an architecture for any country.

## Stack

- **Backend:** FastAPI + SQLAlchemy + Alembic, PostgreSQL + pgvector (Docker), SQLite for local dev
- **Frontend:** Next.js 15 + React 19 + Tailwind CSS
- **AI:** Provider-agnostic LLM layer (OpenRouter, OpenAI, Anthropic, Moonshot, DeepSeek, Ollama)
  with tiered routing, cost tracking, fallback, and a deterministic `mock` provider for offline work
- **Money:** Python `Decimal` everywhere; every posted journal entry must balance

## Quickstart — local dev (SQLite, zero dependencies)

### Backend

```bash
cd backend
python -m venv --system-site-packages .venv
.venv\Scripts\python -m pip install -r requirements.txt
cp .env.example .env
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

### Frontend (another terminal)

```bash
cd frontend
pnpm install
pnpm dev         # http://localhost:3000
```

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

## What's implemented (v1 core)

- Multi-tenant auth (JWT access/refresh, PBKDF2 passwords, RBAC owner/admin/employee)
- MFA (TOTP) framework
- Companies: multiple business entities per user, strictly isolated
- Chart of accounts per company
- Double-entry journal engine: every posted entry must balance (Decimal), posted entries immutable,
  period locking, tamper-evident hash chain
- Suriname tax engine skeleton with verifiable rules (source/effective/verification dates)
- Audit log with tamper-evident hash chain
- AI agent scaffolding (provider-agnostic LLM layer)

## Still required to go live

| Item | Status |
|------|--------|
| LLM API key (OpenRouter/OpenAI/Anthropic/Moonshot/DeepSeek) | Optional — mock provider works offline |
| OCR service credentials (Document Agent) | Not configured |
| SMTP/SMS provider (MFA delivery, notifications) | Not configured |
| Suriname Belastingdienst e-filing credentials | Stub only |
| Official confirmation of Suriname tax brackets above SRD 192,000, wage brackets, employer social rates, filing deadlines, accounting standards | Pending — marked `verification_status='pending'` |
