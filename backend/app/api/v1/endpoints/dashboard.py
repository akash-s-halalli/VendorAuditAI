"""Dashboard statistics API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import (
    Document,
    DocumentStatus,
    Finding,
    FindingSeverity,
    User,
    Vendor,
)

router = APIRouter(tags=["Dashboard"])


class DashboardStatsResponse(BaseModel):
    """Response model for dashboard statistics."""

    totalVendors: int
    totalDocuments: int
    pendingAnalysis: int
    completedAnalysis: int
    criticalFindings: int
    highFindings: int
    mediumFindings: int
    lowFindings: int


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DashboardStatsResponse:
    """
    Get dashboard statistics for the current user's organization.

    Returns counts for:
    - Total vendors
    - Total documents
    - Documents pending analysis (pending or processing status)
    - Documents with completed analysis (processed status)
    - Findings by severity (critical, high, medium, low)
    """
    org_id = current_user.organization_id

    # Count total vendors
    vendor_count_result = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.organization_id == org_id)
    )
    total_vendors = vendor_count_result.scalar() or 0

    # Count total documents
    doc_count_result = await db.execute(
        select(func.count(Document.id)).where(Document.organization_id == org_id)
    )
    total_documents = doc_count_result.scalar() or 0

    # Count documents pending analysis (pending or processing)
    pending_result = await db.execute(
        select(func.count(Document.id)).where(
            Document.organization_id == org_id,
            Document.status.in_([
                DocumentStatus.PENDING.value,
                DocumentStatus.PROCESSING.value,
            ]),
        )
    )
    pending_analysis = pending_result.scalar() or 0

    # Count documents with completed analysis
    completed_result = await db.execute(
        select(func.count(Document.id)).where(
            Document.organization_id == org_id,
            Document.status == DocumentStatus.PROCESSED.value,
        )
    )
    completed_analysis = completed_result.scalar() or 0

    # Count findings by severity
    critical_result = await db.execute(
        select(func.count(Finding.id)).where(
            Finding.organization_id == org_id,
            Finding.severity == FindingSeverity.CRITICAL.value,
        )
    )
    critical_findings = critical_result.scalar() or 0

    high_result = await db.execute(
        select(func.count(Finding.id)).where(
            Finding.organization_id == org_id,
            Finding.severity == FindingSeverity.HIGH.value,
        )
    )
    high_findings = high_result.scalar() or 0

    medium_result = await db.execute(
        select(func.count(Finding.id)).where(
            Finding.organization_id == org_id,
            Finding.severity == FindingSeverity.MEDIUM.value,
        )
    )
    medium_findings = medium_result.scalar() or 0

    low_result = await db.execute(
        select(func.count(Finding.id)).where(
            Finding.organization_id == org_id,
            Finding.severity == FindingSeverity.LOW.value,
        )
    )
    low_findings = low_result.scalar() or 0

    return DashboardStatsResponse(
        totalVendors=total_vendors,
        totalDocuments=total_documents,
        pendingAnalysis=pending_analysis,
        completedAnalysis=completed_analysis,
        criticalFindings=critical_findings,
        highFindings=high_findings,
        mediumFindings=medium_findings,
        lowFindings=low_findings,
    )
