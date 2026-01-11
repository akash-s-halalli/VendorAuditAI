"""Monitoring and alerting models for continuous vendor assessment."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.vendor import Vendor


class ScheduleFrequency(str, Enum):
    """Frequency options for scheduled assessments."""

    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class ScheduleStatus(str, Enum):
    """Status of a monitoring schedule."""

    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class AlertSeverity(str, Enum):
    """Severity levels for alerts."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, Enum):
    """Status of an alert."""

    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class NotificationChannelType(str, Enum):
    """Types of notification channels."""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    TEAMS = "teams"


class MonitoringSchedule(Base, UUIDMixin, TimestampMixin):
    """Schedule for automated vendor assessments.

    Defines when and how often to run assessments for vendors.
    """

    __tablename__ = "monitoring_schedules"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Schedule details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency: Mapped[str] = mapped_column(
        String(20), default=ScheduleFrequency.MONTHLY.value
    )
    status: Mapped[str] = mapped_column(
        String(20), default=ScheduleStatus.ACTIVE.value, index=True
    )

    # Assessment configuration
    framework: Mapped[str | None] = mapped_column(String(50), nullable=True)
    include_all_vendors: Mapped[bool] = mapped_column(default=False)

    # Timing
    next_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Run configuration
    notify_on_completion: Mapped[bool] = mapped_column(default=True)
    notify_on_findings: Mapped[bool] = mapped_column(default=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="monitoring_schedules",
    )
    vendor: Mapped["Vendor | None"] = relationship(
        "Vendor",
        back_populates="monitoring_schedules",
    )
    scheduled_runs: Mapped[list["ScheduledRun"]] = relationship(
        "ScheduledRun",
        back_populates="schedule",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<MonitoringSchedule(id={self.id}, name={self.name}, "
            f"frequency={self.frequency}, status={self.status})>"
        )


class ScheduledRun(Base, UUIDMixin, TimestampMixin):
    """Record of a scheduled assessment execution."""

    __tablename__ = "scheduled_runs"

    # Foreign keys
    schedule_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("monitoring_schedules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Run details
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Results
    vendors_assessed: Mapped[int] = mapped_column(Integer, default=0)
    documents_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    findings_generated: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    schedule: Mapped["MonitoringSchedule"] = relationship(
        "MonitoringSchedule",
        back_populates="scheduled_runs",
    )
    organization: Mapped["Organization"] = relationship("Organization")

    def __repr__(self) -> str:
        return (
            f"<ScheduledRun(id={self.id}, schedule_id={self.schedule_id}, "
            f"status={self.status})>"
        )


class AlertRule(Base, UUIDMixin, TimestampMixin):
    """Rule defining when to trigger alerts."""

    __tablename__ = "alert_rules"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Rule details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    # Trigger conditions (stored as JSON)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Alert configuration
    severity: Mapped[str] = mapped_column(
        String(20), default=AlertSeverity.MEDIUM.value
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="alert_rules",
    )
    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="rule",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<AlertRule(id={self.id}, name={self.name}, is_active={self.is_active})>"


class Alert(Base, UUIDMixin, TimestampMixin):
    """Alert instance triggered by a rule."""

    __tablename__ = "alerts"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("alert_rules.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    vendor_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("vendors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Alert details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(
        String(20), default=AlertSeverity.MEDIUM.value, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default=AlertStatus.NEW.value, index=True
    )

    # Context
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Resolution
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    acknowledged_by_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_by_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="alerts",
    )
    rule: Mapped["AlertRule | None"] = relationship(
        "AlertRule",
        back_populates="alerts",
    )
    vendor: Mapped["Vendor | None"] = relationship("Vendor")

    def __repr__(self) -> str:
        return (
            f"<Alert(id={self.id}, title={self.title[:50]}, "
            f"severity={self.severity}, status={self.status})>"
        )


class NotificationChannel(Base, UUIDMixin, TimestampMixin):
    """Configured notification channel for alerts."""

    __tablename__ = "notification_channels"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Channel details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    channel_type: Mapped[str] = mapped_column(
        String(20), default=NotificationChannelType.EMAIL.value
    )
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    # Configuration (stored as JSON)
    config: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Usage tracking
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failure_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="notification_channels",
    )

    def __repr__(self) -> str:
        return (
            f"<NotificationChannel(id={self.id}, name={self.name}, "
            f"type={self.channel_type}, active={self.is_active})>"
        )
