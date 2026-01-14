"""Pydantic schemas for BPO (Business Process Outsourcing) risk management."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


# --- Enums ---

class ServiceType(str, Enum):
    """Types of BPO services provided."""
    CALL_CENTER = "call_center"
    BACK_OFFICE = "back_office"
    IT_SERVICES = "it_services"
    FINANCE = "finance"
    HR = "hr"
    LEGAL = "legal"
    OTHER = "other"


class ProcessCategory(str, Enum):
    """Categories of business processes outsourced."""
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
    """Level of data access granted to BPO provider."""
    NONE = "none"
    LIMITED = "limited"
    STANDARD = "standard"
    ELEVATED = "elevated"
    FULL = "full"


class Criticality(str, Enum):
    """Criticality level of a process or provider."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ControlType(str, Enum):
    """Type of control implementation."""
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"


class ControlCategory(str, Enum):
    """Category of control."""
    ACCESS = "access"
    DATA = "data"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"


class ControlStatus(str, Enum):
    """Implementation status of a control."""
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    NOT_IMPLEMENTED = "not_implemented"
    NOT_APPLICABLE = "not_applicable"


class TestResult(str, Enum):
    """Test result for a control."""
    PASSED = "passed"
    FAILED = "failed"
    NOT_TESTED = "not_tested"


class AssessmentType(str, Enum):
    """Type of BPO assessment."""
    INITIAL = "initial"
    PERIODIC = "periodic"
    INCIDENT_TRIGGERED = "incident_triggered"


class AssessmentStatus(str, Enum):
    """Status of a BPO assessment."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


# =============================================================================
# BPO Provider Schemas
# =============================================================================


class BPOProviderCreate(BaseModel):
    """Schema for creating a new BPO provider."""
    vendor_id: str = Field(..., description="ID of the linked vendor")
    service_type: str = Field(default="other", description="Primary service type")
    process_category: str = Field(default="other", description="Process category")
    geographic_locations: str | None = Field(default=None, description="JSON list of locations")
    data_access_level: str = Field(default="none", description="Data access level")
    employee_count: int | None = Field(default=None, ge=0, description="Employee count")
    contract_value: float | None = Field(default=None, ge=0, description="Contract value")
    sla_requirements: str | None = Field(default=None, description="SLA requirements (JSON)")
    primary_contact_name: str | None = Field(default=None, max_length=255)
    primary_contact_email: str | None = Field(default=None, max_length=255)
    contract_start_date: date | None = Field(default=None)
    contract_end_date: date | None = Field(default=None)


class BPOProviderUpdate(BaseModel):
    """Schema for updating a BPO provider."""
    service_type: str | None = None
    process_category: str | None = None
    geographic_locations: str | None = None
    data_access_level: str | None = None
    employee_count: int | None = None
    contract_value: float | None = None
    sla_requirements: str | None = None
    primary_contact_name: str | None = None
    primary_contact_email: str | None = None
    contract_start_date: date | None = None
    contract_end_date: date | None = None


class BPOProviderResponse(BaseModel):
    """Schema for BPO provider response."""
    id: str
    vendor_id: str
    organization_id: str
    service_type: str
    process_category: str
    geographic_locations: str | None = None
    data_access_level: str
    employee_count: int | None = None
    contract_value: float | None = None
    sla_requirements: str | None = None
    primary_contact_name: str | None = None
    primary_contact_email: str | None = None
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BPOProviderDetailResponse(BPOProviderResponse):
    """Schema for BPO provider detail response with processes."""
    processes: list["BPOProcessResponse"] = Field(default_factory=list)


class BPOProviderListResponse(BaseModel):
    """Schema for paginated BPO provider list."""
    data: list[BPOProviderResponse]
    total: int
    page: int
    limit: int


# =============================================================================
# BPO Process Schemas
# =============================================================================


class BPOProcessCreate(BaseModel):
    """Schema for creating a new BPO process."""
    process_name: str = Field(..., min_length=2, max_length=255)
    description: str | None = Field(default=None)
    criticality: str = Field(default="medium")
    data_types: str | None = Field(default=None, description="JSON list of data types")
    controls_required: str | None = Field(default=None, description="JSON list of required controls")
    volume_per_month: int | None = Field(default=None, ge=0)


class BPOProcessUpdate(BaseModel):
    """Schema for updating a BPO process."""
    process_name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    criticality: str | None = None
    data_types: str | None = None
    controls_required: str | None = None
    volume_per_month: int | None = None


class BPOProcessResponse(BaseModel):
    """Schema for BPO process response."""
    id: str
    provider_id: str
    process_name: str
    description: str | None = None
    criticality: str
    data_types: str | None = None
    controls_required: str | None = None
    volume_per_month: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BPOProcessListResponse(BaseModel):
    """Schema for paginated BPO process list."""
    data: list[BPOProcessResponse]
    total: int
    page: int
    limit: int


# =============================================================================
# BPO Control Schemas
# =============================================================================


class BPOControlCreate(BaseModel):
    """Schema for creating a new BPO control."""
    control_name: str = Field(..., min_length=2, max_length=255)
    control_description: str | None = Field(default=None)
    control_type: str = Field(default="preventive")
    control_category: str = Field(default="operational")
    status: str = Field(default="not_implemented")
    evidence: str | None = Field(default=None)
    last_tested_date: date | None = Field(default=None)
    test_result: str = Field(default="not_tested")


class BPOControlUpdate(BaseModel):
    """Schema for updating a BPO control."""
    control_name: str | None = Field(default=None, min_length=2, max_length=255)
    control_description: str | None = None
    control_type: str | None = None
    control_category: str | None = None
    status: str | None = None
    evidence: str | None = None
    last_tested_date: date | None = None
    test_result: str | None = None


class BPOControlResponse(BaseModel):
    """Schema for BPO control response."""
    id: str
    process_id: str
    control_name: str
    control_description: str | None = None
    control_type: str
    control_category: str
    status: str
    evidence: str | None = None
    last_tested_date: date | None = None
    test_result: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BPOControlListResponse(BaseModel):
    """Schema for paginated BPO control list."""
    data: list[BPOControlResponse]
    total: int
    page: int
    limit: int


# =============================================================================
# BPO Assessment Schemas
# =============================================================================


class BPOAssessmentCreate(BaseModel):
    """Schema for creating a new BPO assessment."""
    provider_id: str = Field(..., description="ID of the BPO provider being assessed")
    assessment_type: str = Field(default="periodic")
    assessment_date: datetime | None = Field(default=None)
    overall_score: int | None = Field(default=None, ge=0, le=100)
    findings: str | None = Field(default=None, description="JSON list of findings")
    recommendations: str | None = Field(default=None)
    next_review_date: date | None = Field(default=None)


class BPOAssessmentUpdate(BaseModel):
    """Schema for updating a BPO assessment."""
    assessment_type: str | None = None
    assessment_date: datetime | None = None
    status: str | None = None
    overall_score: int | None = Field(default=None, ge=0, le=100)
    findings: str | None = None
    recommendations: str | None = None
    next_review_date: date | None = None


class BPOAssessmentResponse(BaseModel):
    """Schema for BPO assessment response."""
    id: str
    provider_id: str
    organization_id: str
    assessor_id: str | None = None
    assessment_date: datetime | None = None
    assessment_type: str
    overall_score: int | None = None
    findings: str | None = None
    recommendations: str | None = None
    next_review_date: date | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BPOAssessmentListResponse(BaseModel):
    """Schema for paginated BPO assessment list."""
    data: list[BPOAssessmentResponse]
    total: int
    page: int
    limit: int


# =============================================================================
# BPO Dashboard Schemas
# =============================================================================


class BPODashboardStats(BaseModel):
    """Schema for BPO dashboard statistics."""
    total_providers: int = Field(..., description="Total number of BPO providers")
    active_providers: int = Field(..., description="Number of active providers")
    total_processes: int = Field(..., description="Total number of processes")
    critical_processes: int = Field(..., description="Number of critical processes")
    total_assessments: int = Field(..., description="Total number of assessments")
    assessments_in_progress: int = Field(..., description="Assessments currently in progress")
    assessments_overdue: int = Field(..., description="Overdue assessments")
    assessments_completed_this_month: int = Field(
        ...,
        description="Assessments completed in current month"
    )
    total_controls: int = Field(..., description="Total number of controls")
    controls_implemented: int = Field(..., description="Number of implemented controls")
    controls_partial: int = Field(..., description="Number of partially implemented controls")
    controls_not_implemented: int = Field(..., description="Number of not implemented controls")
    average_risk_score: float | None = Field(
        default=None,
        description="Average risk score across all providers"
    )
    providers_by_service_type: dict[str, int] = Field(
        default_factory=dict,
        description="Count of providers by service type"
    )
    providers_by_criticality: dict[str, int] = Field(
        default_factory=dict,
        description="Count of providers by criticality level"
    )
    upcoming_assessments: int = Field(..., description="Number of upcoming assessments")
    contracts_expiring_soon: int = Field(
        ...,
        description="Number of contracts expiring in next 30 days"
    )
