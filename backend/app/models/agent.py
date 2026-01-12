"""AI Agent models for autonomous security operations."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class AgentStatus(str, enum.Enum):
    """Agent operational status."""

    ACTIVE = "active"
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    DISABLED = "disabled"


class AgentType(str, enum.Enum):
    """Types of AI agents available."""

    THREAT_DETECTION = "threat_detection"  # Sentinel Prime
    RISK_ASSESSMENT = "risk_assessment"  # Vector Analyst
    VULNERABILITY_SCANNER = "vulnerability_scanner"  # Watchdog Zero
    COMPLIANCE_VERIFICATION = "compliance_verification"  # Audit Core


class Agent(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """AI Agent for autonomous security operations.

    Represents one of four specialized agents:
    - Sentinel Prime: Threat Detection
    - Vector Analyst: Risk Assessment
    - Watchdog Zero: Vulnerability Scanning
    - Audit Core: Compliance Verification
    """

    __tablename__ = "agents"

    # Agent identity
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_type: Mapped[AgentType] = mapped_column(
        Enum(AgentType), nullable=False
    )
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status and health
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus), default=AgentStatus.IDLE, nullable=False
    )
    uptime_percentage: Mapped[float] = mapped_column(
        Float, default=100.0, nullable=False
    )
    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Configuration
    configuration: Mapped[dict] = mapped_column(
        JSON, default=dict, nullable=False
    )

    # Organization association
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="agents"
    )
    tasks: Mapped[list["AgentTask"]] = relationship(
        "AgentTask", back_populates="agent", cascade="all, delete-orphan"
    )
    logs: Mapped[list["AgentLog"]] = relationship(
        "AgentLog", back_populates="agent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Agent {self.name} ({self.agent_type.value}) - {self.status.value}>"


class TaskStatus(str, enum.Enum):
    """Agent task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, enum.Enum):
    """Types of tasks agents can execute."""

    SCAN = "scan"
    ANALYZE = "analyze"
    REPORT = "report"
    MONITOR = "monitor"
    AUDIT = "audit"


class AgentTask(Base, UUIDMixin, TimestampMixin):
    """Task executed by an AI agent.

    Tracks individual task executions with input/output data and timing.
    """

    __tablename__ = "agent_tasks"

    # Task identity
    agent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    task_type: Mapped[TaskType] = mapped_column(
        Enum(TaskType), nullable=False
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False
    )

    # Task data
    input_data: Mapped[dict] = mapped_column(
        JSON, default=dict, nullable=False
    )
    output_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Results summary
    items_processed: Mapped[int | None] = mapped_column(nullable=True)
    findings_count: Mapped[int | None] = mapped_column(nullable=True)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<AgentTask {self.id[:8]} - {self.task_type.value} ({self.status.value})>"


class LogLevel(str, enum.Enum):
    """Log entry severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class AgentLog(Base, UUIDMixin, TimestampMixin):
    """Log entry from an AI agent.

    Captures operational logs for monitoring and debugging.
    """

    __tablename__ = "agent_logs"

    # Association
    agent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("agent_tasks.id", ondelete="SET NULL"), nullable=True
    )

    # Log content
    level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel), default=LogLevel.INFO, nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="logs")

    def __repr__(self) -> str:
        return f"<AgentLog [{self.level.value}] {self.message[:50]}>"
