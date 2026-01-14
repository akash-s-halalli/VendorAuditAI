"""BPO Risk Management models for managing Business Process Outsourcing providers."""

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.vendor import Vendor


class BPOServiceType(str, Enum):
    """Types of BPO services provided."""

    CALL_CENTER = "call_center"
    BACK_OFFICE = "back_office"
    IT_SERVICES = "it_services"
    FINANCE = "finance"
    HR = "hr"
    LEGAL = "legal"
    OTHER = "other"


class BPOProcessCategory(str, Enum):
    """Categories of BPO processes."""

    CUSTOMER_SUPPORT = "customer_support"
    DATA_PROCESSING = "data_processing"
    SOFTWARE_DEV = "software_dev"
    ACCOUNTING = "accounting"
    RECRUITMENT = "recruitment"
    PAYROLL = "payroll"
    CLAIMS_PROCESSING = "claims_processing"
    CONTENT_MODERATION = "content_moderation"
    RESEARCH = "research"
    OTHER = "other"


class DataAccessLevel(str, Enum):
    """Data access levels for BPO providers."""

    NONE = "none"
    LIMITED = "limited"
    STANDARD = "standard"
    ELEVATED = "elevated"
    FULL = "full"


class ProcessCriticality(str, Enum):
    """Criticality levels for BPO processes."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssessmentType(str, Enum):
    """Types of BPO assessments."""

    INITIAL = "initial"
    PERIODIC = "periodic"
    INCIDENT_TRIGGERED = "incident_triggered"


class AssessmentStatus(str, Enum):
    """Status of BPO assessments."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class ControlType(str, Enum):
    """Types of BPO controls."""

    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"


class ControlCategory(str, Enum):
    """Categories of BPO controls."""

    ACCESS = "access"
    DATA = "data"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"


class ControlStatus(str, Enum):
    """Implementation status of BPO controls."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    NOT_IMPLEMENTED = "not_implemented"
    NOT_APPLICABLE = "not_applicable"


class TestResult(str, Enum):
    """Test results for BPO controls."""

    PASSED = "passed"
    FAILED = "failed"
    NOT_TESTED = "not_tested"


class BPOProvider(Base, UUIDMixin, TimestampMixin):
    """BPO Provider model for managing Business Process Outsourcing providers.

    Tracks BPO providers with their service details, contract information,
    and data access levels for comprehensive third-party risk management.
    """

    __tablename__ = "bpo_providers"

    # Foreign keys
    vendor_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Service classification
    service_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=BPOServiceType.OTHER.value,
    )
    process_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=BPOProcessCategory.OTHER.value,
    )

    # Geographic and access details
    geographic_locations: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON list of locations
    data_access_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DataAccessLevel.NONE.value,
    )

    # Operational details
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contract_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    sla_requirements: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON object with SLA details

    # Contact information
    primary_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Contract dates
    contract_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    contract_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    vendor: Mapped["Vendor"] = relationship(
        "Vendor",
        back_populates="bpo_provider",
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="bpo_providers",
    )
    processes: Mapped[list["BPOProcess"]] = relationship(
        "BPOProcess",
        back_populates="provider",
        cascade="all, delete-orphan",
    )
    assessments: Mapped[list["BPOAssessment"]] = relationship(
        "BPOAssessment",
        back_populates="provider",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<BPOProvider(id={self.id}, vendor_id={self.vendor_id}, service_type={self.service_type})>"

    @property
    def is_high_risk(self) -> bool:
        """Check if provider has elevated or full data access."""
        return self.data_access_level in [
            DataAccessLevel.ELEVATED.value,
            DataAccessLevel.FULL.value,
        ]

    @property
    def contract_active(self) -> bool:
        """Check if contract is currently active."""
        today = date.today()
        if self.contract_start_date and self.contract_end_date:
            return self.contract_start_date <= today <= self.contract_end_date
        return False


class BPOProcess(Base, UUIDMixin, TimestampMixin):
    """BPO Process model for tracking specific processes handled by providers.

    Each process represents a distinct business function outsourced to a BPO provider,
    with its own criticality level, data types, and control requirements.
    """

    __tablename__ = "bpo_processes"

    # Foreign keys
    provider_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("bpo_providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Process details
    process_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    criticality: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ProcessCriticality.MEDIUM.value,
    )

    # Data and control requirements
    data_types: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON list of data types accessed
    controls_required: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON list of required controls

    # Volume metrics
    volume_per_month: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    provider: Mapped["BPOProvider"] = relationship(
        "BPOProvider",
        back_populates="processes",
    )
    controls: Mapped[list["BPOControl"]] = relationship(
        "BPOControl",
        back_populates="process",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<BPOProcess(id={self.id}, name={self.process_name}, criticality={self.criticality})>"

    @property
    def is_critical(self) -> bool:
        """Check if process is classified as critical."""
        return self.criticality == ProcessCriticality.CRITICAL.value


class BPOAssessment(Base, UUIDMixin, TimestampMixin):
    """BPO Assessment model for tracking risk assessments of providers.

    Assessments evaluate BPO providers against security and compliance requirements,
    capturing findings, scores, and recommendations.
    """

    __tablename__ = "bpo_assessments"

    # Foreign keys
    provider_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("bpo_providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assessor_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Assessment details
    assessment_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    assessment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=AssessmentType.PERIODIC.value,
    )

    # Scoring and findings
    overall_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100
    findings: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON list of finding objects
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status and scheduling
    next_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=AssessmentStatus.SCHEDULED.value,
    )

    # Relationships
    provider: Mapped["BPOProvider"] = relationship(
        "BPOProvider",
        back_populates="assessments",
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="bpo_assessments",
    )
    assessor: Mapped["User"] = relationship(
        "User",
        back_populates="bpo_assessments",
    )

    def __repr__(self) -> str:
        return f"<BPOAssessment(id={self.id}, provider_id={self.provider_id}, status={self.status})>"

    @property
    def is_overdue(self) -> bool:
        """Check if assessment is overdue for review."""
        if self.next_review_date:
            return date.today() > self.next_review_date
        return False

    @property
    def risk_level(self) -> str:
        """Determine risk level based on overall score."""
        if self.overall_score is None:
            return "unknown"
        if self.overall_score >= 80:
            return "low"
        if self.overall_score >= 60:
            return "medium"
        if self.overall_score >= 40:
            return "high"
        return "critical"


class BPOControl(Base, UUIDMixin, TimestampMixin):
    """BPO Control model for tracking controls implemented for processes.

    Controls represent specific security and compliance measures in place
    for BPO processes, with testing and validation tracking.
    """

    __tablename__ = "bpo_controls"

    # Foreign keys
    process_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("bpo_processes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Control details
    control_name: Mapped[str] = mapped_column(String(255), nullable=False)
    control_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    control_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ControlType.PREVENTIVE.value,
    )
    control_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ControlCategory.OPERATIONAL.value,
    )

    # Implementation status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ControlStatus.NOT_IMPLEMENTED.value,
    )
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Testing information
    last_tested_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    test_result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=TestResult.NOT_TESTED.value,
    )

    # Relationships
    process: Mapped["BPOProcess"] = relationship(
        "BPOProcess",
        back_populates="controls",
    )

    def __repr__(self) -> str:
        return f"<BPOControl(id={self.id}, name={self.control_name}, status={self.status})>"

    @property
    def is_effective(self) -> bool:
        """Check if control is implemented and passing tests."""
        return (
            self.status == ControlStatus.IMPLEMENTED.value
            and self.test_result == TestResult.PASSED.value
        )

    @property
    def needs_testing(self) -> bool:
        """Check if control has never been tested or test is outdated."""
        if self.last_tested_date is None:
            return True
        # Controls should be tested at least annually
        from datetime import timedelta
        return date.today() - self.last_tested_date > timedelta(days=365)
