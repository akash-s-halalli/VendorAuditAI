"""Organization model for multi-tenant support."""

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.finding import AnalysisRun, Finding
    from app.models.query import ConversationThread, QueryHistory
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

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"
