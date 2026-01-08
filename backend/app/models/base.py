"""SQLAlchemy base model and mixins."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Provides common functionality and type annotations for all models.
    """

    # Enable type annotation support
    type_annotation_map = {
        str: String(255),
    }


class UUIDMixin:
    """Mixin for UUID primary key.

    Provides a UUID primary key that is automatically generated.
    Uses string representation for SQLite compatibility.
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps.

    Automatically sets created_at on insert and updates updated_at on every update.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality.

    Instead of permanently deleting records, marks them as deleted.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft deleted."""
        return self.deleted_at is not None
