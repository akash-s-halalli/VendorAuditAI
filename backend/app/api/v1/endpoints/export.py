"""Export API endpoints for findings data."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.middleware.rate_limit import limiter
from app.models import User
from app.services.export import (
    CSVExporter,
    PDFExporter,
    get_findings_for_export,
)

router = APIRouter(tags=["Export"])


@router.get("/findings/csv")
@limiter.limit("5/minute")
async def export_findings_csv(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    document_id: str | None = Query(None, description="Filter by document ID"),
    vendor_id: str | None = Query(None, description="Filter by vendor ID"),
    severity: str | None = Query(None, description="Filter by severity"),
    framework_id: str | None = Query(None, description="Filter by framework"),
) -> Response:
    """
    Export findings to CSV format.

    Returns a CSV file containing findings with columns:
    id, title, description, severity, framework, control, page, confidence

    Supports filtering by document, vendor, severity, and framework.
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
