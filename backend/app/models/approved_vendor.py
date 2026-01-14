"""Approved AI Vendor models for self-service registry."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class ApprovalStatus(str, Enum):
    """Approval status for AI vendors."""
    PENDING = "pending"
    APPROVED = "approved"
    CONDITIONAL = "conditional"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNDER_REVIEW = "under_review"


class DeploymentStatus(str, Enum):
    """Deployment status for approved vendors."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_APPROVAL = "pending_approval"


class RequestStatus(str, Enum):
    """Status for new tool requests."""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MORE_INFO_NEEDED = "more_info_needed"


class DataClassification(str, Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ApprovedAIVendor(Base, UUIDMixin, TimestampMixin):
    """Pre-approved AI vendor that business users can adopt."""

    __tablename__ = "approved_ai_vendors"

    # Link to main vendor
    vendor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("vendors.id"), unique=True, nullable=False
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False
    )

    # Approval details
    approval_status: Mapped[str] = mapped_column(
        String(50), default=ApprovalStatus.PENDING.value
    )
    approval_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expiration_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    # Usage restrictions
    approved_departments: Mapped[list | None] = mapped_column(JSON, nullable=True)
    approved_use_cases: Mapped[list | None] = mapped_column(JSON, nullable=True)
    prohibited_uses: Mapped[list | None] = mapped_column(JSON, nullable=True)
    data_classification_limit: Mapped[str] = mapped_column(
        String(50), default=DataClassification.INTERNAL.value
    )

    # Conditions and requirements
    conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    required_training: Mapped[bool] = mapped_column(Boolean, default=False)
    training_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Metadata
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_deployment_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    vendor = relationship("Vendor", back_populates="approved_vendor_entry")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    use_cases = relationship(
        "ApprovedUseCase", back_populates="approved_vendor", cascade="all, delete-orphan"
    )
    deployments = relationship(
        "VendorDeployment", back_populates="approved_vendor", cascade="all, delete-orphan"
    )


class ApprovedUseCase(Base, UUIDMixin, TimestampMixin):
    """Approved use cases for a vendor."""

    __tablename__ = "approved_use_cases"

    approved_vendor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("approved_ai_vendors.id"), nullable=False
    )

    use_case_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_types_allowed: Mapped[list | None] = mapped_column(JSON, nullable=True)
    restrictions: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_prompts: Mapped[list | None] = mapped_column(JSON, nullable=True)
    prohibited_actions: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Relationships
    approved_vendor = relationship("ApprovedAIVendor", back_populates="use_cases")


class VendorDeployment(Base, UUIDMixin, TimestampMixin):
    """Tracks individual deployments of approved vendors."""

    __tablename__ = "vendor_deployments"

    approved_vendor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("approved_ai_vendors.id"), nullable=False
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False
    )
    deployed_by_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # Deployment details
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    team: Mapped[str | None] = mapped_column(String(255), nullable=True)
    use_case: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=DeploymentStatus.PENDING_APPROVAL.value
    )

    # Configuration
    configuration: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    data_classification: Mapped[str] = mapped_column(
        String(50), default=DataClassification.INTERNAL.value
    )

    # Tracking
    activated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    approved_vendor = relationship("ApprovedAIVendor", back_populates="deployments")
    deployed_by = relationship("User")


class AIToolRequest(Base, UUIDMixin, TimestampMixin):
    """Request for new AI tool evaluation."""

    __tablename__ = "ai_tool_requests"

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False
    )
    requested_by_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # Tool info
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tool_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Use case details
    use_case_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_data_types: Mapped[list | None] = mapped_column(JSON, nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(50), default=RequestStatus.SUBMITTED.value
    )
    assigned_reviewer_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # If approved, link to created vendor
    created_vendor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("vendors.id"), nullable=True
    )

    # Relationships
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    assigned_reviewer = relationship("User", foreign_keys=[assigned_reviewer_id])
    created_vendor = relationship("Vendor")
