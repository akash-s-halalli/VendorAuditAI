"""Pydantic schemas for audit logging."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# Action type literals matching the model enum
AuditActionType = Literal[
    "CREATE",
    "READ",
    "UPDATE",
    "DELETE",
    "LOGIN",
    "LOGOUT",
    "LOGIN_FAILED",
    "EXPORT",
    "BULK_OPERATION",
    "STATUS_CHANGE",
    "PERMISSION_CHANGE",
]


class AuditLogResponse(BaseModel):
    """Response schema for an audit log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    user_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    ip_address: str | None
    user_agent: str | None
    details: str | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Paginated list of audit logs."""

    data: list[AuditLogResponse]
    total: int
    page: int
    limit: int


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""

    action: AuditActionType | None = Field(None, description="Filter by action type")
    resource_type: str | None = Field(None, description="Filter by resource type")
    resource_id: str | None = Field(None, description="Filter by resource ID")
    user_id: str | None = Field(None, description="Filter by user ID")
    start_date: datetime | None = Field(None, description="Filter logs after this date")
    end_date: datetime | None = Field(None, description="Filter logs before this date")


class AuditLogExportRequest(BaseModel):
    """Schema for audit log export request."""

    action: AuditActionType | None = Field(None, description="Filter by action type")
    resource_type: str | None = Field(None, description="Filter by resource type")
    user_id: str | None = Field(None, description="Filter by user ID")
    start_date: datetime | None = Field(None, description="Filter logs after this date")
    end_date: datetime | None = Field(None, description="Filter logs before this date")
    max_records: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Maximum number of records to export",
    )


class AuditLogSummary(BaseModel):
    """Summary statistics for audit logs."""

    total_logs: int
    logs_by_action: dict[str, int]
    logs_by_resource_type: dict[str, int]
    logs_by_user: dict[str, int]
    recent_activity_count: int
