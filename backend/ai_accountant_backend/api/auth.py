"""Authentication endpoints: register, login, refresh, MFA setup/verify."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ai_accountant_backend.db import get_db
from ai_accountant_backend.deps import get_current_user
from ai_accountant_backend.models import Tenant, User
from ai_accountant_backend.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_totp_secret,
    hash_password,
    verify_password,
    verify_totp,
)
from ai_accountant_backend.schemas import (
    LoginRequest,
    MfaSetupRequest,
    MfaVerifyRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=UserOut)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    tenant = Tenant(name=payload.email, slug=payload.email.split("@")[0])
    db.add(tenant)
    db.flush()
    user = User(
        tenant_id=tenant.id,
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role="owner",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(id=user.id, email=user.email, role=user.role, full_name=user.full_name)


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive")
    access = create_access_token(user.id, user.tenant_id, user.role, user.email)
    refresh = create_refresh_token(user.id, user.tenant_id, user.role, user.email)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        mfa_required=user.mfa_enabled,
        user=UserOut(
            id=user.id,
            email=user.email,
            role=user.role,
            full_name=user.full_name,
            mfa_enabled=user.mfa_enabled,
        ),
    )


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        token = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if token.token_type != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")
    user = db.query(User).filter(User.id == token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive")
    access = create_access_token(user.id, user.tenant_id, user.role, user.email)
    refresh = create_refresh_token(user.id, user.tenant_id, user.role, user.email)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        mfa_required=user.mfa_enabled,
        user=UserOut(
            id=user.id,
            email=user.email,
            role=user.role,
            full_name=user.full_name,
            mfa_enabled=user.mfa_enabled,
        ),
    )


@router.post("/auth/mfa/setup")
def mfa_setup(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    secret = generate_totp_secret()
    user.totp_secret = secret
    db.commit()
    return {"secret": secret, "provisioning_url": f"otpauth://totp/{settings.mfa_issuer}:{user.email}?secret={secret}&issuer={settings.mfa_issuer}"}


@router.post("/auth/mfa/verify")
def mfa_verify(payload: MfaVerifyRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.totp_secret:
        raise HTTPException(status_code=400, detail="MFA not set up")
    if not verify_totp(user.totp_secret, payload.code):
        raise HTTPException(status_code=400, detail="Invalid code")
    user.mfa_enabled = True
    db.commit()
    return {"mfa_enabled": True}


