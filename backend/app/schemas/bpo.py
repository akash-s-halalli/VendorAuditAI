"""Pydantic schemas for BPO (Business Process Outsourcing) risk management."""

from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


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


# --- BPO Provider Schemas ---

class BPOProviderBase(BaseModel):
    """Base schema for BPO provider."""

    name: str = Field(..., min_length=2, max_length=255, description="Provider name")
    description: str | None = Field(default=None, description="Provider description")
    service_type: ServiceType = Field(..., description="Primary service type")
    country: str | None = Field(default=None, max_length=100, description="Provider country")
    city: str | None = Field(default=None, max_length=100, description="Provider city")
    contact_name: str | None = Field(default=None, max_length=255, description="Primary contact name")
    contact_email: str | None = Field(default=None, max_length=255, description="Primary contact email")
    contact_phone: str | None = Field(default=None, max_length=50, description="Primary contact phone")
    contract_start_date: date | None = Field(default=None, description="Contract start date")
    contract_end_date: date | None = Field(default=None, description="Contract end date")
    data_access_level: DataAccessLevel = Field(
        default=DataAccessLevel.LIMITED,
        description="Level of data access granted"
    )
    criticality: Criticality = Field(
        default=Criticality.MEDIUM,
        description="Overall criticality rating"
    )
    employee_count: int | None = Field(default=None, ge=0, description="Number of employees at provider")
    certifications: list[str] | None = Field(default=None, description="List of certifications held")
    tags: list[str] | None = Field(default=None, description="Custom tags for categorization")


class BPOProviderCreate(BPOProviderBase):
    """Schema for creating a new BPO provider."""

    pass


class BPOProviderUpdate(BaseModel):
    """Schema for updating a BPO provider (partial updates)."""

    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    service_type: ServiceType | None = None
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    contact_name: str | None = Field(default=None, max_length=255)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    data_access_level: DataAccessLevel | None = None
    criticality: Criticality | None = None
    employee_count: int | None = Field(default=None, ge=0)
    certifications: list[str] | None = None
    tags: list[str] | None = None


class BPOProcessResponse(BaseModel):
    """Schema for BPO process response."""

    id: str
    provider_id: str
    name: str
    description: str | None = None
    category: ProcessCategory
    criticality: Criticality
    data_types_handled: list[str] | None = None
    volume_per_month: int | None = None
    sla_response_time_hours: int | None = None
    sla_resolution_time_hours: int | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("data_types_handled", mode="before")
    @classmethod
    def parse_data_types(cls, v: str | list | None) -> list[str] | None:
        """Parse JSON string to list if needed."""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return None


class BPOControlResponse(BaseModel):
    """Schema for BPO control response."""

    id: str
    process_id: str
    name: str
    description: str | None = None
    control_type: ControlType
    control_category: ControlCategory
    status: ControlStatus
    effectiveness_score: int | None = Field(default=None, ge=0, le=100)
    last_tested: datetime | None = None
    next_test_due: date | None = None
    evidence_required: bool = True
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BPOProviderResponse(BPOProviderBase):
    """Schema for BPO provider response."""

    id: str
    organization_id: str
    risk_score: float | None = Field(default=None, ge=0, le=100)
    last_assessed: datetime | None = None
    next_assessment_due: date | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("certifications", "tags", mode="before")
    @classmethod
    def parse_json_list(cls, v: str | list | None) -> list[str] | None:
        """Parse JSON string to list if needed."""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return None


class BPOProviderDetailResponse(BPOProviderResponse):
    """Schema for detailed BPO provider response with processes."""

    processes: list[BPOProcessResponse] = Field(default_factory=list)


class BPOProviderListResponse(BaseModel):
    """Schema for paginated BPO provider list response."""

    data: list[BPOProviderResponse]
    total: int
    page: int
    limit: int


# --- BPO Process Schemas ---

class BPOProcessBase(BaseModel):
    """Base schema for BPO process."""

    name: str = Field(..., min_length=2, max_length=255, description="Process name")
    description: str | None = Field(default=None, description="Process description")
    category: ProcessCategory = Field(..., description="Process category")
    criticality: Criticality = Field(
        default=Criticality.MEDIUM,
        description="Process criticality"
    )
    data_types_handled: list[str] | None = Field(
        default=None,
        description="Types of data handled by this process"
    )
    volume_per_month: int | None = Field(
        default=None,
        ge=0,
        description="Average monthly transaction volume"
    )
    sla_response_time_hours: int | None = Field(
        default=None,
        ge=0,
        description="SLA response time in hours"
    )
    sla_resolution_time_hours: int | None = Field(
        default=None,
        ge=0,
        description="SLA resolution time in hours"
    )
    is_active: bool = Field(default=True, description="Whether process is currently active")


class BPOProcessCreate(BPOProcessBase):
    """Schema for creating a new BPO process."""

    pass


class BPOProcessUpdate(BaseModel):
    """Schema for updating a BPO process."""

    process_name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    category: ProcessCategory | None = None
    criticality: Criticality | None = None
    data_types_handled: list[str] | None = None
    volume_per_month: int | None = None
    is_active: bool | None = None


class BPOProcessListResponse(BaseModel):
    """Schema for paginated BPO process list response."""

    data: list[BPOProcessResponse]
    total: int
    page: int
    limit: int


# --- BPO Assessment Schemas ---

class BPOAssessmentBase(BaseModel):
    """Base schema for BPO assessment."""

    provider_id: str = Field(..., description="ID of the BPO provider being assessed")
    assessment_type: AssessmentType = Field(..., description="Type of assessment")
    scheduled_date: date = Field(..., description="Scheduled date for the assessment")
    title: str = Field(..., min_length=2, max_length=255, description="Assessment title")
    description: str | None = Field(default=None, description="Assessment description")
    scope: list[str] | None = Field(
        default=None,
        description="List of areas/processes in scope"
    )


class BPOAssessmentCreate(BPOAssessmentBase):
    """Schema for creating a new BPO assessment."""

    pass


class BPOAssessmentUpdate(BaseModel):
    """Schema for updating a BPO assessment."""

    status: AssessmentStatus | None = None
    scheduled_date: date | None = None
    completed_date: date | None = None
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    scope: list[str] | None = None
    findings_summary: str | None = None
    overall_rating: Literal["satisfactory", "needs_improvement", "unsatisfactory"] | None = None
    risk_score: float | None = Field(default=None, ge=0, le=100)
    recommendations: list[str] | None = None


class BPOAssessmentResponse(BaseModel):
    """Schema for BPO assessment response."""

    id: str
    organization_id: str
    provider_id: str
    assessor_id: str
    assessment_type: AssessmentType
    status: AssessmentStatus
    scheduled_date: date
    completed_date: date | None = None
    title: str
    description: str | None = None
    scope: list[str] | None = None
    findings_summary: str | None = None
    overall_rating: str | None = None
    risk_score: float | None = None
    recommendations: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("scope", "recommendations", mode="before")
    @classmethod
    def parse_json_list(cls, v: str | list | None) -> list[str] | None:
        """Parse JSON string to list if needed."""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return None


class BPOAssessmentListResponse(BaseModel):
    """Schema for paginated BPO assessment list response."""

    data: list[BPOAssessmentResponse]
    total: int
    page: int
    limit: int


# --- BPO Control Schemas ---

class BPOControlBase(BaseModel):
    """Base schema for BPO control."""

    name: str = Field(..., min_length=2, max_length=255, description="Control name")
    description: str | None = Field(default=None, description="Control description")
    control_type: ControlType = Field(..., description="Type of control")
    control_category: ControlCategory = Field(..., description="Category of control")
    status: ControlStatus = Field(
        default=ControlStatus.NOT_IMPLEMENTED,
        description="Implementation status"
    )
    effectiveness_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Effectiveness score (0-100)"
    )
    last_tested: datetime | None = Field(default=None, description="Last test date")
    next_test_due: date | None = Field(default=None, description="Next test due date")
    evidence_required: bool = Field(default=True, description="Whether evidence is required")
    notes: str | None = Field(default=None, description="Additional notes")


class BPOControlCreate(BPOControlBase):
    """Schema for creating a new BPO control."""

    pass


class BPOControlUpdate(BaseModel):
    """Schema for updating a BPO control."""

    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    control_type: ControlType | None = None
    control_category: ControlCategory | None = None
    status: ControlStatus | None = None
    effectiveness_score: int | None = Field(default=None, ge=0, le=100)
    last_tested: datetime | None = None
    next_test_due: date | None = None
    evidence_required: bool | None = None
    notes: str | None = None


class BPOControlListResponse(BaseModel):
    """Schema for paginated BPO control list response."""

    data: list[BPOControlResponse]
    total: int
    page: int
    limit: int


# --- Dashboard Stats Schema ---

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
    upcoming_assessments: int = Field(
        ...,
        description="Assessments scheduled in next 30 days"
    )
    contracts_expiring_soon: int = Field(
        ...,
        description="Contracts expiring in next 90 days"
    )
