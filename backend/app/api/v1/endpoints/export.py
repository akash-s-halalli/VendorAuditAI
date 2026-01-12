"""Export API endpoints for findings, vendors, remediation, and compliance data."""

from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_active_user
from app.db import get_db
from app.middleware.rate_limit import limiter
from app.models import User
from app.models.finding import Finding
from app.models.remediation import RemediationTask
from app.models.vendor import Vendor
from app.schemas.export import (
    ExportFormat,
    FindingExportFilters,
    RemediationExportFilters,
    VendorExportFilters,
)
from app.services.csv_export import (
    FindingCSVExporter,
    RemediationCSVExporter,
    VendorCSVExporter,
)
from app.services.excel_export import (
    ComplianceReportExporter,
    FindingExcelExporter,
    RemediationExcelExporter,
    VendorExcelExporter,
    VendorReportExporter,
)
from app.services.export import (
    CSVExporter,
    PDFExporter,
    get_findings_for_export,
)

router = APIRouter(tags=["Export"])


# Helper functions for data fetching
async def get_vendors_for_export(
    db: AsyncSession,
    org_id: str,
    filters: VendorExportFilters | None = None,
) -> list[Vendor]:
    """Fetch vendors with optional filters."""
    query = select(Vendor).where(Vendor.organization_id == org_id)

    if filters:
        if filters.status:
            query = query.where(Vendor.status == filters.status)
        if filters.tier:
            query = query.where(Vendor.tier == filters.tier)
        if filters.category:
            query = query.where(Vendor.category == filters.category)
        if filters.contract_expiry_before:
            query = query.where(Vendor.contract_expiry <= filters.contract_expiry_before)
        if filters.contract_expiry_after:
            query = query.where(Vendor.contract_expiry >= filters.contract_expiry_after)
        if filters.assessment_due_before:
            query = query.where(
                Vendor.next_assessment_due <= filters.assessment_due_before
            )

    query = query.order_by(Vendor.name)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_findings_for_export_filtered(
    db: AsyncSession,
    org_id: str,
    filters: FindingExportFilters | None = None,
) -> list[Finding]:
    """Fetch findings with optional filters."""
    query = (
        select(Finding)
        .join(Finding.document)
        .join(Finding.document.property.mapper.class_.vendor)
        .where(Finding.document.property.mapper.class_.vendor.property.mapper.class_.organization_id == org_id)
    )

    # Use simpler approach - get all findings for org and filter
    from app.models.document import Document

    query = (
        select(Finding)
        .join(Document, Finding.document_id == Document.id)
        .join(Vendor, Document.vendor_id == Vendor.id)
        .where(Vendor.organization_id == org_id)
    )

    if filters:
        if filters.status:
            query = query.where(Finding.status == filters.status)
        if filters.severity:
            query = query.where(Finding.severity == filters.severity)
        if filters.vendor_id:
            query = query.where(Vendor.id == filters.vendor_id)
        if filters.document_id:
            query = query.where(Finding.document_id == filters.document_id)
        if filters.framework:
            query = query.where(Finding.framework == filters.framework)
        if filters.created_from:
            query = query.where(Finding.created_at >= filters.created_from)
        if filters.created_to:
            query = query.where(Finding.created_at <= filters.created_to)

    query = query.order_by(Finding.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_remediation_for_export(
    db: AsyncSession,
    org_id: str,
    filters: RemediationExportFilters | None = None,
) -> list[RemediationTask]:
    """Fetch remediation tasks with optional filters."""
    query = (
        select(RemediationTask)
        .join(Vendor, RemediationTask.vendor_id == Vendor.id)
        .options(
            selectinload(RemediationTask.vendor),
            selectinload(RemediationTask.assignee),
            selectinload(RemediationTask.finding),
        )
        .where(Vendor.organization_id == org_id)
    )

    if filters:
        if filters.status:
            query = query.where(RemediationTask.status == filters.status)
        if filters.priority:
            query = query.where(RemediationTask.priority == filters.priority)
        if filters.vendor_id:
            query = query.where(RemediationTask.vendor_id == filters.vendor_id)
        if filters.assignee_id:
            query = query.where(RemediationTask.assignee_id == filters.assignee_id)
        if filters.sla_breached is not None:
            query = query.where(RemediationTask.sla_breached == filters.sla_breached)
        if filters.overdue_only:
            from datetime import datetime

            query = query.where(RemediationTask.due_date < datetime.utcnow().date())
        if filters.due_before:
            query = query.where(RemediationTask.due_date <= filters.due_before)
        if filters.due_after:
            query = query.where(RemediationTask.due_date >= filters.due_after)

    query = query.order_by(RemediationTask.due_date.asc())
    result = await db.execute(query)
    return list(result.scalars().all())


# Vendor Export Endpoints
@router.get("/vendors")
@limiter.limit("10/minute")
async def export_vendors(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    format: ExportFormat = Query(ExportFormat.XLSX, description="Export format"),
    status: Literal["active", "inactive", "onboarding", "offboarding"] | None = Query(
        None, description="Filter by status"
    ),
    tier: Literal["critical", "high", "medium", "low"] | None = Query(
        None, description="Filter by tier"
    ),
    category: str | None = Query(None, description="Filter by category"),
    contract_expiry_before: date | None = Query(
        None, description="Contracts expiring before date"
    ),
    contract_expiry_after: date | None = Query(
        None, description="Contracts expiring after date"
    ),
    assessment_due_before: date | None = Query(
        None, description="Assessments due before date"
    ),
) -> Response:
    """
    Export vendors to CSV or Excel format.

    Returns a file containing vendor data with columns:
    id, name, description, website, tier, status, category, criticality_score,
    data_classification, contract_expiry, last_assessed, next_assessment_due, created_at

    Excel format includes bold headers, auto-sized columns, and frozen header row.
    """
    filters = VendorExportFilters(
        status=status,
        tier=tier,
        category=category,
        contract_expiry_before=contract_expiry_before,
        contract_expiry_after=contract_expiry_after,
        assessment_due_before=assessment_due_before,
    )

    vendors = await get_vendors_for_export(
        db=db, org_id=current_user.organization_id, filters=filters
    )

    # Generate filename
    filename_parts = ["vendors"]
    if status:
        filename_parts.append(status)
    if tier:
        filename_parts.append(tier)

    if format == ExportFormat.CSV:
        exporter = VendorCSVExporter(vendors)
        content = exporter.generate()
        filename = "_".join(filename_parts) + ".csv"
        media_type = "text/csv"
    else:
        exporter = VendorExcelExporter(vendors)
        content = exporter.generate()
        filename = "_".join(filename_parts) + ".xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
        },
    )


@router.get("/vendors/{vendor_id}/report")
@limiter.limit("5/minute")
async def export_vendor_report(
    request: Request,
    vendor_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    format: ExportFormat = Query(ExportFormat.XLSX, description="Export format"),
) -> Response:
    """
    Export a comprehensive vendor report to Excel format.

    Returns a multi-sheet Excel workbook containing:
    - Vendor Summary: Basic vendor information
    - Documents: All documents for the vendor
    - Findings: All findings from vendor documents
    - Remediation: All remediation tasks for the vendor

    Each sheet has professional formatting with bold headers, color-coded
    severity/status indicators, and frozen header rows.
    """
    # Verify vendor belongs to user's organization
    query = select(Vendor).where(
        Vendor.id == vendor_id, Vendor.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    exporter = VendorReportExporter(vendor_id=vendor_id, db=db)
    content = await exporter.generate()

    filename = f"vendor_report_{vendor.name.replace(' ', '_')}.xlsx"
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
        },
    )


# Findings Export Endpoints
@router.get("/findings")
@limiter.limit("10/minute")
async def export_findings(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    format: ExportFormat = Query(ExportFormat.XLSX, description="Export format"),
    status: Literal[
        "open", "acknowledged", "remediated", "accepted", "false_positive"
    ] | None = Query(None, description="Filter by status"),
    severity: Literal["critical", "high", "medium", "low", "info"] | None = Query(
        None, description="Filter by severity"
    ),
    vendor_id: str | None = Query(None, description="Filter by vendor"),
    document_id: str | None = Query(None, description="Filter by document"),
    framework: str | None = Query(None, description="Filter by framework"),
    created_from: date | None = Query(None, description="Created on or after date"),
    created_to: date | None = Query(None, description="Created on or before date"),
) -> Response:
    """
    Export findings to CSV or Excel format.

    Returns a file containing finding data with columns:
    id, title, description, severity, status, framework, control, evidence,
    remediation, impact, page_number, section, confidence, document_id,
    created_at, resolved_at

    Excel format includes color-coded severity (Critical=Red, High=Orange,
    Medium=Yellow, Low=Green, Info=Light Blue) and frozen header row.
    """
    filters = FindingExportFilters(
        status=status,
        severity=severity,
        vendor_id=vendor_id,
        document_id=document_id,
        framework=framework,
        created_from=created_from,
        created_to=created_to,
    )

    findings = await get_findings_for_export_filtered(
        db=db, org_id=current_user.organization_id, filters=filters
    )

    # Generate filename
    filename_parts = ["findings"]
    if severity:
        filename_parts.append(severity)
    if status:
        filename_parts.append(status)
    if vendor_id:
        filename_parts.append(f"vendor_{vendor_id[:8]}")

    if format == ExportFormat.CSV:
        exporter = FindingCSVExporter(findings)
        content = exporter.generate()
        filename = "_".join(filename_parts) + ".csv"
        media_type = "text/csv"
    else:
        exporter = FindingExcelExporter(findings)
        content = exporter.generate()
        filename = "_".join(filename_parts) + ".xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
        },
    )


# Remediation Export Endpoints
@router.get("/remediation")
@limiter.limit("10/minute")
async def export_remediation(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    format: ExportFormat = Query(ExportFormat.XLSX, description="Export format"),
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
    ] | None = Query(None, description="Filter by status"),
    priority: Literal["critical", "high", "medium", "low"] | None = Query(
        None, description="Filter by priority"
    ),
    vendor_id: str | None = Query(None, description="Filter by vendor"),
    assignee_id: str | None = Query(None, description="Filter by assignee"),
    sla_breached: bool | None = Query(None, description="Filter by SLA breach status"),
    overdue_only: bool = Query(False, description="Only show overdue tasks"),
    due_before: date | None = Query(None, description="Tasks due before date"),
    due_after: date | None = Query(None, description="Tasks due after date"),
) -> Response:
    """
    Export remediation tasks to CSV or Excel format.

    Returns a file containing remediation task data with columns:
    id, title, description, status, priority, vendor_name, assignee_email,
    finding_id, finding_title, due_date, sla_days, sla_breached, resolution_notes,
    created_at, resolved_at

    Excel format includes color-coded priority and SLA breach indicators.
    """
    filters = RemediationExportFilters(
        status=status,
        priority=priority,
        vendor_id=vendor_id,
        assignee_id=assignee_id,
        sla_breached=sla_breached,
        overdue_only=overdue_only,
        due_before=due_before,
        due_after=due_after,
    )

    tasks = await get_remediation_for_export(
        db=db, org_id=current_user.organization_id, filters=filters
    )

    # Generate filename
    filename_parts = ["remediation"]
    if priority:
        filename_parts.append(priority)
    if status:
        filename_parts.append(status)
    if overdue_only:
        filename_parts.append("overdue")

    if format == ExportFormat.CSV:
        exporter = RemediationCSVExporter(tasks)
        content = exporter.generate()
        filename = "_".join(filename_parts) + ".csv"
        media_type = "text/csv"
    else:
        exporter = RemediationExcelExporter(tasks)
        content = exporter.generate()
        filename = "_".join(filename_parts) + ".xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
        },
    )


# Compliance Report Export Endpoint
@router.get("/compliance/{vendor_id}")
@limiter.limit("5/minute")
async def export_compliance_report(
    request: Request,
    vendor_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    format: ExportFormat = Query(ExportFormat.XLSX, description="Export format"),
    frameworks: str | None = Query(
        None, description="Comma-separated list of frameworks to include"
    ),
    include_findings: bool = Query(True, description="Include detailed findings"),
    include_remediation: bool = Query(True, description="Include remediation tasks"),
    include_summary: bool = Query(True, description="Include executive summary"),
) -> Response:
    """
    Export a comprehensive compliance report for a vendor.

    Returns a multi-sheet Excel workbook containing:
    - Executive Summary: High-level compliance status and metrics
    - Compliance Matrix: Framework control mappings and compliance status
    - Findings Detail: All findings grouped by framework
    - Remediation Status: All remediation tasks with status tracking

    Color-coded severity and compliance status indicators throughout.
    """
    # Verify vendor belongs to user's organization
    query = select(Vendor).where(
        Vendor.id == vendor_id, Vendor.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Parse frameworks list
    framework_list = None
    if frameworks:
        framework_list = [f.strip() for f in frameworks.split(",")]

    exporter = ComplianceReportExporter(
        vendor_id=vendor_id,
        db=db,
        frameworks=framework_list,
        include_findings=include_findings,
        include_remediation=include_remediation,
        include_summary=include_summary,
    )
    content = await exporter.generate()

    filename = f"compliance_report_{vendor.name.replace(' ', '_')}.xlsx"
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
        },
    )


# Legacy Endpoints (kept for backward compatibility)
@router.get("/findings/csv")
@limiter.limit("5/minute")
async def export_findings_csv_legacy(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    document_id: str | None = Query(None, description="Filter by document ID"),
    vendor_id: str | None = Query(None, description="Filter by vendor ID"),
    severity: str | None = Query(None, description="Filter by severity"),
    framework_id: str | None = Query(None, description="Filter by framework"),
) -> Response:
    """
    [LEGACY] Export findings to CSV format.

    This endpoint is maintained for backward compatibility.
    Use GET /export/findings?format=csv for new integrations.
    """
    findings, _, _ = await get_findings_for_export(
        db=db,
        org_id=current_user.organization_id,
        document_id=document_id,
        vendor_id=vendor_id,
        severity=severity,
        framework_id=framework_id,
    )

    exporter = CSVExporter(findings)
    csv_content = exporter.generate()

    # Generate filename based on filters
    filename_parts = ["findings"]
    if vendor_id:
        filename_parts.append(f"vendor_{vendor_id[:8]}")
    if document_id:
        filename_parts.append(f"doc_{document_id[:8]}")
    if severity:
        filename_parts.append(severity)
    if framework_id:
        filename_parts.append(framework_id)
    filename = "_".join(filename_parts) + ".csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(csv_content)),
        },
    )


@router.get("/findings/pdf")
@limiter.limit("5/minute")
async def export_findings_pdf(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    document_id: str | None = Query(None, description="Filter by document ID"),
    vendor_id: str | None = Query(None, description="Filter by vendor ID"),
    severity: str | None = Query(None, description="Filter by severity"),
    framework_id: str | None = Query(None, description="Filter by framework"),
) -> Response:
    """
    Export findings to PDF format.

    Returns a PDF report containing:
    - Header with vendor name and document title
    - Executive summary with findings count by severity
    - Detailed findings table
    - Footer with generation timestamp

    Supports filtering by document, vendor, severity, and framework.
    """
    findings, vendor, document = await get_findings_for_export(
        db=db,
        org_id=current_user.organization_id,
        document_id=document_id,
        vendor_id=vendor_id,
        severity=severity,
        framework_id=framework_id,
    )

    exporter = PDFExporter(findings, vendor=vendor, document=document)
    pdf_content = exporter.generate()

    # Generate filename based on filters
    filename_parts = ["findings_report"]
    if vendor_id:
        filename_parts.append(f"vendor_{vendor_id[:8]}")
    if document_id:
        filename_parts.append(f"doc_{document_id[:8]}")
    if severity:
        filename_parts.append(severity)
    if framework_id:
        filename_parts.append(framework_id)
    filename = "_".join(filename_parts) + ".pdf"

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_content)),
        },
    )
