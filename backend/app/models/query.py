"""Query models for conversation history and query tracking."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.document import Document


class QueryStatus(str, Enum):
    """Status of a query."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversationThread(Base, UUIDMixin, TimestampMixin):
    """Model for conversation threads.

    Groups related queries into a conversation for context-aware responses.
    """

    __tablename__ = "conversation_threads"

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

    # Thread metadata
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_filter: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON list of document IDs

    # Metrics
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="conversation_threads",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="conversation_threads",
    )
    queries: Mapped[list["QueryHistory"]] = relationship(
        "QueryHistory",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="QueryHistory.created_at",
    )

    def __repr__(self) -> str:
        return f"<ConversationThread(id={self.id}, messages={self.message_count})>"


class QueryHistory(Base, UUIDMixin, TimestampMixin):
    """Model for storing query history.

    Tracks each query and response for auditing and improvement.
    """

    __tablename__ = "query_history"

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
    conversation_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("conversation_threads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Query content
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    citations: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    # Document context (JSON list of document IDs that were searched)
    document_ids: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), default=QueryStatus.PENDING.value
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metrics
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    chunks_retrieved: Mapped[int] = mapped_column(Integer, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="query_history",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="query_history",
    )
    conversation: Mapped["ConversationThread | None"] = relationship(
        "ConversationThread",
        back_populates="queries",
    )

    def __repr__(self) -> str:
        return f"<QueryHistory(id={self.id}, status={self.status})>"
