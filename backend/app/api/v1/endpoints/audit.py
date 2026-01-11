"""Audit logging API endpoints for SOC 2 compliance."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_current_admin_user
from app.db import get_db
from app.models import User
from app.schemas.audit import (
    AuditLogListResponse,
    AuditLogResponse,
)
from app.services.audit import get_audit_service

router = APIRouter(tags=["Audit"])


@router.get("/logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    action: str | None = Query(None, description="Filter by action type"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    resource_id: str | None = Query(None, description="Filter by resource ID"),
    user_id: str | None = Query(None, description="Filter by user ID"),
    start_date: datetime | None = Query(None, description="Filter logs after this date"),
    end_date: datetime | None = Query(None, description="Filter logs before this date"),
) -> AuditLogListResponse:
    """
    List audit logs for the organization.

    Requires admin privileges. Supports filtering by action, resource type,
    resource ID, user ID, and date range.
    """
    service = get_audit_service(db)
    logs, total = await service.get_logs(
        organization_id=current_user.organization_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit,
    )

    return AuditLogListResponse(
        data=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/logs/export")
async def export_audit_logs(
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    action: str | None = Query(None, description="Filter by action type"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    user_id: str | None = Query(None, description="Filter by user ID"),
    start_date: datetime | None = Query(None, description="Filter logs after this date"),
    end_date: datetime | None = Query(None, description="Filter logs before this date"),
    max_records: int = Query(10000, ge=1, le=100000, description="Maximum records to export"),
) -> Response:
    """
    Export audit logs as CSV.

    Requires admin privileges. Supports filtering and limits export
    to max_records for performance.
    """
    service = get_audit_service(db)

    # Log the export action
    await service.log_action(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="EXPORT",
        resource_type="audit_log",
        details=f"Exported audit logs with filters: action={action}, resource_type={resource_type}",
    )

    csv_content = await service.export_logs_csv(
        organization_id=current_user.organization_id,
        action=action,
        resource_type=resource_type,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        max_records=max_records,
    )

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_logs_{timestamp}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/logs/{resource_type}/{resource_id}", response_model=AuditLogListResponse)
async def get_resource_audit_logs(
    resource_type: str,
    resource_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> AuditLogListResponse:
    """
    Get audit logs for a specific resource.

    Returns the audit trail for the specified resource type and ID.
    Available to all authenticated users for resources they have access to.
    """
    service = get_audit_service(db)
    logs, total = await service.get_logs_for_resource(
        organization_id=current_user.organization_id,
        resource_type=resource_type,
        resource_id=resource_id,
        page=page,
        limit=limit,
    )

    return AuditLogListResponse(
        data=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/logs/recent", response_model=list[AuditLogResponse])
async def get_recent_activity(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100, description="Number of recent logs"),
    user_id: str | None = Query(None, description="Filter by user ID"),
) -> list[AuditLogResponse]:
    """
    Get recent activity for the organization.

    Returns the most recent audit log entries. Non-admins can only
    see their own activity unless filtering is applied.
    """
    service = get_audit_service(db)

    # Non-admins can only see their own activity
    filter_user_id = user_id
    if not current_user.is_admin:
        filter_user_id = current_user.id

    logs = await service.get_recent_activity(
        organization_id=current_user.organization_id,
        user_id=filter_user_id,
        limit=limit,
    )

    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get("/logs/login-history", response_model=list[AuditLogResponse])
async def get_login_history(
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: str | None = Query(None, description="Filter by user ID"),
    start_date: datetime | None = Query(None, description="Filter logs after this date"),
    limit: int = Query(100, ge=1, le=1000, description="Number of login records"),
) -> list[AuditLogResponse]:
    """
    Get login history for compliance reporting.

    Requires admin privileges. Returns login, logout, and failed login
    attempts for the organization.
    """
    service = get_audit_service(db)
    logs = await service.get_login_history(
        organization_id=current_user.organization_id,
        user_id=user_id,
        start_date=start_date,
        limit=limit,
    )

    return [AuditLogResponse.model_validate(log) for log in logs]
