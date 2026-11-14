"""Password hashing, JWT token handling, and MFA (TOTP) helpers."""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt

from ai_accountant_backend.config import settings

_PBKDF2_ITERATIONS = 260_000
_PBKDF2_ALGO = "sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGO, password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return "pbkdf2_sha256${}${}${}".format(
        _PBKDF2_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode(),
        base64.urlsafe_b64encode(digest).decode(),
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, iterations_s, salt_s, digest_s = encoded.split("$")
        if algo != "pbkdf2_sha256":
            return False
        iterations = int(iterations_s)
        salt = base64.urlsafe_b64decode(salt_s.encode())
        expected = base64.urlsafe_b64decode(digest_s.encode())
    except Exception:
        return False
    actual = hashlib.pbkdf2_hmac(_PBKDF2_ALGO, password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


@dataclass
class TokenPayload:
    user_id: int
    tenant_id: int
    role: str
    email: str
    token_type: str = "access"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(subject: int, tenant_id: int, role: str, email: str) -> str:
    return _create_token(
        subject, tenant_id, role, email, timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(subject: int, tenant_id: int, role: str, email: str) -> str:
    return _create_token(
        subject, tenant_id, role, email, timedelta(days=settings.refresh_token_expire_days)
    )


def _create_token(
    subject: int, tenant_id: int, role: str, email: str, expires_delta: timedelta
) -> str:
    payload = {
        "sub": str(subject),
        "tid": tenant_id,
        "role": role,
        "email": email,
        "iat": _now(),
        "exp": _now() + expires_delta,
        "type": "access" if expires_delta == timedelta(minutes=settings.access_token_expire_minutes) else "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> TokenPayload:
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    return TokenPayload(
        user_id=int(payload["sub"]),
        tenant_id=int(payload["tid"]),
        role=payload["role"],
        email=payload["email"],
        token_type=payload.get("type", "access"),
    )


# --- MFA (TOTP) helpers ---

def b32decode(secret: str) -> bytes:
    """Base32-decode a TOTP secret, tolerating lower-case and padding."""
    import base64 as _b64

    padded = secret + "=" * (-len(secret) % 8)
    return _b64.b32decode(padded.upper())


def generate_totp_secret() -> str:
    import base64 as _b64

    return _b64.b32encode(secrets.token_bytes(20)).decode()


def totp_code(secret: str, timestamp: int | None = None, digits: int = 6) -> str:
    """Compute the TOTP code for a secret at a given Unix timestep (30s intervals)."""
    if timestamp is None:
        timestamp = int(time.time())
    key = b32decode(secret)
    counter = timestamp // 30
    msg = counter.to_bytes(8, "big")
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    truncated = int.from_bytes(digest[offset : offset + 4], "big") & 0x7FFFFFFF
    code = truncated % (10 ** digits)
    return f"{code:0{digits}d}"


def verify_totp(secret: str, code: str, window: int | None = None) -> bool:
    """Verify a TOTP code, allowing a small window for clock drift."""
    if window is None:
        window = settings.mfa_window
    now = int(time.time())
    for offset in range(-window, window + 1):
        if totp_code(secret, now + offset * 30) == code:
            return True
    return False


