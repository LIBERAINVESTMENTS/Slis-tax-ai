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