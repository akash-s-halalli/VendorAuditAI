"""Pydantic schemas for Approved AI Vendor Registry."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Re-export enums for use in API layer
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


# -----------------------------------------------------------------------------
# Approved Vendor Schemas
# -----------------------------------------------------------------------------

class ApprovedVendorCreate(BaseModel):
    """Schema for creating an approved vendor entry."""
    model_config = ConfigDict(from_attributes=True)

    vendor_id: str = Field(..., description="ID of the vendor to approve")
    organization_id: str = Field(..., description="Organization ID")
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING,
        description="Current approval status"
    )
    expiration_date: datetime | None = Field(
        default=None,
        description="When the approval expires"
    )
    approved_by_id: str | None = Field(
        default=None,
        description="ID of the user who approved"
    )
    approved_departments: list[str] | None = Field(
        default=None,
        description="List of departments allowed to use this vendor"
    )
    approved_use_cases: list[str] | None = Field(
        default=None,
        description="List of approved use cases"
    )
    prohibited_uses: list[str] | None = Field(
        default=None,
        description="List of prohibited uses"
    )
    data_classification_limit: DataClassification = Field(
        default=DataClassification.INTERNAL,
        description="Maximum data classification allowed"
    )
    conditions: str | None = Field(
        default=None,
        description="Conditions for approval"
    )
    required_settings: dict[str, Any] | None = Field(
        default=None,
        description="Required configuration settings"
    )
    required_training: bool = Field(
        default=False,
        description="Whether training is required before use"
    )
    training_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL to training materials"
    )
    review_notes: str | None = Field(
        default=None,
        description="Notes from the review process"
    )
    risk_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Risk score from 0-100"
    )
    max_deployment_count: int | None = Field(
        default=None,
        ge=1,
        description="Maximum number of deployments allowed"
    )


class ApprovedVendorUpdate(BaseModel):
    """Schema for updating an approved vendor (all fields optional)."""
    model_config = ConfigDict(from_attributes=True)

    approval_status: ApprovalStatus | None = Field(
        default=None,
        description="Current approval status"
    )
    expiration_date: datetime | None = Field(
        default=None,
        description="When the approval expires"
    )
    approved_by_id: str | None = Field(
        default=None,
        description="ID of the user who approved"
    )
    approved_departments: list[str] | None = Field(
        default=None,
        description="List of departments allowed to use this vendor"
    )
    approved_use_cases: list[str] | None = Field(
        default=None,
        description="List of approved use cases"
    )
    prohibited_uses: list[str] | None = Field(
        default=None,
        description="List of prohibited uses"
    )
    data_classification_limit: DataClassification | None = Field(
        default=None,
        description="Maximum data classification allowed"
    )
    conditions: str | None = Field(
        default=None,
        description="Conditions for approval"
    )
    required_settings: dict[str, Any] | None = Field(
        default=None,
        description="Required configuration settings"
    )
    required_training: bool | None = Field(
        default=None,
        description="Whether training is required before use"
    )
    training_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL to training materials"
    )
    review_notes: str | None = Field(
        default=None,
        description="Notes from the review process"
    )
    risk_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Risk score from 0-100"
    )
    max_deployment_count: int | None = Field(
        default=None,
        ge=1,
        description="Maximum number of deployments allowed"
    )


class ApprovedVendorResponse(BaseModel):
    """Schema for approved vendor response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    vendor_id: str
    organization_id: str
    approval_status: ApprovalStatus
    approval_date: datetime | None = None
    expiration_date: datetime | None = None
    approved_by_id: str | None = None
    approved_departments: list[str] | None = None
    approved_use_cases: list[str] | None = None
    prohibited_uses: list[str] | None = None
    data_classification_limit: DataClassification
    conditions: str | None = None
    required_settings: dict[str, Any] | None = None
    required_training: bool
    training_url: str | None = None
    review_notes: str | None = None
    risk_score: int | None = None
    max_deployment_count: int | None = None
    created_at: datetime
    updated_at: datetime


class UseCaseResponse(BaseModel):
    """Schema for use case response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    approved_vendor_id: str
    use_case_name: str
    description: str | None = None
    data_types_allowed: list[str] | None = None
    restrictions: str | None = None
    example_prompts: list[str] | None = None
    prohibited_actions: list[str] | None = None
    created_at: datetime
    updated_at: datetime


class ApprovedVendorDetailResponse(BaseModel):
    """Schema for approved vendor response with use cases."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    vendor_id: str
    organization_id: str
    approval_status: ApprovalStatus
    approval_date: datetime | None = None
    expiration_date: datetime | None = None
    approved_by_id: str | None = None
    approved_departments: list[str] | None = None
    approved_use_cases: list[str] | None = None
    prohibited_uses: list[str] | None = None
    data_classification_limit: DataClassification
    conditions: str | None = None
    required_settings: dict[str, Any] | None = None
    required_training: bool
    training_url: str | None = None
    review_notes: str | None = None
    risk_score: int | None = None
    max_deployment_count: int | None = None
    created_at: datetime
    updated_at: datetime
    use_cases: list[UseCaseResponse] = Field(
        default_factory=list,
        description="List of approved use cases for this vendor"
    )


class ApprovedVendorListResponse(BaseModel):
    """Schema for paginated approved vendor list response."""
    model_config = ConfigDict(from_attributes=True)

    data: list[ApprovedVendorResponse]
    total: int = Field(..., description="Total number of approved vendors")


# -----------------------------------------------------------------------------
# Use Case Schemas
# -----------------------------------------------------------------------------

class UseCaseCreate(BaseModel):
    """Schema for creating an approved use case."""
    model_config = ConfigDict(from_attributes=True)

    approved_vendor_id: str = Field(..., description="ID of the approved vendor")
    use_case_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Name of the use case"
    )
    description: str | None = Field(
        default=None,
        description="Description of the use case"
    )
    data_types_allowed: list[str] | None = Field(
        default=None,
        description="List of allowed data types"
    )
    restrictions: str | None = Field(
        default=None,
        description="Restrictions for this use case"
    )
    example_prompts: list[str] | None = Field(
        default=None,
        description="Example prompts for this use case"
    )
    prohibited_actions: list[str] | None = Field(
        default=None,
        description="Actions that are prohibited"
    )


# -----------------------------------------------------------------------------
# Deployment Schemas
# -----------------------------------------------------------------------------

class DeploymentCreate(BaseModel):
    """Schema for creating a self-service deployment."""
    model_config = ConfigDict(from_attributes=True)

    approved_vendor_id: str = Field(..., description="ID of the approved vendor")
    organization_id: str = Field(..., description="Organization ID")
    deployed_by_id: str = Field(..., description="ID of the user deploying")
    department: str | None = Field(
        default=None,
        max_length=255,
        description="Department using the deployment"
    )
    team: str | None = Field(
        default=None,
        max_length=255,
        description="Team using the deployment"
    )
    use_case: str | None = Field(
        default=None,
        max_length=255,
        description="Use case for this deployment"
    )
    status: DeploymentStatus = Field(
        default=DeploymentStatus.PENDING_APPROVAL,
        description="Deployment status"
    )
    configuration: dict[str, Any] | None = Field(
        default=None,
        description="Deployment configuration"
    )
    data_classification: DataClassification = Field(
        default=DataClassification.INTERNAL,
        description="Data classification for this deployment"
    )
    notes: str | None = Field(
        default=None,
        description="Notes about the deployment"
    )


class DeploymentResponse(BaseModel):
    """Schema for deployment response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    approved_vendor_id: str
    organization_id: str
    deployed_by_id: str
    department: str | None = None
    team: str | None = None
    use_case: str | None = None
    status: DeploymentStatus
    configuration: dict[str, Any] | None = None
    data_classification: DataClassification
    activated_at: datetime | None = None
    deactivated_at: datetime | None = None
    last_used_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class DeploymentListResponse(BaseModel):
    """Schema for paginated deployment list response."""
    model_config = ConfigDict(from_attributes=True)

    data: list[DeploymentResponse]
    total: int = Field(..., description="Total number of deployments")


# -----------------------------------------------------------------------------
# AI Tool Request Schemas
# -----------------------------------------------------------------------------

class ToolRequestCreate(BaseModel):
    """Schema for requesting a new AI tool evaluation."""
    model_config = ConfigDict(from_attributes=True)

    organization_id: str = Field(..., description="Organization ID")
    requested_by_id: str = Field(..., description="ID of the requesting user")
    vendor_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Name of the vendor/tool"
    )
    vendor_website: str | None = Field(
        default=None,
        max_length=500,
        description="Vendor website URL"
    )
    tool_description: str | None = Field(
        default=None,
        description="Description of the tool"
    )
    use_case_description: str | None = Field(
        default=None,
        description="Description of intended use case"
    )
    department: str | None = Field(
        default=None,
        max_length=255,
        description="Department requesting the tool"
    )
    business_justification: str | None = Field(
        default=None,
        description="Business justification for the request"
    )
    expected_data_types: list[str] | None = Field(
        default=None,
        description="Expected data types to be used with the tool"
    )
    urgency: str | None = Field(
        default=None,
        max_length=50,
        description="Urgency level of the request"
    )


class ToolRequestUpdate(BaseModel):
    """Schema for updating a tool request status."""
    model_config = ConfigDict(from_attributes=True)

    status: RequestStatus | None = Field(
        default=None,
        description="Request status"
    )
    assigned_reviewer_id: str | None = Field(
        default=None,
        description="ID of the assigned reviewer"
    )
    review_notes: str | None = Field(
        default=None,
        description="Notes from the review"
    )
    decision_date: datetime | None = Field(
        default=None,
        description="Date of the decision"
    )
    created_vendor_id: str | None = Field(
        default=None,
        description="ID of the vendor created from this request"
    )


class ToolRequestResponse(BaseModel):
    """Schema for tool request response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    requested_by_id: str
    vendor_name: str
    vendor_website: str | None = None
    tool_description: str | None = None
    use_case_description: str | None = None
    department: str | None = None
    business_justification: str | None = None
    expected_data_types: list[str] | None = None
    urgency: str | None = None
    status: RequestStatus
    assigned_reviewer_id: str | None = None
    review_notes: str | None = None
    decision_date: datetime | None = None
    created_vendor_id: str | None = None
    created_at: datetime
    updated_at: datetime


class ToolRequestListResponse(BaseModel):
    """Schema for paginated tool request list response."""
    model_config = ConfigDict(from_attributes=True)

    data: list[ToolRequestResponse]
    total: int = Field(..., description="Total number of requests")


# -----------------------------------------------------------------------------
# Dashboard Statistics
# -----------------------------------------------------------------------------

class ApprovedVendorStats(BaseModel):
    """Schema for approved vendor dashboard statistics."""
    model_config = ConfigDict(from_attributes=True)

    total_approved_vendors: int = Field(
        default=0,
        description="Total number of approved vendors"
    )
    total_pending_approval: int = Field(
        default=0,
        description="Vendors pending approval"
    )
    total_conditional_approval: int = Field(
        default=0,
        description="Vendors with conditional approval"
    )
    total_expired: int = Field(
        default=0,
        description="Vendors with expired approval"
    )
    total_active_deployments: int = Field(
        default=0,
        description="Total active deployments"
    )
    total_pending_requests: int = Field(
        default=0,
        description="Tool requests pending review"
    )
    deployments_by_department: dict[str, int] = Field(
        default_factory=dict,
        description="Deployment counts by department"
    )
    vendors_by_classification: dict[str, int] = Field(
        default_factory=dict,
        description="Vendor counts by data classification"
    )
    expiring_soon: int = Field(
        default=0,
        description="Number of approvals expiring within 30 days"
    )
