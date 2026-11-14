"""AI cost/token accounting per request."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ai_accountant_backend.models.shared import Base, created_at, pk, updated_at


class AICostRecord(Base):
    __tablename__ = "ai_cost_records"

    id: Mapped[pk]
    tenant_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    agent: Mapped[str | None] = mapped_column(String(60), nullable=True)  # accountant|tax|cfo|...
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    tier: Mapped[str | None] = mapped_column(String(20), nullable=True)  # light|standard|heavy
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


