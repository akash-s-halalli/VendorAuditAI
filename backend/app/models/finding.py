"""Finding model for analysis results."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.organization import Organization


class FindingSeverity(str, Enum):
    """Severity level for findings."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingStatus(str, Enum):
    """Status of a finding."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    REMEDIATED = "remediated"
    ACCEPTED = "accepted"
    FALSE_POSITIVE = "false_positive"


class AnalysisRun(Base, UUIDMixin, TimestampMixin):
    """Analysis run tracking model.

    Tracks each analysis execution for a document.
    """

    __tablename__ = "analysis_runs"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Analysis configuration
    framework: Mapped[str] = mapped_column(String(50), nullable=False)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metrics
    chunks_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    findings_count: Mapped[int] = mapped_column(Integer, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Summary
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="analysis_runs",
    )
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="analysis_runs",
    )
    findings: Mapped[List["Finding"]] = relationship(
        "Finding",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<AnalysisRun(id={self.id}, document_id={self.document_id}, "
            f"framework={self.framework}, status={self.status})>"
        )


class Finding(Base, UUIDMixin, TimestampMixin):
    """Finding model for analysis results.

    Represents a gap, concern, or finding identified during document analysis.
    """

    __tablename__ = "findings"

    # Foreign keys
    analysis_run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Finding details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), default=FindingSeverity.MEDIUM.value
    )
    status: Mapped[str] = mapped_column(
        String(20), default=FindingStatus.OPEN.value
    )

    # Framework reference
    framework: Mapped[str] = mapped_column(String(50), nullable=False)
    framework_control: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Content
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Citation
    chunk_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_header: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Confidence
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # User response
    user_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship(
        "AnalysisRun",
        back_populates="findings",
    )
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="findings",
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="findings",
    )

    def __repr__(self) -> str:
        return (
            f"<Finding(id={self.id}, title={self.title[:50]}, "
            f"severity={self.severity}, status={self.status})>"
        )

    @property
    def is_open(self) -> bool:
        """Check if finding is still open."""
        return self.status == FindingStatus.OPEN.value

    @property
    def is_resolved(self) -> bool:
        """Check if finding has been resolved."""
        return self.status in [
            FindingStatus.REMEDIATED.value,
            FindingStatus.ACCEPTED.value,
            FindingStatus.FALSE_POSITIVE.value,
        ]
