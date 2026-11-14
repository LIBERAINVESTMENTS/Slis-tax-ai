"""Tenant (user account) and User models."""
from __future__ import annotations

from sqlalchemy import ForeignKey, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_accountant_backend.models.shared import Base, created_at, pk, updated_at


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[pk]
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = created_at

    users: Mapped[list["User"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id: Mapped[pk]
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(50), default="employee", nullable=False)  # owner|admin|employee
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # MFA
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    totp_secret: Mapped[str | None] = mapped_column(String(200))
    mfa_recovery_codes: Mapped[str | None] = mapped_column(Text)  # JSON-encoded list of hashes
    created_at: Mapped[datetime] = created_at
    updated_at: Mapped[datetime] = updated_at

    tenant: Mapped["Tenant"] = relationship(back_populates="users")


