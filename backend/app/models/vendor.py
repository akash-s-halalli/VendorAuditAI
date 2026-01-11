"""Vendor model for third-party vendor management."""

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.organization import Organization
    from app.models.remediation import RemediationTask


class VendorTier(str, Enum):
    """Vendor tier classification based on risk and importance."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VendorStatus(str, Enum):
    """Vendor lifecycle status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ONBOARDING = "onboarding"
    OFFBOARDING = "offboarding"


class Vendor(Base, UUIDMixin, TimestampMixin):
    """Vendor model for managing third-party vendors.

    Vendors belong to an organization and track risk assessment information,
    contract details, and compliance status.
    """

    __tablename__ = "vendors"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Classification
    tier: Mapped[str] = mapped_column(String(20), default=VendorTier.MEDIUM.value)
    status: Mapped[str] = mapped_column(String(20), default=VendorStatus.ACTIVE.value)
    criticality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_classification: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Contract info
    contract_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Contact and metadata
    primary_contact: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of strings
    extra_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    # Assessment tracking
    last_assessed: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_assessment_due: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="vendors",
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="vendor",
    )
    remediation_tasks: Mapped[list["RemediationTask"]] = relationship(
        "RemediationTask",
        back_populates="vendor",
    )

    def __repr__(self) -> str:
        return f"<Vendor(id={self.id}, name={self.name}, tier={self.tier}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Check if vendor is currently active."""
        return self.status == VendorStatus.ACTIVE.value

    @property
    def is_critical(self) -> bool:
        """Check if vendor is classified as critical tier."""
        return self.tier == VendorTier.CRITICAL.value

    @property
    def needs_assessment(self) -> bool:
        """Check if vendor is due for assessment."""
        if self.next_assessment_due is None:
            return False
        return date.today() >= self.next_assessment_due
