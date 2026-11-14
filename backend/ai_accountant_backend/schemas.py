"""Pydantic schemas for request/response validation."""
from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, Field

# Decimal-safe money type for API boundaries
Money = Annotated[str, Field(description="Decimal-safe monetary amount as string")]


class UserOut(BaseModel):
    id: int
    email: str
    role: str
    full_name: Optional[str] = None
    mfa_enabled: bool = False


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    mfa_required: bool = False
    user: UserOut


class MfaSetupRequest(BaseModel):
    pass


class MfaVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


# --- Companies ---

class CompanyOut(BaseModel):
    id: int
    name: str
    slug: str
    country: str
    currency: str
    fiscal_year_start_month: int
    tax_regime: Optional[str] = None
    period_lock_date: Optional[str] = None
    is_active: bool


class CompanyCreate(BaseModel):
    name: str
    slug: str
    country: str = "SR"
    currency: str = "SRD"
    fiscal_year_start_month: int = 1
    tax_regime: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    fiscal_year_start_month: Optional[int] = None
    tax_regime: Optional[str] = None
    period_lock_date: Optional[str] = None


# --- Chart of accounts ---

class AccountOut(BaseModel):
    id: int
    code: str
    name: str
    type: str
    subtype: Optional[str] = None
    currency: str
    is_active: bool
    description: Optional[str] = None


class AccountCreate(BaseModel):
    code: str
    name: str
    type: str
    subtype: Optional[str] = None
    currency: str = "SRD"
    description: Optional[str] = None


# --- Journal ---

class JournalLineIn(BaseModel):
    account_id: int
    debit: Money = "0"
    credit: Money = "0"
    memo: Optional[str] = None


class JournalEntryCreate(BaseModel):
    entry_no: str
    entry_date: str
    reference: Optional[str] = None
    description: Optional[str] = None
    lines: list[JournalLineIn]


class JournalEntryOut(BaseModel):
    id: int
    entry_no: str
    entry_date: str
    reference: Optional[str] = None
    description: Optional[str] = None
    posted: bool
    hash: str
    prev_hash: str
