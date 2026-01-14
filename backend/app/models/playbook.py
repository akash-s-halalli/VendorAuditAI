"""AI Governance Playbook models for guided AI tool adoption workflows."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.vendor import Vendor


class PlaybookPhase(str, Enum):
    """Phase of AI governance playbook."""

    TOOL_SELECTION = "tool_selection"
    DEPLOYMENT = "deployment"
    REGRESSION_PROTECTION = "regression_protection"


class TargetAudience(str, Enum):
    """Target audience for playbook."""

    TECHNICAL = "technical"
    NON_TECHNICAL = "non_technical"
    ALL = "all"


class Department(str, Enum):
    """Department for playbook targeting."""

    MARKETING = "marketing"
    HR = "hr"
    FINANCE = "finance"
    ENGINEERING = "engineering"
    OPERATIONS = "operations"
    LEGAL = "legal"
    ALL = "all"


class PlaybookProgressStatus(str, Enum):
    """Status of playbook progress."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ApprovalStatus(str, Enum):
    """Status of playbook step approval."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AIPlaybook(Base, UUIDMixin, TimestampMixin):
    """AI Governance Playbook template.

    Defines a reusable playbook for guiding users through AI tool
    adoption processes (selection, deployment, regression protection).
    """

    __tablename__ = "ai_playbooks"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Playbook info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    phase: Mapped[str] = mapped_column(
        String(50),
        default=PlaybookPhase.TOOL_SELECTION.value,
        nullable=False,
    )
    target_audience: Mapped[str] = mapped_column(
        String(50),
        default=TargetAudience.ALL.value,
        nullable=False,
    )
    department: Mapped[str] = mapped_column(
        String(50),
        default=Department.ALL.value,
        nullable=False,
    )

    # Version and status
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Metadata
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="playbooks",
    )
    created_by: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[created_by_id],
    )
    steps: Mapped[list["PlaybookStep"]] = relationship(
        "PlaybookStep",
        back_populates="playbook",
        cascade="all, delete-orphan",
        order_by="PlaybookStep.step_number",
    )
    progress_records: Mapped[list["PlaybookProgress"]] = relationship(
        "PlaybookProgress",
        back_populates="playbook",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<AIPlaybook(id={self.id}, name={self.name}, phase={self.phase})>"

    @property
    def total_steps(self) -> int:
        """Get total number of steps in playbook."""
        return len(self.steps) if self.steps else 0


class PlaybookStep(Base, UUIDMixin, TimestampMixin):
    """Individual step within a playbook.

    Each step contains instructions, checklists, and approval requirements
    for completing a portion of the AI governance process.
    """

    __tablename__ = "playbook_steps"

    # Foreign keys
    playbook_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_playbooks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Step info
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)

    # Checklist items (JSON array)
    checklist: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Approval requirements (JSON array of role names)
    required_approvals: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Time estimate
    estimated_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Resources (JSON array of {title, url, type})
    resources: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optional fields
    tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    warning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    playbook: Mapped["AIPlaybook"] = relationship(
        "AIPlaybook",
        back_populates="steps",
    )

    def __repr__(self) -> str:
        return f"<PlaybookStep(id={self.id}, step={self.step_number}, title={self.title})>"


class PlaybookProgress(Base, UUIDMixin, TimestampMixin):
    """Tracks a user's progress through a playbook for a specific vendor.

    Records which steps have been completed and overall progress status.
    """

    __tablename__ = "playbook_progress"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    playbook_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_playbooks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("vendors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Progress tracking
    current_step: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=PlaybookProgressStatus.NOT_STARTED.value,
        nullable=False,
    )

    # Step completions (JSON object: {step_id: {completed, completed_at, notes, checklist_status}})
    step_completions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Progress percentage
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    user: Mapped["User"] = relationship("User")
    playbook: Mapped["AIPlaybook"] = relationship(
        "AIPlaybook",
        back_populates="progress_records",
    )
    vendor: Mapped["Vendor | None"] = relationship("Vendor")
    approvals: Mapped[list["PlaybookApproval"]] = relationship(
        "PlaybookApproval",
        back_populates="progress",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<PlaybookProgress(id={self.id}, status={self.status}, step={self.current_step})>"


class PlaybookApproval(Base, UUIDMixin, TimestampMixin):
    """Approval request for a playbook step.

    When a step requires approval, this tracks the request and response.
    """

    __tablename__ = "playbook_approvals"

    # Foreign keys
    progress_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("playbook_progress.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("playbook_steps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requested_by_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    approver_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Approval info
    status: Mapped[str] = mapped_column(
        String(50),
        default=ApprovalStatus.PENDING.value,
        nullable=False,
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Required role for approval
    required_role: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Timestamps
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    progress: Mapped["PlaybookProgress"] = relationship(
        "PlaybookProgress",
        back_populates="approvals",
    )
    step: Mapped["PlaybookStep"] = relationship("PlaybookStep")
    requested_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[requested_by_id],
    )
    approver: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[approver_id],
    )

    def __repr__(self) -> str:
        return f"<PlaybookApproval(id={self.id}, status={self.status})>"
