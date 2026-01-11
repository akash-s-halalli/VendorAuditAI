"""Audit logging service for SOC 2 compliance."""

import csv
import io
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditAction, AuditLog


class AuditService:
    """Service for managing system-wide audit logs.

    Provides comprehensive audit trail functionality for SOC 2 compliance,
    including logging, querying, and exporting audit events.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        organization_id: str,
        action: str | AuditAction,
        resource_type: str,
        user_id: str | None = None,
        resource_id: str | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: str | None = None,
    ) -> AuditLog:
        """Log an audit action.

        Args:
            organization_id: The organization ID for multi-tenant isolation
            action: The action type (CREATE, READ, UPDATE, DELETE, LOGIN, etc.)
            resource_type: The type of resource being acted upon
            user_id: The ID of the user performing the action (None for system actions)
            resource_id: The ID of the specific resource
            old_values: The previous state of the resource (for updates/deletes)
            new_values: The new state of the resource (for creates/updates)
            ip_address: The IP address of the request
            user_agent: The user agent string from the request
            details: Additional details about the action

        Returns:
            The created AuditLog entry
        """
        # Convert AuditAction enum to string if needed
        action_str = action.value if isinstance(action, AuditAction) else action

        # Sanitize values - remove sensitive fields
        sanitized_old = self._sanitize_values(old_values) if old_values else None
        sanitized_new = self._sanitize_values(new_values) if new_values else None

        log = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action_str,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=sanitized_old,
            new_values=sanitized_new,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )

        self.db.add(log)
        await self.db.flush()
        return log

    def _sanitize_values(self, values: dict[str, Any]) -> dict[str, Any]:
        """Remove sensitive fields from audit log values.

        Args:
            values: The dictionary of values to sanitize

        Returns:
            A new dictionary with sensitive fields masked
        """
        sensitive_fields = {
            "password",
            "password_hash",
            "secret",
            "token",
            "api_key",
            "mfa_secret",
            "refresh_token",
            "access_token",
            "private_key",
            "credentials",
        }

        sanitized = {}
        for key, value in values.items():
            if key.lower() in sensitive_fields:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_values(value)
            else:
                sanitized[key] = value

        return sanitized

    async def get_logs(
        self,
        organization_id: str,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        user_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """Get audit logs with filtering and pagination.

        Args:
            organization_id: The organization ID for multi-tenant isolation
            action: Filter by action type
            resource_type: Filter by resource type
            resource_id: Filter by specific resource ID
            user_id: Filter by user ID
            start_date: Filter logs after this date
            end_date: Filter logs before this date
            page: Page number (1-indexed)
            limit: Number of items per page

        Returns:
            Tuple of (list of audit logs, total count)
        """
        query = select(AuditLog).where(
            AuditLog.organization_id == organization_id
        )

        # Apply filters
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.where(AuditLog.resource_id == resource_id)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(AuditLog.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def get_logs_for_resource(
        self,
        organization_id: str,
        resource_type: str,
        resource_id: str,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """Get audit logs for a specific resource.

        Args:
            organization_id: The organization ID
            resource_type: The type of resource
            resource_id: The ID of the resource
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (list of audit logs, total count)
        """
        return await self.get_logs(
            organization_id=organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            page=page,
            limit=limit,
        )

    async def export_logs_csv(
        self,
        organization_id: str,
        action: str | None = None,
        resource_type: str | None = None,
        user_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        max_records: int = 10000,
    ) -> str:
        """Export audit logs as CSV.

        Args:
            organization_id: The organization ID
            action: Filter by action type
            resource_type: Filter by resource type
            user_id: Filter by user ID
            start_date: Filter logs after this date
            end_date: Filter logs before this date
            max_records: Maximum number of records to export

        Returns:
            CSV string of audit logs
        """
        query = select(AuditLog).where(
            AuditLog.organization_id == organization_id
        )

        # Apply filters
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)

        # Order and limit
        query = query.order_by(AuditLog.created_at.desc()).limit(max_records)

        result = await self.db.execute(query)
        logs = result.scalars().all()

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "ID",
            "Timestamp",
            "User ID",
            "Action",
            "Resource Type",
            "Resource ID",
            "IP Address",
            "User Agent",
            "Details",
            "Old Values",
            "New Values",
        ])

        # Write rows
        for log in logs:
            writer.writerow([
                log.id,
                log.created_at.isoformat() if log.created_at else "",
                log.user_id or "",
                log.action,
                log.resource_type,
                log.resource_id or "",
                log.ip_address or "",
                log.user_agent or "",
                log.details or "",
                str(log.old_values) if log.old_values else "",
                str(log.new_values) if log.new_values else "",
            ])

        return output.getvalue()

    async def get_recent_activity(
        self,
        organization_id: str,
        user_id: str | None = None,
        limit: int = 20,
    ) -> list[AuditLog]:
        """Get recent activity for an organization or user.

        Args:
            organization_id: The organization ID
            user_id: Optional user ID to filter by
            limit: Maximum number of records

        Returns:
            List of recent audit logs
        """
        query = select(AuditLog).where(
            AuditLog.organization_id == organization_id
        )

        if user_id:
            query = query.where(AuditLog.user_id == user_id)

        query = query.order_by(AuditLog.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_login_history(
        self,
        organization_id: str,
        user_id: str | None = None,
        start_date: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get login history for compliance reporting.

        Args:
            organization_id: The organization ID
            user_id: Optional user ID to filter by
            start_date: Start date for history
            limit: Maximum number of records

        Returns:
            List of login-related audit logs
        """
        query = select(AuditLog).where(
            and_(
                AuditLog.organization_id == organization_id,
                AuditLog.action.in_([
                    AuditAction.LOGIN.value,
                    AuditAction.LOGOUT.value,
                    AuditAction.LOGIN_FAILED.value,
                ]),
            )
        )

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)

        query = query.order_by(AuditLog.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())


def get_audit_service(db: AsyncSession) -> AuditService:
    """Factory function to create audit service."""
    return AuditService(db)
