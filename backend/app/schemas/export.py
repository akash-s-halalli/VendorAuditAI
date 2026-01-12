"""Pydantic schemas for export functionality."""

from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Supported export formats."""

    CSV = "csv"
    XLSX = "xlsx"


class ExportFilters(BaseModel):
    """Common filters for export operations."""

    # Date range filters
    date_from: date | None = Field(
        default=None, description="Start date for filtering (inclusive)"
    )
    date_to: date | None = Field(
        default=None, description="End date for filtering (inclusive)"
    )

    # Entity filters
    vendor_id: str | None = Field(default=None, description="Filter by specific vendor")
    document_id: str | None = Field(
        default=None, description="Filter by specific document"
    )

    # Status filters
    status: str | None = Field(default=None, description="Filter by status")
    severity: str | None = Field(
        default=None, description="Filter by severity (for findings)"
    )

    # Framework filter
    framework: str | None = Field(
        default=None, description="Filter by compliance framework"
    )


class VendorExportFilters(BaseModel):
    """Filters specific to vendor exports."""

    # Status
    status: Literal["active", "inactive", "onboarding", "offboarding"] | None = Field(
        default=None, description="Filter by vendor status"
    )

    # Tier
    tier: Literal["critical", "high", "medium", "low"] | None = Field(
        default=None, description="Filter by vendor tier"
    )

    # Category
    category: str | None = Field(default=None, description="Filter by vendor category")

    # Date filters
    contract_expiry_before: date | None = Field(
        default=None, description="Vendors with contracts expiring before this date"
    )
    contract_expiry_after: date | None = Field(
        default=None, description="Vendors with contracts expiring after this date"
    )
    assessment_due_before: date | None = Field(
        default=None, description="Vendors with assessments due before this date"
    )


class FindingExportFilters(BaseModel):
    """Filters specific to finding exports."""

    # Status
    status: Literal[
        "open", "acknowledged", "remediated", "accepted", "false_positive"
    ] | None = Field(default=None, description="Filter by finding status")

    # Severity
    severity: Literal["critical", "high", "medium", "low", "info"] | None = Field(
        default=None, description="Filter by finding severity"
    )

    # Entity filters
    vendor_id: str | None = Field(
        default=None, description="Filter by vendor (via documents)"
    )
    document_id: str | None = Field(
        default=None, description="Filter by specific document"
    )

    # Framework
    framework: str | None = Field(
        default=None, description="Filter by compliance framework"
    )

    # Date filters
    created_from: date | None = Field(
        default=None, description="Findings created on or after this date"
    )
    created_to: date | None = Field(
        default=None, description="Findings created on or before this date"
    )


class RemediationExportFilters(BaseModel):
    """Filters specific to remediation task exports."""

    # Status
    status: Literal[
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
    ] | None = Field(default=None, description="Filter by task status")

    # Priority
    priority: Literal["critical", "high", "medium", "low"] | None = Field(
        default=None, description="Filter by task priority"
    )

    # Entity filters
    vendor_id: str | None = Field(default=None, description="Filter by vendor")
    assignee_id: str | None = Field(default=None, description="Filter by assignee")

    # SLA filters
    sla_breached: bool | None = Field(
        default=None, description="Filter by SLA breach status"
    )
    overdue_only: bool = Field(
        default=False, description="Only show tasks past their due date"
    )

    # Date filters
    due_before: date | None = Field(
        default=None, description="Tasks due before this date"
    )
    due_after: date | None = Field(default=None, description="Tasks due after this date")


class ComplianceReportFilters(BaseModel):
    """Filters for compliance report exports."""

    # Frameworks to include
    frameworks: list[str] | None = Field(
        default=None, description="List of frameworks to include (all if not specified)"
    )

    # Include sections
    include_findings: bool = Field(
        default=True, description="Include detailed findings section"
    )
    include_remediation: bool = Field(
        default=True, description="Include remediation tasks section"
    )
    include_summary: bool = Field(
        default=True, description="Include executive summary"
    )


class ExportMetadata(BaseModel):
    """Metadata about an export operation."""

    format: ExportFormat
    filename: str
    record_count: int
    generated_at: datetime
    filters_applied: dict | None = None


class ExportResponse(BaseModel):
    """Response model for export operations (when returning metadata only)."""

    success: bool = True
    metadata: ExportMetadata
    message: str | None = None
