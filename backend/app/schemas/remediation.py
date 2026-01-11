"""Pydantic schemas for remediation workflow."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Status and priority literals matching the model enums
RemediationStatusType = Literal[
    "draft",
    "pending_assignment",
    "assigned",
    "in_progress",
    "pending_review",
    "pending_verification",
    "verified",
    "closed",
    "exception_requested",
    "exception_approved",
    "exception_denied",
    "reopened",
]

RemediationPriorityType = Literal["critical", "high", "medium", "low"]


class RemediationTaskCreate(BaseModel):
    """Schema for creating a remediation task."""

    finding_id: str = Field(..., description="ID of the finding to remediate")
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    priority: RemediationPriorityType = Field(
        default="medium", description="Task priority"
    )
    assignee_id: str | None = Field(None, description="User ID to assign the task to")
    vendor_id: str | None = Field(None, description="Vendor ID if applicable")
    due_date: datetime | None = Field(None, description="Due date for completion")
    sla_days: int | None = Field(
        None, ge=1, le=365, description="Custom SLA days override"
    )


class RemediationTaskUpdate(BaseModel):
    """Schema for updating a remediation task."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    priority: RemediationPriorityType | None = None
    assignee_id: str | None = None
    due_date: datetime | None = None
    resolution_notes: str | None = Field(None, max_length=5000)


class RemediationTransition(BaseModel):
    """Schema for transitioning task status."""

    new_status: RemediationStatusType = Field(..., description="New status to transition to")
    notes: str | None = Field(None, max_length=2000, description="Notes about the transition")
    exception_reason: str | None = Field(
        None, max_length=2000, description="Reason if requesting exception"
    )


class RemediationCommentCreate(BaseModel):
    """Schema for creating a comment."""

    content: str = Field(..., min_length=1, max_length=5000)
    is_internal: bool = Field(default=True, description="Whether comment is internal-only")


class RemediationCommentResponse(BaseModel):
    """Response schema for a comment."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    user_id: str
    content: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime


class RemediationAuditLogResponse(BaseModel):
    """Response schema for an audit log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    user_id: str | None
    action: str
    field_changed: str | None
    old_value: str | None
    new_value: str | None
    notes: str | None
    created_at: datetime


class RemediationTaskResponse(BaseModel):
    """Response schema for a remediation task."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    finding_id: str
    vendor_id: str | None
    assignee_id: str | None
    created_by_id: str
    title: str
    description: str | None
    status: str
    priority: str
    due_date: datetime | None
    sla_days: int | None
    sla_breached: bool
    sla_breached_at: datetime | None
    resolution_notes: str | None
    resolved_at: datetime | None
    verified_at: datetime | None
    verified_by_id: str | None
    exception_reason: str | None
    exception_approved_by_id: str | None
    exception_approved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RemediationTaskDetail(RemediationTaskResponse):
    """Detailed response including audit trail and comments."""

    audit_logs: list[RemediationAuditLogResponse] = []
    comments: list[RemediationCommentResponse] = []


class RemediationTaskListResponse(BaseModel):
    """Paginated list of remediation tasks."""

    data: list[RemediationTaskResponse]
    total: int
    page: int
    limit: int


class RemediationDashboardStats(BaseModel):
    """Statistics for remediation dashboard."""

    total_tasks: int = 0
    open_tasks: int = 0
    overdue_tasks: int = 0
    sla_breached: int = 0
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    avg_resolution_days: float | None = None


class SLAPolicyCreate(BaseModel):
    """Schema for creating an SLA policy."""

    name: str = Field(..., min_length=1, max_length=200)
    is_default: bool = False
    critical_sla_days: int = Field(default=3, ge=1, le=365)
    high_sla_days: int = Field(default=7, ge=1, le=365)
    medium_sla_days: int = Field(default=30, ge=1, le=365)
    low_sla_days: int = Field(default=90, ge=1, le=365)


class SLAPolicyResponse(BaseModel):
    """Response schema for an SLA policy."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    name: str
    is_default: bool
    critical_sla_days: int
    high_sla_days: int
    medium_sla_days: int
    low_sla_days: int
    created_at: datetime
    updated_at: datetime
