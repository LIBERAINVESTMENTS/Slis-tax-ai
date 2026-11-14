"use client"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const API_PREFIX = "/api"

function getAccessToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem("access_token")
}

function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem("refresh_token")
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAccessToken()
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const res = await fetch(`${API_URL}${API_PREFIX}${path}`, {
    ...options,
    headers,
  })

  if (res.status === 401) {
    const refresh = getRefreshToken()
    if (refresh) {
      const refreshRes = await fetch(`${API_URL}${API_PREFIX}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      })
      if (refreshRes.ok) {
        const data = await refreshRes.json()
        localStorage.setItem("access_token", data.access_token)
        localStorage.setItem("refresh_token", data.refresh_token)
        return request(path, options)
      }
    }
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    if (typeof window !== "undefined") {
      window.location.href = "/login"
    }
    throw new Error("Session expired")
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }

  if (res.status === 204) return undefined as T
  return res.json()
}

// Type definitions matching backend schemas
export interface UserOut {
  id: number
  email: string
  role: string
  full_name: string | null
  mfa_enabled: boolean
}

export interface CompanyOut {
  id: number
  name: string
  slug: string
  country: string
  currency: string
  fiscal_year_start_month: number
  tax_regime: string | null
  period_lock_date: string | null
  is_active: boolean
}

export interface AccountOut {
  id: number
  code: string
  name: string
  type: string
  subtype: string | null
  currency: string
  is_active: boolean
  description: string | null
}

export interface JournalEntryOut {
  id: number
  entry_no: string
  entry_date: string
  reference: string | null
  description: string | null
  posted: boolean
  hash: string
  prev_hash: string
}

export interface TaxReturnOut {
  id: number
  company_id: number | null
  country: string
  tax_type: string
  period_start: string
  period_end: string
  taxable_amount: string
  tax_owed: string
  tax_paid: string
  status: string
  approved_by_user_id: number | null
  approved_at: string | null
  submission_proof: string | null
  submitted_at: string | null
  filing_deadline: string | null
}

export const api = {
  // Auth
  register: (email: string, password: string, full_name?: string) =>
    request<UserOut>("/auth/register", { method: "POST", body: JSON.stringify({ email, password, full_name }) }),
  login: (email: string, password: string) =>
    request<{ access_token: string; refresh_token: string; mfa_required: boolean; user: UserOut }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  refresh: (refresh_token: string) =>
    request<{ access_token: string; refresh_token: string; mfa_required: boolean; user: UserOut }>("/auth/refresh", { method: "POST", body: JSON.stringify({ refresh_token }) }),

  // Companies
  listCompanies: () => request<CompanyOut[]>("/companies"),
  createCompany: (data: { name: string; slug: string; country?: string; currency?: string; fiscal_year_start_month?: number; tax_regime?: string }) =>
    request<CompanyOut>("/companies", { method: "POST", body: JSON.stringify(data) }),
  getCompany: (id: number) => request<CompanyOut>(`/companies/${id}`),
  updateCompany: (id: number, data: any) =>
    request<CompanyOut>(`/companies/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  selectCompany: (id: number) => request<{ company_id: number; name: string }>(`/companies/${id}/select`, { method: "POST" }),

  // Chart of accounts
  listAccounts: (companyId: number) => request<AccountOut[]>(`/companies/${companyId}/accounts`),
  createAccount: (companyId: number, data: any) =>
    request<AccountOut>(`/companies/${companyId}/accounts`, { method: "POST", body: JSON.stringify(data) }),

  // Journal entries
  listJournalEntries: (companyId: number) => request<JournalEntryOut[]>(`/companies/${companyId}/journal`),
  createJournalEntry: (companyId: number, data: any) =>
    request<JournalEntryOut>(`/companies/${companyId}/journal`, { method: "POST", body: JSON.stringify(data) }),
  reverseJournalEntry: (entryId: number) =>
    request<JournalEntryOut>(`/journal/${entryId}/reverse`, { method: "POST" }),

  // Tax
  calculateTax: (data: any) => request<any>("/tax/calculate", { method: "POST", body: JSON.stringify(data) }),
  getTaxCountries: () => request<{ countries: Array<{ code: string; name: string; currency: string; has_vat: boolean }> }>("/tax/countries"),
  createTaxReturn: (data: any) => request<TaxReturnOut>("/tax/returns", { method: "POST", body: JSON.stringify(data) }),
  listTaxReturns: () => request<TaxReturnOut[]>("/tax/returns"),
  approveTaxReturn: (id: number) => request<TaxReturnOut>(`/tax/returns/${id}/approve`, { method: "POST" }),
  submitTaxReturn: (id: number) => request<TaxReturnOut>(`/tax/returns/${id}/submit`, { method: "POST" }),
  downloadTaxReturn: (id: number) => request<any>(`/tax/returns/${id}/download`),

  // Financial reports
  getIncomeStatement: (companyId: number) => request<any>(`/companies/${companyId}/reports/income-statement`),
  getBalanceSheet: (companyId: number) => request<any>(`/companies/${companyId}/reports/balance-sheet`),
  getCashFlow: (companyId: number) => request<any>(`/companies/${companyId}/reports/cash-flow`),
  getFinancialStatements: (companyId: number) => request<any>(`/companies/${companyId}/reports`),

  // AI
  listAgents: () => request<any>("/ai/agents"),
  chat: (message: string, agent?: string) =>
    request<any>("/ai/chat", { method: "POST", body: JSON.stringify({ message, agent }) }),

  // MFA
  mfaSetup: () => request<{ secret: string; provisioning_url: string }>("/auth/mfa/setup", { method: "POST" }),
  mfaVerify: (code: string) => request<{ mfa_enabled: boolean }>("/auth/mfa/verify", { method: "POST", body: JSON.stringify({ code }) }),
}