"""Pydantic schemas for analytics dashboard."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# Dashboard Stats Schemas
class DashboardStats(BaseModel):
    """Overall dashboard statistics."""

    # Core counts
    total_vendors: int = Field(description="Total number of vendors")
    total_documents: int = Field(description="Total number of documents")
    total_findings: int = Field(description="Total number of findings")
    total_remediation_tasks: int = Field(description="Total remediation tasks")

    # Status breakdowns
    active_vendors: int = Field(description="Number of active vendors")
    pending_documents: int = Field(description="Documents pending processing")
    open_findings: int = Field(description="Open findings count")
    overdue_tasks: int = Field(description="Overdue remediation tasks")

    # Risk metrics
    critical_findings: int = Field(description="Critical severity findings")
    high_risk_vendors: int = Field(description="High/critical tier vendors")

    # Compliance metrics
    avg_compliance_score: float | None = Field(
        default=None, description="Average compliance score across vendors"
    )

    # Time-based metrics
    findings_this_month: int = Field(description="New findings this month")
    documents_this_month: int = Field(description="Documents uploaded this month")


class DashboardStatsResponse(BaseModel):
    """Response wrapper for dashboard stats."""

    data: DashboardStats
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Vendor Distribution Schemas
class CategoryDistribution(BaseModel):
    """Distribution item for a category."""

    name: str = Field(description="Category name")
    count: int = Field(description="Number of vendors in this category")
    percentage: float = Field(description="Percentage of total")


class TierDistribution(BaseModel):
    """Distribution of vendors by tier."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class StatusDistribution(BaseModel):
    """Distribution of vendors by status."""

    active: int = 0
    inactive: int = 0
    onboarding: int = 0
    offboarding: int = 0


class VendorDistribution(BaseModel):
    """Complete vendor distribution analytics."""

    by_category: list[CategoryDistribution] = Field(
        default_factory=list, description="Vendors grouped by category"
    )
    by_tier: TierDistribution = Field(
        default_factory=TierDistribution, description="Vendors grouped by tier"
    )
    by_status: StatusDistribution = Field(
        default_factory=StatusDistribution, description="Vendors grouped by status"
    )
    total_vendors: int = Field(description="Total vendor count")


class VendorDistributionResponse(BaseModel):
    """Response wrapper for vendor distribution."""

    data: VendorDistribution
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Findings Analytics Schemas
class SeverityBreakdown(BaseModel):
    """Findings breakdown by severity."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class FindingStatusBreakdown(BaseModel):
    """Findings breakdown by status."""

    open: int = 0
    acknowledged: int = 0
    remediated: int = 0
    accepted: int = 0
    false_positive: int = 0


class FrameworkBreakdown(BaseModel):
    """Finding count for a framework."""

    framework: str = Field(description="Framework name")
    count: int = Field(description="Number of findings")
    critical: int = Field(default=0, description="Critical findings for this framework")
    high: int = Field(default=0, description="High findings for this framework")


class TimeSeriesDataPoint(BaseModel):
    """Single data point in a time series."""

    date: str = Field(description="Date in YYYY-MM-DD format")
    count: int = Field(description="Count for this date")


class FindingsSummary(BaseModel):
    """Complete findings analytics summary."""

    total_findings: int = Field(description="Total findings count")
    by_severity: SeverityBreakdown = Field(
        default_factory=SeverityBreakdown, description="Findings by severity"
    )
    by_status: FindingStatusBreakdown = Field(
        default_factory=FindingStatusBreakdown, description="Findings by status"
    )
    by_framework: list[FrameworkBreakdown] = Field(
        default_factory=list, description="Findings by compliance framework"
    )
    trend_last_30_days: list[TimeSeriesDataPoint] = Field(
        default_factory=list, description="Daily finding counts for last 30 days"
    )
    avg_resolution_time_days: float | None = Field(
        default=None, description="Average days to resolve a finding"
    )


class FindingsSummaryResponse(BaseModel):
    """Response wrapper for findings summary."""

    data: FindingsSummary
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Compliance Metrics Schemas
class FrameworkCoverage(BaseModel):
    """Coverage metrics for a single framework."""

    framework: str = Field(description="Framework name (e.g., SOC2, ISO27001)")
    vendors_assessed: int = Field(description="Vendors assessed against this framework")
    total_controls: int = Field(default=0, description="Total controls in framework")
    controls_covered: int = Field(default=0, description="Controls with coverage")
    coverage_percentage: float = Field(
        default=0.0, description="Percentage of controls covered"
    )
    findings_count: int = Field(default=0, description="Total findings for this framework")
    critical_gaps: int = Field(default=0, description="Critical gaps identified")


class ComplianceMetrics(BaseModel):
    """Overall compliance metrics across the organization."""

    overall_coverage: float = Field(
        default=0.0, description="Overall compliance coverage percentage"
    )
    frameworks: list[FrameworkCoverage] = Field(
        default_factory=list, description="Coverage by framework"
    )
    vendors_with_findings: int = Field(
        description="Vendors that have at least one finding"
    )
    vendors_fully_compliant: int = Field(
        description="Vendors with no open findings"
    )
    avg_findings_per_vendor: float = Field(
        default=0.0, description="Average findings per vendor"
    )


class ComplianceMetricsResponse(BaseModel):
    """Response wrapper for compliance metrics."""

    data: ComplianceMetrics
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Activity Timeline Schemas
class ActivityItem(BaseModel):
    """Single activity item in the timeline."""

    id: str = Field(description="Activity ID")
    timestamp: datetime = Field(description="When the activity occurred")
    action: str = Field(description="Action type (CREATE, UPDATE, DELETE, etc.)")
    resource_type: str = Field(description="Type of resource affected")
    resource_id: str | None = Field(default=None, description="ID of affected resource")
    resource_name: str | None = Field(
        default=None, description="Human-readable resource name"
    )
    user_id: str | None = Field(default=None, description="User who performed action")
    user_email: str | None = Field(default=None, description="Email of user")
    details: str | None = Field(default=None, description="Additional details")


class ActivityTimeline(BaseModel):
    """Activity timeline with recent actions."""

    activities: list[ActivityItem] = Field(
        default_factory=list, description="List of recent activities"
    )
    total_count: int = Field(description="Total activities in time range")
    has_more: bool = Field(default=False, description="Whether more activities exist")


class ActivityTimelineResponse(BaseModel):
    """Response wrapper for activity timeline."""

    data: ActivityTimeline
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Filter Schemas for API endpoints
class FindingsFilterParams(BaseModel):
    """Filter parameters for findings analytics."""

    severity: Literal["critical", "high", "medium", "low", "info"] | None = None
    status: Literal[
        "open", "acknowledged", "remediated", "accepted", "false_positive"
    ] | None = None
    framework: str | None = None
    vendor_id: str | None = None
    days: int = Field(default=30, ge=1, le=365, description="Days to look back")


class ActivityFilterParams(BaseModel):
    """Filter parameters for activity timeline."""

    action: str | None = Field(default=None, description="Filter by action type")
    resource_type: str | None = Field(default=None, description="Filter by resource")
    user_id: str | None = Field(default=None, description="Filter by user")
    limit: int = Field(default=50, ge=1, le=200, description="Number of items")
    offset: int = Field(default=0, ge=0, description="Pagination offset")
