"""Remediation workflow models for tracking finding remediation."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.finding import Finding
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.vendor import Vendor


class RemediationStatus(str, Enum):
    """Status of a remediation task through its lifecycle."""

    DRAFT = "draft"
    PENDING_ASSIGNMENT = "pending_assignment"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    CLOSED = "closed"
    EXCEPTION_REQUESTED = "exception_requested"
    EXCEPTION_APPROVED = "exception_approved"
    EXCEPTION_DENIED = "exception_denied"
    REOPENED = "reopened"


class RemediationPriority(str, Enum):
    """Priority level for remediation tasks."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# State machine transitions - defines valid status transitions
VALID_TRANSITIONS = {
    RemediationStatus.DRAFT: [RemediationStatus.PENDING_ASSIGNMENT],
    RemediationStatus.PENDING_ASSIGNMENT: [RemediationStatus.ASSIGNED],
    RemediationStatus.ASSIGNED: [
        RemediationStatus.IN_PROGRESS,
        RemediationStatus.EXCEPTION_REQUESTED,
    ],
    RemediationStatus.IN_PROGRESS: [
        RemediationStatus.PENDING_REVIEW,
        RemediationStatus.EXCEPTION_REQUESTED,
    ],
    RemediationStatus.PENDING_REVIEW: [
        RemediationStatus.IN_PROGRESS,
        RemediationStatus.PENDING_VERIFICATION,
    ],
    RemediationStatus.PENDING_VERIFICATION: [
        RemediationStatus.PENDING_REVIEW,
        RemediationStatus.VERIFIED,
    ],
    RemediationStatus.VERIFIED: [RemediationStatus.CLOSED],
    RemediationStatus.CLOSED: [RemediationStatus.REOPENED],
    RemediationStatus.EXCEPTION_REQUESTED: [
        RemediationStatus.EXCEPTION_APPROVED,
        RemediationStatus.EXCEPTION_DENIED,
    ],
    RemediationStatus.EXCEPTION_DENIED: [RemediationStatus.IN_PROGRESS],
    RemediationStatus.REOPENED: [RemediationStatus.IN_PROGRESS],
}


class RemediationTask(Base, UUIDMixin, TimestampMixin):
    """Remediation task for tracking finding remediation.

    Links to findings and tracks the full remediation lifecycle
    including assignments, SLA tracking, and audit trail.
    """

    __tablename__ = "remediation_tasks"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    finding_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("vendors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assignee_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )

    # Task details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=RemediationStatus.DRAFT.value, index=True
    )
    priority: Mapped[str] = mapped_column(
        String(20), default=RemediationPriority.MEDIUM.value, index=True
    )

    # SLA tracking
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    sla_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sla_breached: Mapped[bool] = mapped_column(default=False, index=True)
    sla_breached_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Resolution
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_by_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Exception handling
    exception_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    exception_approved_by_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True
    )
    exception_approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # External system integration
    external_system: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )
    external_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    external_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    external_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sync_enabled: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    sync_direction: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="remediation_tasks",
    )
    finding: Mapped["Finding"] = relationship(
        "Finding",
        back_populates="remediation_task",
    )
    vendor: Mapped["Vendor | None"] = relationship(
        "Vendor",
        back_populates="remediation_tasks",
    )
    assignee: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[assignee_id],
        back_populates="assigned_tasks",
    )
    created_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_id],
    )
    audit_logs: Mapped[list["RemediationAuditLog"]] = relationship(
        "RemediationAuditLog",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="RemediationAuditLog.created_at.desc()",
    )
    comments: Mapped[list["RemediationComment"]] = relationship(
        "RemediationComment",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="RemediationComment.created_at.desc()",
    )

    def __repr__(self) -> str:
        return (
            f"<RemediationTask(id={self.id}, title={self.title[:50]}, "
            f"status={self.status}, priority={self.priority})>"
        )

    def can_transition_to(self, new_status: RemediationStatus) -> bool:
        """Check if transition to new status is valid."""
        current = RemediationStatus(self.status)
        return new_status in VALID_TRANSITIONS.get(current, [])

    @property
    def is_overdue(self) -> bool:
        """Check if task is past due date."""
        if self.due_date is None:
            return False
        if self.status in [
            RemediationStatus.CLOSED.value,
            RemediationStatus.VERIFIED.value,
            RemediationStatus.EXCEPTION_APPROVED.value,
        ]:
            return False
        return datetime.now(self.due_date.tzinfo) > self.due_date

    @property
    def is_closed(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in [
            RemediationStatus.CLOSED.value,
            RemediationStatus.EXCEPTION_APPROVED.value,
        ]


class RemediationAuditLog(Base, UUIDMixin, TimestampMixin):
    """Audit log entry for remediation task changes.

    Tracks all changes to remediation tasks for compliance and accountability.
    """

    __tablename__ = "remediation_audit_logs"

    # Foreign keys
    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("remediation_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Change details
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    field_changed: Mapped[str | None] = mapped_column(String(100), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    task: Mapped["RemediationTask"] = relationship(
        "RemediationTask",
        back_populates="audit_logs",
    )
    user: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<RemediationAuditLog(id={self.id}, task_id={self.task_id}, "
            f"action={self.action})>"
        )


class RemediationComment(Base, UUIDMixin, TimestampMixin):
    """Comment on a remediation task.

    Allows team members to communicate about remediation progress.
    """

    __tablename__ = "remediation_comments"

    # Foreign keys
    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("remediation_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )

    # Comment content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(default=True)

    # Relationships
    task: Mapped["RemediationTask"] = relationship(
        "RemediationTask",
        back_populates="comments",
    )
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<RemediationComment(id={self.id}, task_id={self.task_id}, "
            f"user_id={self.user_id})>"
        )


class SLAPolicy(Base, UUIDMixin, TimestampMixin):
    """SLA policy configuration for an organization.

    Defines default SLA days based on priority for remediation tasks.
    """

    __tablename__ = "sla_policies"

    # Foreign key
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Policy name
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_default: Mapped[bool] = mapped_column(default=False)

    # SLA days by priority
    critical_sla_days: Mapped[int] = mapped_column(Integer, default=3)
    high_sla_days: Mapped[int] = mapped_column(Integer, default=7)
    medium_sla_days: Mapped[int] = mapped_column(Integer, default=30)
    low_sla_days: Mapped[int] = mapped_column(Integer, default=90)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="sla_policies",
    )

    def __repr__(self) -> str:
        return f"<SLAPolicy(id={self.id}, name={self.name}, org={self.organization_id})>"

    def get_sla_days(self, priority: RemediationPriority) -> int:
        """Get SLA days for a given priority."""
        mapping = {
            RemediationPriority.CRITICAL: self.critical_sla_days,
            RemediationPriority.HIGH: self.high_sla_days,
            RemediationPriority.MEDIUM: self.medium_sla_days,
            RemediationPriority.LOW: self.low_sla_days,
        }
        return mapping.get(priority, self.medium_sla_days)
