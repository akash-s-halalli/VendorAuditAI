"""Analytics dashboard API endpoints."""

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.schemas.analytics import (
    ActivityTimelineResponse,
    ComplianceMetricsResponse,
    DashboardStatsResponse,
    FindingsSummaryResponse,
    VendorDistributionResponse,
)
from app.services.analytics import (
    get_activity_timeline,
    get_compliance_metrics,
    get_dashboard_stats,
    get_findings_analytics,
    get_vendor_distribution,
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_analytics_dashboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DashboardStatsResponse:
    """
    Get main dashboard statistics.

    Returns aggregated counts and metrics including:
    - Total vendors, documents, findings, and remediation tasks
    - Active vendors and pending documents
    - Open and critical findings
    - Overdue remediation tasks
    - Month-over-month metrics

    Requires authentication. Data is scoped to the user's organization.
    """
    stats = await get_dashboard_stats(db, current_user.organization_id)
    return DashboardStatsResponse(
        data=stats,
        generated_at=datetime.utcnow(),
    )


@router.get("/vendors/distribution", response_model=VendorDistributionResponse)
async def get_vendor_distribution_analytics(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VendorDistributionResponse:
    """
    Get vendor distribution analytics.

    Returns vendor counts grouped by:
    - Category (with percentages)
    - Tier (critical, high, medium, low)
    - Status (active, inactive, onboarding, offboarding)

    Useful for visualizing vendor portfolio composition.
    Requires authentication. Data is scoped to the user's organization.
    """
    distribution = await get_vendor_distribution(db, current_user.organization_id)
    return VendorDistributionResponse(
        data=distribution,
        generated_at=datetime.utcnow(),
    )


@router.get("/findings/summary", response_model=FindingsSummaryResponse)
async def get_findings_summary(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    severity: Annotated[
        Literal["critical", "high", "medium", "low", "info"] | None,
        Query(description="Filter by severity level"),
    ] = None,
    status: Annotated[
        Literal["open", "acknowledged", "remediated", "accepted", "false_positive"]
        | None,
        Query(description="Filter by finding status"),
    ] = None,
    framework: Annotated[
        str | None,
        Query(description="Filter by compliance framework (e.g., SOC2, ISO27001)"),
    ] = None,
    vendor_id: Annotated[
        str | None,
        Query(description="Filter by vendor ID"),
    ] = None,
    days: Annotated[
        int,
        Query(ge=1, le=365, description="Number of days to look back for trends"),
    ] = 30,
) -> FindingsSummaryResponse:
    """
    Get findings analytics summary with optional filters.

    Returns:
    - Total findings count
    - Breakdown by severity (critical, high, medium, low, info)
    - Breakdown by status (open, acknowledged, remediated, etc.)
    - Breakdown by compliance framework
    - Daily trend for the specified time period
    - Average resolution time

    Filters:
    - severity: Filter findings by severity level
    - status: Filter findings by current status
    - framework: Filter by compliance framework
    - vendor_id: Filter by specific vendor
    - days: Number of days for trend data (default: 30)

    Requires authentication. Data is scoped to the user's organization.
    """
    summary = await get_findings_analytics(
        db=db,
        organization_id=current_user.organization_id,
        severity=severity,
        status=status,
        framework=framework,
        vendor_id=vendor_id,
        days=days,
    )
    return FindingsSummaryResponse(
        data=summary,
        generated_at=datetime.utcnow(),
    )


@router.get("/compliance/overview", response_model=ComplianceMetricsResponse)
async def get_compliance_overview(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ComplianceMetricsResponse:
    """
    Get compliance metrics overview.

    Returns:
    - Overall compliance coverage percentage
    - Coverage metrics per framework (SOC2, ISO27001, etc.)
    - Vendors with findings vs fully compliant
    - Average findings per vendor
    - Critical gaps by framework

    Useful for understanding compliance posture across the vendor portfolio.
    Requires authentication. Data is scoped to the user's organization.
    """
    metrics = await get_compliance_metrics(db, current_user.organization_id)
    return ComplianceMetricsResponse(
        data=metrics,
        generated_at=datetime.utcnow(),
    )


@router.get("/activity", response_model=ActivityTimelineResponse)
async def get_activity(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    action: Annotated[
        str | None,
        Query(description="Filter by action type (CREATE, UPDATE, DELETE, etc.)"),
    ] = None,
    resource_type: Annotated[
        str | None,
        Query(description="Filter by resource type (vendor, document, finding, etc.)"),
    ] = None,
    user_id: Annotated[
        str | None,
        Query(description="Filter by user ID"),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=200, description="Number of activities to return"),
    ] = 50,
    offset: Annotated[
        int,
        Query(ge=0, description="Pagination offset"),
    ] = 0,
) -> ActivityTimelineResponse:
    """
    Get activity timeline from audit logs.

    Returns a chronological list of recent activities including:
    - Timestamp and action type
    - Resource type and ID
    - User information
    - Additional details

    Filters:
    - action: Filter by action type (CREATE, UPDATE, DELETE, LOGIN, etc.)
    - resource_type: Filter by resource (vendor, document, finding, etc.)
    - user_id: Filter by specific user
    - limit: Number of items per page (max 200)
    - offset: Pagination offset

    Useful for audit trails and monitoring system activity.
    Requires authentication. Data is scoped to the user's organization.
    """
    timeline = await get_activity_timeline(
        db=db,
        organization_id=current_user.organization_id,
        action=action,
        resource_type=resource_type,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return ActivityTimelineResponse(
        data=timeline,
        generated_at=datetime.utcnow(),
    )
