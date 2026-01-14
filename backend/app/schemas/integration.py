"""Pydantic schemas for Integration Hub."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Enums
class IntegrationType(str, Enum):
    """Types of integrations supported."""

    JIRA = "jira"
    SERVICENOW = "servicenow"
    SLACK = "slack"
    WEBHOOK = "webhook"
    EMAIL = "email"
    TEAMS = "teams"


class IntegrationStatus(str, Enum):
    """Integration connection status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING_SETUP = "pending_setup"


class SyncAction(str, Enum):
    """Actions performed during sync operations."""

    SYNC = "sync"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    TEST = "test"
    WEBHOOK_RECEIVED = "webhook_received"


class SyncStatus(str, Enum):
    """Status of sync operations."""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class EntityType(str, Enum):
    """Entity types that can be synced."""

    VENDOR = "vendor"
    FINDING = "finding"
    REMEDIATION_TASK = "remediation_task"
    DOCUMENT = "document"


# Integration Schemas
class IntegrationBase(BaseModel):
    """Base schema for integrations."""

    name: str = Field(..., min_length=1, max_length=255, description="Integration name")
    integration_type: IntegrationType = Field(..., description="Type of integration")
    description: str | None = Field(None, max_length=1000, description="Integration description")
    is_enabled: bool = Field(default=True, description="Whether integration is enabled")


class IntegrationCreate(IntegrationBase):
    """Schema for creating an integration."""

    config: dict[str, Any] = Field(
        default_factory=dict, description="Integration-specific configuration"
    )
    credentials: dict[str, Any] = Field(
        default_factory=dict, description="Integration credentials (encrypted at rest)"
    )
    sync_settings: dict[str, Any] = Field(
        default_factory=dict,
        description="Sync configuration including frequency and entity mappings",
    )


class IntegrationUpdate(BaseModel):
    """Schema for updating an integration."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    is_enabled: bool | None = None
    config: dict[str, Any] | None = None
    credentials: dict[str, Any] | None = None
    sync_settings: dict[str, Any] | None = None


class IntegrationResponse(BaseModel):
    """Schema for integration response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    name: str
    integration_type: str
    description: str | None
    status: str
    is_enabled: bool
    last_sync_at: datetime | None
    last_sync_status: str | None
    last_error: str | None
    sync_count: int
    error_count: int
    created_at: datetime
    updated_at: datetime


class IntegrationDetailResponse(IntegrationResponse):
    """Detailed integration response including config."""

    config: dict[str, Any] = Field(default_factory=dict)
    sync_settings: dict[str, Any] = Field(default_factory=dict)
    # Note: credentials are never returned in responses


class IntegrationListResponse(BaseModel):
    """Paginated list of integrations."""

    data: list[IntegrationResponse]
    total: int
    page: int
    limit: int


# Integration Mapping Schemas
class IntegrationMappingCreate(BaseModel):
    """Schema for creating a field mapping."""

    source_entity: EntityType = Field(..., description="Source entity type")
    source_field: str = Field(..., min_length=1, max_length=255, description="Source field name")
    target_entity: str = Field(..., min_length=1, max_length=255, description="Target entity in external system")
    target_field: str = Field(..., min_length=1, max_length=255, description="Target field name")
    transform: str | None = Field(
        None, max_length=500, description="Optional transformation expression"
    )
    is_bidirectional: bool = Field(
        default=False, description="Whether mapping syncs both directions"
    )


class IntegrationMappingResponse(BaseModel):
    """Schema for field mapping response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    integration_id: str
    source_entity: str
    source_field: str
    target_entity: str
    target_field: str
    transform: str | None
    is_bidirectional: bool
    created_at: datetime
    updated_at: datetime


# Integration Log Schemas
class IntegrationLogResponse(BaseModel):
    """Schema for integration log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    integration_id: str
    action: str
    status: str
    entity_type: str | None
    entity_id: str | None
    external_id: str | None
    request_payload: dict[str, Any] | None
    response_payload: dict[str, Any] | None
    error_message: str | None
    duration_ms: int | None
    created_at: datetime


class IntegrationLogListResponse(BaseModel):
    """Paginated list of integration logs."""

    data: list[IntegrationLogResponse]
    total: int
    page: int
    limit: int


# Webhook Endpoint Schemas
class WebhookEndpointCreate(BaseModel):
    """Schema for creating a webhook endpoint."""

    name: str = Field(..., min_length=1, max_length=255, description="Webhook endpoint name")
    description: str | None = Field(None, max_length=1000)
    events: list[str] = Field(
        default_factory=list, description="List of events to listen for"
    )
    target_entity: EntityType | None = Field(
        None, description="Entity type this webhook creates/updates"
    )
    payload_mapping: dict[str, str] = Field(
        default_factory=dict, description="Mapping from webhook payload to entity fields"
    )
    headers_required: list[str] = Field(
        default_factory=list, description="Required headers for validation"
    )
    secret: str | None = Field(
        None, max_length=255, description="Webhook secret for signature validation"
    )


class WebhookEndpointResponse(BaseModel):
    """Schema for webhook endpoint response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    name: str
    description: str | None
    endpoint_key: str  # Unique key used in URL
    endpoint_url: str  # Full URL to receive webhooks
    events: list[str]
    target_entity: str | None
    payload_mapping: dict[str, str]
    is_active: bool
    last_received_at: datetime | None
    receive_count: int
    created_at: datetime
    updated_at: datetime


# Test Result Schema
class IntegrationTestResult(BaseModel):
    """Result of testing an integration connection."""

    success: bool = Field(..., description="Whether the test was successful")
    message: str = Field(..., description="Test result message")
    response_time_ms: int | None = Field(None, description="Response time in milliseconds")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Additional test details"
    )
    tested_at: datetime = Field(
        default_factory=lambda: datetime.now(), description="When the test was performed"
    )
    errors: list[str] = Field(
        default_factory=list, description="List of errors if test failed"
    )


# Stats Schema
class IntegrationStats(BaseModel):
    """Dashboard statistics for integrations."""

    total_integrations: int = Field(default=0, description="Total number of integrations")
    active_integrations: int = Field(default=0, description="Number of active integrations")
    error_integrations: int = Field(default=0, description="Integrations in error state")
    pending_setup: int = Field(default=0, description="Integrations pending setup")

    by_type: dict[str, int] = Field(
        default_factory=dict, description="Count by integration type"
    )
    by_status: dict[str, int] = Field(
        default_factory=dict, description="Count by status"
    )

    total_syncs_today: int = Field(default=0, description="Total syncs performed today")
    successful_syncs_today: int = Field(default=0, description="Successful syncs today")
    failed_syncs_today: int = Field(default=0, description="Failed syncs today")

    total_webhooks_today: int = Field(default=0, description="Webhooks received today")
    active_webhook_endpoints: int = Field(default=0, description="Active webhook endpoints")

    last_sync_at: datetime | None = Field(None, description="Last sync across all integrations")
    last_webhook_at: datetime | None = Field(None, description="Last webhook received")


# Sync Result Schema
class SyncResult(BaseModel):
    """Result of a sync operation."""

    success: bool = Field(..., description="Whether sync was successful")
    status: SyncStatus = Field(..., description="Sync status")
    message: str = Field(..., description="Result message")
    records_synced: int = Field(default=0, description="Number of records synced")
    records_created: int = Field(default=0, description="Number of records created")
    records_updated: int = Field(default=0, description="Number of records updated")
    records_failed: int = Field(default=0, description="Number of records that failed")
    duration_ms: int | None = Field(None, description="Sync duration in milliseconds")
    errors: list[str] = Field(
        default_factory=list, description="List of errors if any"
    )
    synced_at: datetime = Field(
        default_factory=lambda: datetime.now(), description="When sync was performed"
    )


# Webhook Processing Result
class WebhookProcessResult(BaseModel):
    """Result of processing a webhook."""

    success: bool = Field(..., description="Whether processing was successful")
    message: str = Field(..., description="Result message")
    entity_type: str | None = Field(None, description="Entity type created/updated")
    entity_id: str | None = Field(None, description="ID of created/updated entity")
    action_taken: str | None = Field(None, description="Action taken (create/update/ignore)")
    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(), description="When webhook was processed"
    )
