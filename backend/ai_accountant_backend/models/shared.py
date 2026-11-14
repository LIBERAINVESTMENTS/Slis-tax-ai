"""Shared SQLAlchemy base and mixins."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Decimal-safe primary key id type
pk = Annotated[int, mapped_column(primary_key=True)]
uuid_id = Annotated[str, mapped_column(default=lambda: str(uuid.uuid4()), unique=True, index=True)]
created_at = Annotated[
    datetime, mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
]
updated_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    ),
]


class Base(DeclarativeBase):
    """Base class for all models."""
