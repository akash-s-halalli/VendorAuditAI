"""Pydantic schemas for AI Governance Playbooks."""

import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# Checklist item schema
class ChecklistItem(BaseModel):
    """Individual checklist item within a step."""

    id: str
    text: str
    required: bool = True
    help_text: str | None = None


class Resource(BaseModel):
    """Resource link for a step."""

    title: str
    url: str
    type: str = "link"  # link, document, video, template


# Step schemas
class PlaybookStepBase(BaseModel):
    """Base schema for playbook steps."""

    step_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    instructions: str = Field(..., min_length=1)
    checklist: list[ChecklistItem] | None = None
    required_approvals: list[str] | None = None
    estimated_time_minutes: int | None = Field(default=None, ge=1)
    resources: list[Resource] | None = None
    tips: str | None = None
    warning: str | None = None


class PlaybookStepCreate(PlaybookStepBase):
    """Schema for creating a playbook step."""

    pass


class PlaybookStepUpdate(BaseModel):
    """Schema for updating a playbook step."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    instructions: str | None = None
    checklist: list[ChecklistItem] | None = None
    required_approvals: list[str] | None = None
    estimated_time_minutes: int | None = None
    resources: list[Resource] | None = None
    tips: str | None = None
    warning: str | None = None


class PlaybookStepResponse(PlaybookStepBase):
    """Schema for playbook step response."""

    id: str
    playbook_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("checklist", "required_approvals", "resources", mode="before")
    @classmethod
    def parse_json_fields(cls, v):
        """Parse JSON string to list if needed."""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return None


# Playbook schemas
class PlaybookBase(BaseModel):
    """Base schema for playbooks."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    phase: Literal["tool_selection", "deployment", "regression_protection"] = "tool_selection"
    target_audience: Literal["technical", "non_technical", "all"] = "all"
    department: Literal["marketing", "hr", "finance", "engineering", "operations", "legal", "all"] = "all"
    estimated_duration_minutes: int | None = None
    icon: str | None = None
    color: str | None = None


class PlaybookCreate(PlaybookBase):
    """Schema for creating a playbook."""

    steps: list[PlaybookStepCreate] | None = None
    is_active: bool = True


class PlaybookUpdate(BaseModel):
    """Schema for updating a playbook."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    phase: Literal["tool_selection", "deployment", "regression_protection"] | None = None
    target_audience: Literal["technical", "non_technical", "all"] | None = None
    department: Literal["marketing", "hr", "finance", "engineering", "operations", "legal", "all"] | None = None
    estimated_duration_minutes: int | None = None
    is_active: bool | None = None
    icon: str | None = None
    color: str | None = None


class PlaybookResponse(PlaybookBase):
    """Schema for playbook response."""

    id: str
    organization_id: str
    version: str
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime
    total_steps: int = 0

    model_config = {"from_attributes": True}


class PlaybookDetailResponse(PlaybookResponse):
    """Schema for detailed playbook response with steps."""

    steps: list[PlaybookStepResponse] = []


# Progress schemas
class StepCompletionData(BaseModel):
    """Data for completing a step."""

    checklist_completions: dict[str, bool] = {}  # {checklist_item_id: completed}
    notes: str | None = None
    evidence_urls: list[str] | None = None


class PlaybookProgressCreate(BaseModel):
    """Schema for starting a playbook."""

    playbook_id: str
    vendor_id: str | None = None


class PlaybookProgressResponse(BaseModel):
    """Schema for playbook progress response."""

    id: str
    organization_id: str
    user_id: str
    playbook_id: str
    vendor_id: str | None
    current_step: int
    status: Literal["not_started", "in_progress", "pending_approval", "completed", "abandoned"]
    step_completions: dict | None = None
    started_at: datetime | None
    completed_at: datetime | None
    progress_percentage: float
    created_at: datetime
    updated_at: datetime

    # Related info
    playbook_name: str | None = None
    vendor_name: str | None = None
    total_steps: int = 0

    model_config = {"from_attributes": True}

    @field_validator("step_completions", mode="before")
    @classmethod
    def parse_step_completions(cls, v):
        """Parse JSON string to dict if needed."""
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return None


# Approval schemas
class ApprovalRequestCreate(BaseModel):
    """Schema for requesting approval."""

    step_id: str
    approver_ids: list[str] | None = None  # If None, sends to all with required role
    required_role: str | None = None


class ApprovalResponseData(BaseModel):
    """Schema for responding to an approval request."""

    status: Literal["approved", "rejected"]
    comments: str | None = None


class PlaybookApprovalResponse(BaseModel):
    """Schema for approval response."""

    id: str
    progress_id: str
    step_id: str
    requested_by_id: str
    approver_id: str | None
    status: Literal["pending", "approved", "rejected"]
    comments: str | None
    required_role: str | None
    requested_at: datetime
    responded_at: datetime | None
    created_at: datetime

    # Related info
    step_title: str | None = None
    requested_by_name: str | None = None
    approver_name: str | None = None

    model_config = {"from_attributes": True}


# List response schemas
class PlaybookListResponse(BaseModel):
    """Paginated list of playbooks."""

    data: list[PlaybookResponse]
    total: int
    page: int
    limit: int


class PlaybookProgressListResponse(BaseModel):
    """Paginated list of playbook progress records."""

    data: list[PlaybookProgressResponse]
    total: int
    page: int
    limit: int


class PlaybookApprovalListResponse(BaseModel):
    """Paginated list of approvals."""

    data: list[PlaybookApprovalResponse]
    total: int
    page: int
    limit: int
