"""Document chunk model for storing parsed and embedded text segments."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document


class DocumentChunk(Base, UUIDMixin, TimestampMixin):
    """Document chunk model for storing text segments with embeddings.

    Chunks are semantic segments of a document optimized for RAG retrieval.
    Each chunk maintains context about its position in the source document.
    """

    __tablename__ = "document_chunks"

    # Foreign keys
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Position metadata
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_header: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Embedding (stored as JSON string for SQLite compatibility)
    # For PostgreSQL with pgvector, this would be a Vector column
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata (JSON)
    metadata_: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunks",
    )

    def __repr__(self) -> str:
        return (
            f"<DocumentChunk(id={self.id}, document_id={self.document_id}, "
            f"index={self.chunk_index}, tokens={self.token_count})>"
        )

    @property
    def has_embedding(self) -> bool:
        """Check if chunk has an embedding."""
        return self.embedding is not None
