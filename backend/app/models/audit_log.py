"""System-wide audit logging model for SOC 2 compliance."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class AuditAction(str, Enum):
    """Audit action types for SOC 2 compliance tracking."""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    EXPORT = "EXPORT"
    BULK_OPERATION = "BULK_OPERATION"
    STATUS_CHANGE = "STATUS_CHANGE"
    PERMISSION_CHANGE = "PERMISSION_CHANGE"
    CONFIG_CHANGE = "CONFIG_CHANGE"


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """System-wide audit log for tracking all user actions.

    Provides comprehensive audit trail for SOC 2 compliance requirements,
    tracking all CRUD operations, authentication events, and data exports.
    """

    __tablename__ = "audit_logs"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Action details
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    resource_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    # Change tracking - JSON fields for old/new values
    old_values: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    new_values: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Request context
    ip_address: Mapped[str | None] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Additional details
    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="audit_logs",
    )
    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="audit_logs",
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, action={self.action}, "
            f"resource_type={self.resource_type}, user_id={self.user_id})>"
        )

    @property
    def is_authentication_event(self) -> bool:
        """Check if this is an authentication-related event."""
        return self.action in [
            AuditAction.LOGIN.value,
            AuditAction.LOGOUT.value,
            AuditAction.LOGIN_FAILED.value,
        ]

    @property
    def is_data_modification(self) -> bool:
        """Check if this event modified data."""
        return self.action in [
            AuditAction.CREATE.value,
            AuditAction.UPDATE.value,
            AuditAction.DELETE.value,
        ]
