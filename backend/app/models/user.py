"""User model for authentication and authorization."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.bpo import BPOAssessment
    from app.models.organization import Organization
    from app.models.query import ConversationThread, QueryHistory
    from app.models.remediation import RemediationTask


class UserRole(str, Enum):
    """User roles for authorization."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(Base, UUIDMixin, TimestampMixin):
    """User model for authentication.

    Users belong to an organization and have role-based access control.
    """

    __tablename__ = "users"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # User info
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Role and status
    role: Mapped[str] = mapped_column(String(20), default=UserRole.ANALYST.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # MFA
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Tracking
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="users",
    )
    conversation_threads: Mapped[list["ConversationThread"]] = relationship(
        "ConversationThread",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    query_history: Mapped[list["QueryHistory"]] = relationship(
        "QueryHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    assigned_tasks: Mapped[list["RemediationTask"]] = relationship(
        "RemediationTask",
        foreign_keys="RemediationTask.assignee_id",
        back_populates="assignee",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
    )
    bpo_assessments: Mapped[list["BPOAssessment"]] = relationship(
        "BPOAssessment",
        back_populates="assessor",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN.value
