"""Integration Hub models for external system integrations.

Provides models for connecting VendorAuditAI with external systems like
Jira, ServiceNow, Slack, Microsoft Teams, and custom webhooks.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class IntegrationType(str, Enum):
    """Types of external integrations supported."""

    JIRA = "jira"
    SERVICENOW = "servicenow"
    SLACK = "slack"
    WEBHOOK = "webhook"
    EMAIL = "email"
    TEAMS = "teams"


class IntegrationStatus(str, Enum):
    """Status of an integration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING_SETUP = "pending_setup"


class IntegrationLogAction(str, Enum):
    """Types of actions logged for integrations."""

    SYNC = "sync"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    TEST = "test"
    WEBHOOK_RECEIVED = "webhook_received"


class IntegrationLogStatus(str, Enum):
    """Status of an integration log entry."""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class IntegrationEntityType(str, Enum):
    """Entity types that can be mapped in integrations."""

    VENDOR = "vendor"
    FINDING = "finding"
    REMEDIATION_TASK = "remediation_task"
    DOCUMENT = "document"


class Integration(Base, UUIDMixin, TimestampMixin):
    """External system integration configuration.

    Stores connection details and state for integrations with external
    systems like Jira, ServiceNow, Slack, etc.
    """

    __tablename__ = "integrations"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )

    # Integration details
    integration_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Configuration (encrypted sensitive fields handled at application layer)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    credentials: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sync_settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Enable/disable toggle
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(50),
        default=IntegrationStatus.PENDING_SETUP.value,
        nullable=False,
        index=True,
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sync_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="integrations",
    )
    created_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_id],
    )
    mappings: Mapped[list["IntegrationMapping"]] = relationship(
        "IntegrationMapping",
        back_populates="integration",
        cascade="all, delete-orphan",
    )
    logs: Mapped[list["IntegrationLog"]] = relationship(
        "IntegrationLog",
        back_populates="integration",
        cascade="all, delete-orphan",
        order_by="IntegrationLog.created_at.desc()",
    )
    webhook_endpoints: Mapped[list["WebhookEndpoint"]] = relationship(
        "WebhookEndpoint",
        back_populates="integration",
    )

    def __repr__(self) -> str:
        return (
            f"<Integration(id={self.id}, name={self.name}, "
            f"type={self.integration_type}, status={self.status})>"
        )

    @property
    def is_active(self) -> bool:
        """Check if the integration is active."""
        return self.status == IntegrationStatus.ACTIVE.value

    @property
    def has_error(self) -> bool:
        """Check if the integration is in error state."""
        return self.status == IntegrationStatus.ERROR.value


class IntegrationMapping(Base, UUIDMixin, TimestampMixin):
    """Field mapping between VendorAuditAI and external systems.

    Defines how fields in local entities map to fields in the integrated
    external system, including optional transformation rules.
    """

    __tablename__ = "integration_mappings"

    # Foreign keys
    integration_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integrations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Mapping details
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    local_field: Mapped[str] = mapped_column(String(255), nullable=False)
    remote_field: Mapped[str] = mapped_column(String(255), nullable=False)
    transform: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_bidirectional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    integration: Mapped["Integration"] = relationship(
        "Integration",
        back_populates="mappings",
    )

    def __repr__(self) -> str:
        return (
            f"<IntegrationMapping(id={self.id}, entity={self.entity_type}, "
            f"local={self.local_field}, remote={self.remote_field})>"
        )


class IntegrationLog(Base, UUIDMixin):
    """Log entry for integration sync operations.

    Tracks all sync activities, including success/failure status,
    request/response data for debugging, and timing information.
    """

    __tablename__ = "integration_logs"

    # Foreign keys
    integration_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integrations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Log details
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Entity reference (optional)
    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Request/response data for debugging
    request_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    response_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Performance tracking
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamp (only created_at, logs are immutable)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
    )

    # Relationships
    integration: Mapped["Integration"] = relationship(
        "Integration",
        back_populates="logs",
    )

    def __repr__(self) -> str:
        return (
            f"<IntegrationLog(id={self.id}, integration_id={self.integration_id}, "
            f"action={self.action}, status={self.status})>"
        )

    @property
    def is_success(self) -> bool:
        """Check if the log entry represents a successful operation."""
        return self.status == IntegrationLogStatus.SUCCESS.value

    @property
    def is_failed(self) -> bool:
        """Check if the log entry represents a failed operation."""
        return self.status == IntegrationLogStatus.FAILED.value


class WebhookEndpoint(Base, UUIDMixin, TimestampMixin):
    """Incoming webhook endpoint configuration.

    Defines endpoints that can receive webhook calls from external systems,
    with secret-based signature validation.
    """

    __tablename__ = "webhook_endpoints"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    integration_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("integrations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Endpoint details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    endpoint_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    secret: Mapped[str] = mapped_column(String(255), nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    trigger_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="webhook_endpoints",
    )
    integration: Mapped["Integration | None"] = relationship(
        "Integration",
        back_populates="webhook_endpoints",
    )

    def __repr__(self) -> str:
        return (
            f"<WebhookEndpoint(id={self.id}, name={self.name}, "
            f"key={self.endpoint_key[:8]}..., active={self.is_active})>"
        )
