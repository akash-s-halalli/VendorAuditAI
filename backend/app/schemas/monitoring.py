"""Pydantic schemas for monitoring and alerting."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Literal types matching model enums
ScheduleFrequencyType = Literal["daily", "weekly", "biweekly", "monthly", "quarterly"]
ScheduleStatusType = Literal["active", "paused", "disabled"]
AlertSeverityType = Literal["critical", "high", "medium", "low", "info"]
AlertStatusType = Literal["new", "acknowledged", "in_progress", "resolved", "dismissed"]
NotificationChannelTypeType = Literal["email", "slack", "webhook", "teams"]


class MonitoringScheduleCreate(BaseModel):
    """Schema for creating a monitoring schedule."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    frequency: ScheduleFrequencyType = "monthly"
    vendor_id: str | None = Field(None, description="Specific vendor to monitor")
    framework: str | None = Field(None, description="Framework to assess against")
    include_all_vendors: bool = Field(default=False)
    notify_on_completion: bool = Field(default=True)
    notify_on_findings: bool = Field(default=True)


class MonitoringScheduleUpdate(BaseModel):
    """Schema for updating a monitoring schedule."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    frequency: ScheduleFrequencyType | None = None
    status: ScheduleStatusType | None = None
    notify_on_completion: bool | None = None
    notify_on_findings: bool | None = None


class MonitoringScheduleResponse(BaseModel):
    """Response schema for a monitoring schedule."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    vendor_id: str | None
    name: str
    description: str | None
    frequency: str
    status: str
    framework: str | None
    include_all_vendors: bool
    next_run_at: datetime | None
    last_run_at: datetime | None
    notify_on_completion: bool
    notify_on_findings: bool
    created_at: datetime
    updated_at: datetime


class ScheduledRunResponse(BaseModel):
    """Response schema for a scheduled run."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    schedule_id: str
    organization_id: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    vendors_assessed: int
    documents_analyzed: int
    findings_generated: int
    error_message: str | None
    created_at: datetime


class AlertRuleCreate(BaseModel):
    """Schema for creating an alert rule."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    trigger_type: str = Field(..., description="Type of trigger (e.g., 'critical_finding', 'sla_breach')")
    trigger_conditions: str | None = Field(None, description="JSON string of conditions")
    severity: AlertSeverityType = "medium"


class AlertRuleResponse(BaseModel):
    """Response schema for an alert rule."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    name: str
    description: str | None
    is_active: bool
    trigger_type: str
    trigger_conditions: str | None
    severity: str
    created_at: datetime
    updated_at: datetime


class AlertResponse(BaseModel):
    """Response schema for an alert."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    rule_id: str | None
    vendor_id: str | None
    title: str
    description: str | None
    severity: str
    status: str
    source_type: str | None
    source_id: str | None
    acknowledged_at: datetime | None
    acknowledged_by_id: str | None
    resolved_at: datetime | None
    resolved_by_id: str | None
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime


class AlertAcknowledge(BaseModel):
    """Schema for acknowledging an alert."""

    notes: str | None = Field(None, max_length=2000)


class AlertResolve(BaseModel):
    """Schema for resolving an alert."""

    resolution_notes: str = Field(..., min_length=1, max_length=2000)


class AlertListResponse(BaseModel):
    """Paginated list of alerts."""

    data: list[AlertResponse]
    total: int
    page: int
    limit: int


class NotificationChannelCreate(BaseModel):
    """Schema for creating a notification channel."""

    name: str = Field(..., min_length=1, max_length=200)
    channel_type: NotificationChannelTypeType = "email"
    config: str | None = Field(None, description="JSON configuration for the channel")


class NotificationChannelResponse(BaseModel):
    """Response schema for a notification channel."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    name: str
    channel_type: str
    is_active: bool
    last_used_at: datetime | None
    failure_count: int
    created_at: datetime
    updated_at: datetime


class NotificationChannelTest(BaseModel):
    """Schema for testing a notification channel."""

    message: str = Field(default="Test notification from VendorAuditAI")


class MonitoringDashboardStats(BaseModel):
    """Statistics for monitoring dashboard."""

    active_schedules: int = 0
    total_alerts: int = 0
    open_alerts: int = 0
    critical_alerts: int = 0
    recent_runs: int = 0
    alerts_by_severity: dict[str, int] = {}
    alerts_by_status: dict[str, int] = {}
