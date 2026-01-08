"""Document model for uploaded compliance documents."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.vendor import Vendor


class DocumentType(str, Enum):
    """Type of compliance document."""

    SOC2 = "soc2"
    SIG_LITE = "sig_lite"
    SIG_CORE = "sig_core"
    HECVAT = "hecvat"
    ISO27001 = "iso27001"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Overall document processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class ProcessingStage(str, Enum):
    """Current stage in the document processing pipeline."""

    UPLOADED = "uploaded"
    PARSING = "parsing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    ERROR = "error"


class Document(Base, UUIDMixin, TimestampMixin):
    """Document model for managing uploaded compliance documents.

    Documents belong to an organization and optionally to a vendor.
    They track the processing pipeline status and store metadata about
    the uploaded files.
    """

    __tablename__ = "documents"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("vendors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # File info
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Document classification
    document_type: Mapped[str] = mapped_column(
        String(50), default=DocumentType.OTHER.value
    )

    # Processing status
    status: Mapped[str] = mapped_column(
        String(50), default=DocumentStatus.PENDING.value
    )
    processing_stage: Mapped[str] = mapped_column(
        String(50), default=ProcessingStage.UPLOADED.value
    )

    # Document details
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Processing timestamp
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="documents",
    )
    vendor: Mapped["Vendor | None"] = relationship(
        "Vendor",
        back_populates="documents",
    )

    def __repr__(self) -> str:
        return (
            f"<Document(id={self.id}, filename={self.filename}, "
            f"type={self.document_type}, status={self.status})>"
        )

    @property
    def is_processed(self) -> bool:
        """Check if document has been fully processed."""
        return self.status == DocumentStatus.PROCESSED.value

    @property
    def has_error(self) -> bool:
        """Check if document processing encountered an error."""
        return (
            self.status == DocumentStatus.FAILED.value
            or self.processing_stage == ProcessingStage.ERROR.value
        )

    @property
    def is_pending(self) -> bool:
        """Check if document is waiting to be processed."""
        return self.status == DocumentStatus.PENDING.value

    @property
    def is_processing(self) -> bool:
        """Check if document is currently being processed."""
        return self.status == DocumentStatus.PROCESSING.value
