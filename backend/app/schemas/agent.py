"""Pydantic schemas for AI agents."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# Agent schemas
class AgentBase(BaseModel):
    """Base agent schema with common fields."""

    name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., min_length=2, max_length=100)
    description: str | None = None


class AgentCreate(AgentBase):
    """Schema for creating a new agent (admin only)."""

    agent_type: Literal[
        "threat_detection",
        "risk_assessment",
        "vulnerability_scanner",
        "compliance_verification",
    ]
    configuration: dict = Field(default_factory=dict)


class AgentUpdate(BaseModel):
    """Schema for updating an agent."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    status: Literal["active", "idle", "disabled"] | None = None
    configuration: dict | None = None


class AgentResponse(AgentBase):
    """Schema for agent response."""

    id: str
    agent_type: str
    status: str
    uptime_percentage: float
    last_run_at: datetime | None = None
    error_message: str | None = None
    configuration: dict
    organization_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentListResponse(BaseModel):
    """Schema for paginated agent list response."""

    data: list[AgentResponse]
    total: int


# Task schemas
class TaskCreate(BaseModel):
    """Schema for creating a new agent task."""

    task_type: Literal["scan", "analyze", "report", "monitor", "audit"]
    input_data: dict = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: str
    agent_id: str
    task_type: str
    status: str
    input_data: dict
    output_data: dict | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    items_processed: int | None = None
    findings_count: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""

    data: list[TaskResponse]
    total: int


# Log schemas
class LogResponse(BaseModel):
    """Schema for log entry response."""

    id: str
    agent_id: str
    task_id: str | None = None
    level: str
    message: str
    details: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LogListResponse(BaseModel):
    """Schema for paginated log list response."""

    data: list[LogResponse]
    total: int


# Configuration update schemas
class AgentConfigUpdate(BaseModel):
    """Schema for updating agent configuration."""

    scan_frequency: str | None = Field(
        default=None,
        pattern=r"^(hourly|daily|weekly|monthly)$",
        description="How often the agent runs automatic scans",
    )
    alert_threshold: int | None = Field(
        default=None, ge=1, le=10, description="Minimum severity level for alerts"
    )
    enabled_checks: list[str] | None = Field(
        default=None, description="List of enabled security checks"
    )
    notification_enabled: bool | None = Field(
        default=None, description="Whether to send notifications"
    )


# Agent stats for dashboard
class AgentStats(BaseModel):
    """Schema for agent statistics."""

    total_agents: int
    active_agents: int
    processing_agents: int
    error_agents: int
    total_tasks_today: int
    completed_tasks_today: int
    total_findings_today: int
