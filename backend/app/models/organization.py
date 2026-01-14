"""Organization model for multi-tenant support."""

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.audit_log import AuditLog
    from app.models.bpo import BPOAssessment, BPOProvider
    from app.models.document import Document
    from app.models.finding import AnalysisRun, Finding
    from app.models.integration import Integration, WebhookEndpoint
    from app.models.monitoring import Alert, AlertRule, MonitoringSchedule, NotificationChannel
    from app.models.playbook import AIPlaybook
    from app.models.query import ConversationThread, QueryHistory
    from app.models.remediation import RemediationTask, SLAPolicy
    from app.models.user import User
    from app.models.vendor import Vendor


class Organization(Base, UUIDMixin, TimestampMixin):
    """Organization model for multi-tenant isolation.

    Each organization has its own set of users, vendors, and documents.
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    subscription_tier: Mapped[str] = mapped_column(String(50), default="free")
    settings: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    vendors: Mapped[list["Vendor"]] = relationship(
        "Vendor",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    analysis_runs: Mapped[list["AnalysisRun"]] = relationship(
        "AnalysisRun",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    findings: Mapped[list["Finding"]] = relationship(
        "Finding",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    conversation_threads: Mapped[list["ConversationThread"]] = relationship(
        "ConversationThread",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    query_history: Mapped[list["QueryHistory"]] = relationship(
        "QueryHistory",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    remediation_tasks: Mapped[list["RemediationTask"]] = relationship(
        "RemediationTask",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    sla_policies: Mapped[list["SLAPolicy"]] = relationship(
        "SLAPolicy",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    monitoring_schedules: Mapped[list["MonitoringSchedule"]] = relationship(
        "MonitoringSchedule",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    alert_rules: Mapped[list["AlertRule"]] = relationship(
        "AlertRule",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    notification_channels: Mapped[list["NotificationChannel"]] = relationship(
        "NotificationChannel",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    agents: Mapped[list["Agent"]] = relationship(
        "Agent",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    playbooks: Mapped[list["AIPlaybook"]] = relationship(
        "AIPlaybook",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    bpo_providers: Mapped[list["BPOProvider"]] = relationship(
        "BPOProvider",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    bpo_assessments: Mapped[list["BPOAssessment"]] = relationship(
        "BPOAssessment",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    integrations: Mapped[list["Integration"]] = relationship(
        "Integration",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    webhook_endpoints: Mapped[list["WebhookEndpoint"]] = relationship(
        "WebhookEndpoint",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"
