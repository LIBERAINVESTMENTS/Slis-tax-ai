"""FastAPI dependencies: authentication, tenant/company scoping, RBAC."""
from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ai_accountant_backend.db import get_db, set_current_company, set_current_tenant
from ai_accountant_backend.models import User
from ai_accountant_backend.security import TokenPayload, decode_token

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload: TokenPayload = decode_token(creds.credentials)
    except Exception as exc:  # expired, tampered, wrong key
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        ) from exc
    user = db.query(User).filter(User.id == payload.user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")
    # Bind tenant/company context for the remainder of this request.
    set_current_tenant(user.tenant_id)
    set_current_company(None)
    return user


def require_role(*roles: str) -> Callable:
    """Dependency factory that restricts an endpoint to the given roles."""

    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role in {roles}",
            )
        return user

    return _check


