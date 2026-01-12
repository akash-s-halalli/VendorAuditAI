"""Analytics service for dashboard statistics and metrics."""

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, case, distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AuditLog,
    Document,
    DocumentStatus,
    DocumentType,
    Finding,
    FindingSeverity,
    FindingStatus,
    User,
    Vendor,
    VendorStatus,
    VendorTier,
)
from app.models.remediation import RemediationStatus, RemediationTask
from app.schemas.analytics import (
    ActivityItem,
    ActivityTimeline,
    CategoryDistribution,
    ComplianceMetrics,
    DashboardStats,
    FindingsSummary,
    FindingStatusBreakdown,
    FrameworkBreakdown,
    FrameworkCoverage,
    SeverityBreakdown,
    StatusDistribution,
    TierDistribution,
    TimeSeriesDataPoint,
    VendorDistribution,
)


class AnalyticsService:
    """Service for generating analytics and dashboard statistics."""

    def __init__(self, db: AsyncSession, organization_id: str):
        """Initialize analytics service.

        Args:
            db: Database session
            organization_id: Organization ID to scope queries
        """
        self.db = db
        self.organization_id = organization_id

    async def get_dashboard_stats(self) -> DashboardStats:
        """Get overall dashboard statistics.

        Returns aggregated counts and metrics for the main dashboard.
        """
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Run all queries in parallel for performance
        results = await asyncio.gather(
            self._get_vendor_counts(),
            self._get_document_counts(start_of_month),
            self._get_finding_counts(start_of_month),
            self._get_remediation_counts(),
            return_exceptions=True,
        )

        # Unpack results with error handling
        vendor_counts = results[0] if not isinstance(results[0], Exception) else {}
        doc_counts = results[1] if not isinstance(results[1], Exception) else {}
        finding_counts = results[2] if not isinstance(results[2], Exception) else {}
        remediation_counts = (
            results[3] if not isinstance(results[3], Exception) else {}
        )

        return DashboardStats(
            total_vendors=vendor_counts.get("total", 0),
            active_vendors=vendor_counts.get("active", 0),
            high_risk_vendors=vendor_counts.get("high_risk", 0),
            total_documents=doc_counts.get("total", 0),
            pending_documents=doc_counts.get("pending", 0),
            documents_this_month=doc_counts.get("this_month", 0),
            total_findings=finding_counts.get("total", 0),
            open_findings=finding_counts.get("open", 0),
            critical_findings=finding_counts.get("critical", 0),
            findings_this_month=finding_counts.get("this_month", 0),
            total_remediation_tasks=remediation_counts.get("total", 0),
            overdue_tasks=remediation_counts.get("overdue", 0),
            avg_compliance_score=None,  # To be calculated based on business logic
        )

    async def _get_vendor_counts(self) -> dict[str, int]:
        """Get vendor-related counts."""
        # Total vendors
        total_result = await self.db.execute(
            select(func.count(Vendor.id)).where(
                Vendor.organization_id == self.organization_id
            )
        )
        total = total_result.scalar() or 0

        # Active vendors
        active_result = await self.db.execute(
            select(func.count(Vendor.id)).where(
                and_(
                    Vendor.organization_id == self.organization_id,
                    Vendor.status == VendorStatus.ACTIVE.value,
                )
            )
        )
        active = active_result.scalar() or 0

        # High risk vendors (critical or high tier)
        high_risk_result = await self.db.execute(
            select(func.count(Vendor.id)).where(
                and_(
                    Vendor.organization_id == self.organization_id,
                    Vendor.tier.in_([VendorTier.CRITICAL.value, VendorTier.HIGH.value]),
                )
            )
        )
        high_risk = high_risk_result.scalar() or 0

        return {"total": total, "active": active, "high_risk": high_risk}

    async def _get_document_counts(self, start_of_month: datetime) -> dict[str, int]:
        """Get document-related counts."""
        # Total documents
        total_result = await self.db.execute(
            select(func.count(Document.id)).where(
                Document.organization_id == self.organization_id
            )
        )
        total = total_result.scalar() or 0

        # Pending documents
        pending_result = await self.db.execute(
            select(func.count(Document.id)).where(
                and_(
                    Document.organization_id == self.organization_id,
                    Document.status.in_(
                        [DocumentStatus.PENDING.value, DocumentStatus.PROCESSING.value]
                    ),
                )
            )
        )
        pending = pending_result.scalar() or 0

        # Documents this month
        this_month_result = await self.db.execute(
            select(func.count(Document.id)).where(
                and_(
                    Document.organization_id == self.organization_id,
                    Document.created_at >= start_of_month,
                )
            )
        )
        this_month = this_month_result.scalar() or 0

        return {"total": total, "pending": pending, "this_month": this_month}

    async def _get_finding_counts(self, start_of_month: datetime) -> dict[str, int]:
        """Get finding-related counts."""
        # Total findings
        total_result = await self.db.execute(
            select(func.count(Finding.id)).where(
                Finding.organization_id == self.organization_id
            )
        )
        total = total_result.scalar() or 0

        # Open findings
        open_result = await self.db.execute(
            select(func.count(Finding.id)).where(
                and_(
                    Finding.organization_id == self.organization_id,
                    Finding.status == FindingStatus.OPEN.value,
                )
            )
        )
        open_count = open_result.scalar() or 0

        # Critical findings
        critical_result = await self.db.execute(
            select(func.count(Finding.id)).where(
                and_(
                    Finding.organization_id == self.organization_id,
                    Finding.severity == FindingSeverity.CRITICAL.value,
                )
            )
        )
        critical = critical_result.scalar() or 0

        # Findings this month
        this_month_result = await self.db.execute(
            select(func.count(Finding.id)).where(
                and_(
                    Finding.organization_id == self.organization_id,
                    Finding.created_at >= start_of_month,
                )
            )
        )
        this_month = this_month_result.scalar() or 0

        return {
            "total": total,
            "open": open_count,
            "critical": critical,
            "this_month": this_month,
        }

    async def _get_remediation_counts(self) -> dict[str, int]:
        """Get remediation task counts."""
        now = datetime.utcnow()

        # Total tasks
        total_result = await self.db.execute(
            select(func.count(RemediationTask.id)).where(
                RemediationTask.organization_id == self.organization_id
            )
        )
        total = total_result.scalar() or 0

        # Overdue tasks (past due date and not closed)
        closed_statuses = [
            RemediationStatus.CLOSED.value,
            RemediationStatus.VERIFIED.value,
            RemediationStatus.EXCEPTION_APPROVED.value,
        ]
        overdue_result = await self.db.execute(
            select(func.count(RemediationTask.id)).where(
                and_(
                    RemediationTask.organization_id == self.organization_id,
                    RemediationTask.due_date < now,
                    ~RemediationTask.status.in_(closed_statuses),
                )
            )
        )
        overdue = overdue_result.scalar() or 0

        return {"total": total, "overdue": overdue}

    async def get_vendor_distribution(self) -> VendorDistribution:
        """Get vendor distribution by category, tier, and status."""
        # Get distribution by category
        category_result = await self.db.execute(
            select(Vendor.category, func.count(Vendor.id).label("count"))
            .where(Vendor.organization_id == self.organization_id)
            .group_by(Vendor.category)
        )
        category_rows = category_result.all()

        # Get distribution by tier
        tier_result = await self.db.execute(
            select(Vendor.tier, func.count(Vendor.id).label("count"))
            .where(Vendor.organization_id == self.organization_id)
            .group_by(Vendor.tier)
        )
        tier_rows = tier_result.all()

        # Get distribution by status
        status_result = await self.db.execute(
            select(Vendor.status, func.count(Vendor.id).label("count"))
            .where(Vendor.organization_id == self.organization_id)
            .group_by(Vendor.status)
        )
        status_rows = status_result.all()

        # Calculate total vendors
        total_vendors = sum(row[1] for row in tier_rows)

        # Build category distribution with percentages
        by_category = []
        for row in category_rows:
            category_name = row[0] or "Uncategorized"
            count = row[1]
            percentage = (count / total_vendors * 100) if total_vendors > 0 else 0
            by_category.append(
                CategoryDistribution(
                    name=category_name,
                    count=count,
                    percentage=round(percentage, 2),
                )
            )

        # Sort by count descending
        by_category.sort(key=lambda x: x.count, reverse=True)

        # Build tier distribution
        tier_dict = {row[0]: row[1] for row in tier_rows}
        by_tier = TierDistribution(
            critical=tier_dict.get(VendorTier.CRITICAL.value, 0),
            high=tier_dict.get(VendorTier.HIGH.value, 0),
            medium=tier_dict.get(VendorTier.MEDIUM.value, 0),
            low=tier_dict.get(VendorTier.LOW.value, 0),
        )

        # Build status distribution
        status_dict = {row[0]: row[1] for row in status_rows}
        by_status = StatusDistribution(
            active=status_dict.get(VendorStatus.ACTIVE.value, 0),
            inactive=status_dict.get(VendorStatus.INACTIVE.value, 0),
            onboarding=status_dict.get(VendorStatus.ONBOARDING.value, 0),
            offboarding=status_dict.get(VendorStatus.OFFBOARDING.value, 0),
        )

        return VendorDistribution(
            by_category=by_category,
            by_tier=by_tier,
            by_status=by_status,
            total_vendors=total_vendors,
        )

    async def get_findings_analytics(
        self,
        severity: str | None = None,
        status: str | None = None,
        framework: str | None = None,
        vendor_id: str | None = None,
        days: int = 30,
    ) -> FindingsSummary:
        """Get findings analytics with optional filters.

        Args:
            severity: Filter by severity level
            status: Filter by finding status
            framework: Filter by compliance framework
            vendor_id: Filter by vendor ID
            days: Number of days to look back for trends
        """
        # Build base filter conditions
        conditions = [Finding.organization_id == self.organization_id]

        if severity:
            conditions.append(Finding.severity == severity)
        if status:
            conditions.append(Finding.status == status)
        if framework:
            conditions.append(Finding.framework == framework)
        if vendor_id:
            # Join with documents to filter by vendor
            conditions.append(Finding.document_id.in_(
                select(Document.id).where(Document.vendor_id == vendor_id)
            ))

        combined_condition = and_(*conditions)

        # Get total findings with filters
        total_result = await self.db.execute(
            select(func.count(Finding.id)).where(combined_condition)
        )
        total_findings = total_result.scalar() or 0

        # Get severity breakdown (always unfiltered by severity for the breakdown)
        severity_conditions = [
            c for c in conditions if "severity" not in str(c).lower()
        ]
        severity_base = and_(*severity_conditions) if severity_conditions else True

        severity_result = await self.db.execute(
            select(Finding.severity, func.count(Finding.id).label("count"))
            .where(severity_base if severity_conditions else Finding.organization_id == self.organization_id)
            .group_by(Finding.severity)
        )
        severity_rows = severity_result.all()
        severity_dict = {row[0]: row[1] for row in severity_rows}

        by_severity = SeverityBreakdown(
            critical=severity_dict.get(FindingSeverity.CRITICAL.value, 0),
            high=severity_dict.get(FindingSeverity.HIGH.value, 0),
            medium=severity_dict.get(FindingSeverity.MEDIUM.value, 0),
            low=severity_dict.get(FindingSeverity.LOW.value, 0),
            info=severity_dict.get(FindingSeverity.INFO.value, 0),
        )

        # Get status breakdown
        status_conditions = [c for c in conditions if "status" not in str(c).lower()]
        status_base = and_(*status_conditions) if status_conditions else True

        status_result = await self.db.execute(
            select(Finding.status, func.count(Finding.id).label("count"))
            .where(status_base if status_conditions else Finding.organization_id == self.organization_id)
            .group_by(Finding.status)
        )
        status_rows = status_result.all()
        status_dict = {row[0]: row[1] for row in status_rows}

        by_status = FindingStatusBreakdown(
            open=status_dict.get(FindingStatus.OPEN.value, 0),
            acknowledged=status_dict.get(FindingStatus.ACKNOWLEDGED.value, 0),
            remediated=status_dict.get(FindingStatus.REMEDIATED.value, 0),
            accepted=status_dict.get(FindingStatus.ACCEPTED.value, 0),
            false_positive=status_dict.get(FindingStatus.FALSE_POSITIVE.value, 0),
        )

        # Get framework breakdown with severity counts
        framework_result = await self.db.execute(
            select(
                Finding.framework,
                func.count(Finding.id).label("count"),
                func.sum(
                    case(
                        (Finding.severity == FindingSeverity.CRITICAL.value, 1),
                        else_=0,
                    )
                ).label("critical"),
                func.sum(
                    case(
                        (Finding.severity == FindingSeverity.HIGH.value, 1), else_=0
                    )
                ).label("high"),
            )
            .where(Finding.organization_id == self.organization_id)
            .group_by(Finding.framework)
            .order_by(func.count(Finding.id).desc())
        )
        framework_rows = framework_result.all()

        by_framework = [
            FrameworkBreakdown(
                framework=row[0] or "Unknown",
                count=row[1],
                critical=row[2] or 0,
                high=row[3] or 0,
            )
            for row in framework_rows
        ]

        # Get trend for last N days
        start_date = datetime.utcnow() - timedelta(days=days)
        trend_result = await self.db.execute(
            select(
                func.date(Finding.created_at).label("date"),
                func.count(Finding.id).label("count"),
            )
            .where(
                and_(
                    Finding.organization_id == self.organization_id,
                    Finding.created_at >= start_date,
                )
            )
            .group_by(func.date(Finding.created_at))
            .order_by(func.date(Finding.created_at))
        )
        trend_rows = trend_result.all()

        trend_last_30_days = [
            TimeSeriesDataPoint(
                date=str(row[0]),
                count=row[1],
            )
            for row in trend_rows
        ]

        # Calculate average resolution time
        resolution_result = await self.db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch", Finding.resolved_at - Finding.created_at
                    ) / 86400  # Convert to days
                )
            ).where(
                and_(
                    Finding.organization_id == self.organization_id,
                    Finding.resolved_at.isnot(None),
                )
            )
        )
        avg_resolution = resolution_result.scalar()
        avg_resolution_time_days = (
            round(float(avg_resolution), 2) if avg_resolution else None
        )

        return FindingsSummary(
            total_findings=total_findings,
            by_severity=by_severity,
            by_status=by_status,
            by_framework=by_framework,
            trend_last_30_days=trend_last_30_days,
            avg_resolution_time_days=avg_resolution_time_days,
        )

    async def get_compliance_metrics(self) -> ComplianceMetrics:
        """Get compliance coverage metrics across frameworks."""
        # Get framework coverage data
        framework_result = await self.db.execute(
            select(
                Finding.framework,
                func.count(distinct(Document.vendor_id)).label("vendors_assessed"),
                func.count(Finding.id).label("findings_count"),
                func.sum(
                    case(
                        (Finding.severity == FindingSeverity.CRITICAL.value, 1),
                        else_=0,
                    )
                ).label("critical_gaps"),
            )
            .join(Document, Finding.document_id == Document.id)
            .where(Finding.organization_id == self.organization_id)
            .group_by(Finding.framework)
        )
        framework_rows = framework_result.all()

        frameworks = []
        for row in framework_rows:
            frameworks.append(
                FrameworkCoverage(
                    framework=row[0] or "Unknown",
                    vendors_assessed=row[1] or 0,
                    total_controls=0,  # Would need control mapping data
                    controls_covered=0,  # Would need control mapping data
                    coverage_percentage=0.0,  # Would need control mapping data
                    findings_count=row[2] or 0,
                    critical_gaps=row[3] or 0,
                )
            )

        # Get vendors with findings
        vendors_with_findings_result = await self.db.execute(
            select(func.count(distinct(Document.vendor_id))).where(
                and_(
                    Document.organization_id == self.organization_id,
                    Document.vendor_id.isnot(None),
                    Document.id.in_(
                        select(Finding.document_id).where(
                            Finding.organization_id == self.organization_id
                        )
                    ),
                )
            )
        )
        vendors_with_findings = vendors_with_findings_result.scalar() or 0

        # Get total vendors with documents
        total_vendors_result = await self.db.execute(
            select(func.count(distinct(Document.vendor_id))).where(
                and_(
                    Document.organization_id == self.organization_id,
                    Document.vendor_id.isnot(None),
                )
            )
        )
        total_vendors = total_vendors_result.scalar() or 0

        # Vendors fully compliant (have documents but no open findings)
        vendors_with_open_findings_result = await self.db.execute(
            select(func.count(distinct(Document.vendor_id))).where(
                and_(
                    Document.organization_id == self.organization_id,
                    Document.vendor_id.isnot(None),
                    Document.id.in_(
                        select(Finding.document_id).where(
                            and_(
                                Finding.organization_id == self.organization_id,
                                Finding.status == FindingStatus.OPEN.value,
                            )
                        )
                    ),
                )
            )
        )
        vendors_with_open_findings = vendors_with_open_findings_result.scalar() or 0
        vendors_fully_compliant = max(0, total_vendors - vendors_with_open_findings)

        # Average findings per vendor
        total_findings_result = await self.db.execute(
            select(func.count(Finding.id)).where(
                Finding.organization_id == self.organization_id
            )
        )
        total_findings = total_findings_result.scalar() or 0
        avg_findings_per_vendor = (
            round(total_findings / total_vendors, 2) if total_vendors > 0 else 0.0
        )

        # Calculate overall coverage (placeholder - would need control data)
        overall_coverage = 0.0
        if total_vendors > 0:
            overall_coverage = round(
                (vendors_fully_compliant / total_vendors) * 100, 2
            )

        return ComplianceMetrics(
            overall_coverage=overall_coverage,
            frameworks=frameworks,
            vendors_with_findings=vendors_with_findings,
            vendors_fully_compliant=vendors_fully_compliant,
            avg_findings_per_vendor=avg_findings_per_vendor,
        )

    async def get_activity_timeline(
        self,
        action: str | None = None,
        resource_type: str | None = None,
        user_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ActivityTimeline:
        """Get recent activity timeline from audit logs.

        Args:
            action: Filter by action type
            resource_type: Filter by resource type
            user_id: Filter by user ID
            limit: Number of activities to return
            offset: Pagination offset
        """
        # Build filter conditions
        conditions = [AuditLog.organization_id == self.organization_id]

        if action:
            conditions.append(AuditLog.action == action)
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        if user_id:
            conditions.append(AuditLog.user_id == user_id)

        combined_condition = and_(*conditions)

        # Get total count for pagination
        count_result = await self.db.execute(
            select(func.count(AuditLog.id)).where(combined_condition)
        )
        total_count = count_result.scalar() or 0

        # Get activities with user information
        activities_result = await self.db.execute(
            select(AuditLog, User.email)
            .outerjoin(User, AuditLog.user_id == User.id)
            .where(combined_condition)
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        activity_rows = activities_result.all()

        activities = []
        for row in activity_rows:
            audit_log = row[0]
            user_email = row[1]

            # Try to get resource name from new_values or details
            resource_name = None
            if audit_log.new_values and isinstance(audit_log.new_values, dict):
                resource_name = audit_log.new_values.get(
                    "name", audit_log.new_values.get("title")
                )

            activities.append(
                ActivityItem(
                    id=audit_log.id,
                    timestamp=audit_log.created_at,
                    action=audit_log.action,
                    resource_type=audit_log.resource_type,
                    resource_id=audit_log.resource_id,
                    resource_name=resource_name,
                    user_id=audit_log.user_id,
                    user_email=user_email,
                    details=audit_log.details,
                )
            )

        has_more = (offset + limit) < total_count

        return ActivityTimeline(
            activities=activities,
            total_count=total_count,
            has_more=has_more,
        )


# Convenience functions for direct use
async def get_dashboard_stats(db: AsyncSession, organization_id: str) -> DashboardStats:
    """Get dashboard statistics for an organization."""
    service = AnalyticsService(db, organization_id)
    return await service.get_dashboard_stats()


async def get_vendor_distribution(
    db: AsyncSession, organization_id: str
) -> VendorDistribution:
    """Get vendor distribution for an organization."""
    service = AnalyticsService(db, organization_id)
    return await service.get_vendor_distribution()


async def get_findings_analytics(
    db: AsyncSession,
    organization_id: str,
    severity: str | None = None,
    status: str | None = None,
    framework: str | None = None,
    vendor_id: str | None = None,
    days: int = 30,
) -> FindingsSummary:
    """Get findings analytics for an organization."""
    service = AnalyticsService(db, organization_id)
    return await service.get_findings_analytics(
        severity=severity,
        status=status,
        framework=framework,
        vendor_id=vendor_id,
        days=days,
    )


async def get_compliance_metrics(
    db: AsyncSession, organization_id: str
) -> ComplianceMetrics:
    """Get compliance metrics for an organization."""
    service = AnalyticsService(db, organization_id)
    return await service.get_compliance_metrics()


async def get_activity_timeline(
    db: AsyncSession,
    organization_id: str,
    action: str | None = None,
    resource_type: str | None = None,
    user_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> ActivityTimeline:
    """Get activity timeline for an organization."""
    service = AnalyticsService(db, organization_id)
    return await service.get_activity_timeline(
        action=action,
        resource_type=resource_type,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
