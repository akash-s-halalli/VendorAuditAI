"""Pydantic schemas for AI Tool Classification."""

import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# Enums as Literal types for Pydantic
AIStackTypeEnum = Literal[
    "foundation_model",
    "genai_application",
    "inference_optimization",
    "fine_tuning_platform",
    "autonomous_agent",
    "horizontal_layer",
    "embedding_service",
    "mlops_platform",
    "not_ai_tool",
]

AutonomyLevelEnum = Literal["none", "low", "medium", "high", "critical"]
BlastRadiusEnum = Literal["minimal", "limited", "significant", "severe", "catastrophic"]
ClassificationMethodEnum = Literal["manual", "ai_assisted", "auto_detected"]
RiskLevelEnum = Literal["low", "medium", "high", "critical"]


class AIToolCapabilityBase(BaseModel):
    """Base schema for AI tool capability."""

    capability_category: str = Field(..., min_length=1, max_length=100)
    capability_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    risk_level: RiskLevelEnum = "medium"
    is_enabled: bool = True
    evidence: str | None = None
    documentation_url: str | None = None


class AIToolCapabilityCreate(AIToolCapabilityBase):
    """Schema for creating a capability."""

    pass


class AIToolCapabilityResponse(AIToolCapabilityBase):
    """Schema for capability response."""

    id: str
    classification_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIClassificationBase(BaseModel):
    """Base schema for AI classification."""

    stack_type: AIStackTypeEnum = "not_ai_tool"

    # Capability Flags
    has_credential_access: bool = False
    has_autonomous_actions: bool = False
    has_data_training: bool = False
    has_external_integrations: bool = False
    has_code_execution: bool = False

    # Credential Details
    credential_types: list[str] | None = None
    credential_scope: list[str] | None = None

    # Autonomous Action Details
    action_types: list[str] | None = None
    requires_human_approval: bool = True

    # Data Handling
    data_access_types: list[str] | None = None
    data_retention_policy: str | None = None
    trains_on_customer_data: bool = False
    data_sharing_third_parties: bool = False

    # Risk Assessment
    autonomy_level: AutonomyLevelEnum = "none"
    blast_radius: BlastRadiusEnum = "minimal"

    # Notes
    notes: str | None = None


class AIClassificationCreate(AIClassificationBase):
    """Schema for creating a classification."""

    vendor_id: str = Field(..., description="ID of the vendor to classify")
    capabilities: list[AIToolCapabilityCreate] | None = None


class AIClassificationUpdate(BaseModel):
    """Schema for updating a classification."""

    stack_type: AIStackTypeEnum | None = None
    has_credential_access: bool | None = None
    has_autonomous_actions: bool | None = None
    has_data_training: bool | None = None
    has_external_integrations: bool | None = None
    has_code_execution: bool | None = None
    credential_types: list[str] | None = None
    credential_scope: list[str] | None = None
    action_types: list[str] | None = None
    requires_human_approval: bool | None = None
    data_access_types: list[str] | None = None
    data_retention_policy: str | None = None
    trains_on_customer_data: bool | None = None
    data_sharing_third_parties: bool | None = None
    autonomy_level: AutonomyLevelEnum | None = None
    blast_radius: BlastRadiusEnum | None = None
    notes: str | None = None


class AIClassificationResponse(AIClassificationBase):
    """Schema for classification response."""

    id: str
    vendor_id: str
    organization_id: str
    ai_risk_score: int | None = None
    classification_method: ClassificationMethodEnum = "manual"
    classification_confidence: float | None = None
    classified_by_id: str | None = None
    classified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    capabilities: list[AIToolCapabilityResponse] = []

    model_config = {"from_attributes": True}

    @field_validator(
        "credential_types",
        "credential_scope",
        "action_types",
        "data_access_types",
        mode="before",
    )
    @classmethod
    def parse_json_list(cls, v):
        """Parse JSON string to list if needed."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v


class AIClassificationDetailResponse(AIClassificationResponse):
    """Detailed classification response with vendor info."""

    vendor_name: str | None = None
    vendor_category: str | None = None


class AIClassificationListResponse(BaseModel):
    """Response for listing classifications."""

    data: list[AIClassificationDetailResponse]
    total: int


# Stack Type Definitions for the frontend
class StackTypeDefinition(BaseModel):
    """Definition of an AI stack type."""

    id: str
    name: str
    description: str
    examples: list[str]
    typical_risks: list[str]
    base_risk_score: int
    typical_credential_access: bool
    typical_autonomous_actions: bool


class StackTypeListResponse(BaseModel):
    """Response for listing stack types."""

    stack_types: list[StackTypeDefinition]


# Risk Matrix View
class RiskMatrixEntry(BaseModel):
    """Entry in the risk matrix."""

    vendor_id: str
    vendor_name: str
    stack_type: AIStackTypeEnum
    autonomy_level: AutonomyLevelEnum
    blast_radius: BlastRadiusEnum
    ai_risk_score: int | None
    has_credential_access: bool
    has_autonomous_actions: bool


class RiskMatrixResponse(BaseModel):
    """Response for risk matrix view."""

    entries: list[RiskMatrixEntry]
    total: int
    summary: dict[str, int]  # Count by stack type


# AI-Assisted Classification Request
class ClassifyVendorRequest(BaseModel):
    """Request for AI-assisted classification."""

    vendor_id: str
    vendor_description: str | None = None
    additional_context: str | None = None
