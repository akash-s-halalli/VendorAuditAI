"""Remediation workflow service for managing remediation tasks."""

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.remediation import (
    RemediationAuditLog,
    RemediationComment,
    RemediationPriority,
    RemediationStatus,
    RemediationTask,
    SLAPolicy,
    VALID_TRANSITIONS,
)
from app.schemas.remediation import (
    RemediationCommentCreate,
    RemediationDashboardStats,
    RemediationTaskCreate,
    RemediationTaskUpdate,
    RemediationTransition,
    SLAPolicyCreate,
)


class RemediationService:
    """Service for managing remediation workflow."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(
        self,
        task_data: RemediationTaskCreate,
        organization_id: str,
        created_by_id: str,
    ) -> RemediationTask:
        """Create a new remediation task from a finding."""
        # Get SLA policy for organization
        sla_policy = await self.get_default_sla_policy(organization_id)

        # Calculate due date based on priority and SLA
        priority = RemediationPriority(task_data.priority)
        sla_days = task_data.sla_days
        if sla_days is None and sla_policy:
            sla_days = sla_policy.get_sla_days(priority)

        due_date = task_data.due_date
        if due_date is None and sla_days:
            due_date = datetime.now(timezone.utc) + timedelta(days=sla_days)

        # Create the task
        task = RemediationTask(
            organization_id=organization_id,
            finding_id=task_data.finding_id,
            vendor_id=task_data.vendor_id,
            assignee_id=task_data.assignee_id,
            created_by_id=created_by_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            status=RemediationStatus.DRAFT.value,
            due_date=due_date,
            sla_days=sla_days,
        )

        self.db.add(task)
        await self.db.flush()

        # Create audit log for creation
        await self._create_audit_log(
            task_id=task.id,
            user_id=created_by_id,
            action="created",
            notes=f"Task created from finding",
        )

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task(
        self, task_id: str, organization_id: str, include_details: bool = False
    ) -> RemediationTask | None:
        """Get a remediation task by ID."""
        query = select(RemediationTask).where(
            and_(
                RemediationTask.id == task_id,
                RemediationTask.organization_id == organization_id,
            )
        )

        if include_details:
            query = query.options(
                selectinload(RemediationTask.audit_logs),
                selectinload(RemediationTask.comments),
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_tasks(
        self,
        organization_id: str,
        status: str | None = None,
        priority: str | None = None,
        assignee_id: str | None = None,
        vendor_id: str | None = None,
        is_overdue: bool | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[RemediationTask], int]:
        """List remediation tasks with filters."""
        query = select(RemediationTask).where(
            RemediationTask.organization_id == organization_id
        )

        # Apply filters
        if status:
            query = query.where(RemediationTask.status == status)
        if priority:
            query = query.where(RemediationTask.priority == priority)
        if assignee_id:
            query = query.where(RemediationTask.assignee_id == assignee_id)
        if vendor_id:
            query = query.where(RemediationTask.vendor_id == vendor_id)
        if is_overdue is True:
            now = datetime.now(timezone.utc)
            query = query.where(
                and_(
                    RemediationTask.due_date < now,
                    RemediationTask.status.notin_(
                        [
                            RemediationStatus.CLOSED.value,
                            RemediationStatus.VERIFIED.value,
                            RemediationStatus.EXCEPTION_APPROVED.value,
                        ]
                    ),
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.order_by(RemediationTask.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        tasks = list(result.scalars().all())

        return tasks, total

    async def update_task(
        self,
        task_id: str,
        organization_id: str,
        update_data: RemediationTaskUpdate,
        user_id: str,
    ) -> RemediationTask | None:
        """Update a remediation task."""
        task = await self.get_task(task_id, organization_id)
        if not task:
            return None

        # Track changes for audit log
        changes = []
        update_dict = update_data.model_dump(exclude_unset=True)

        for field, new_value in update_dict.items():
            old_value = getattr(task, field)
            if old_value != new_value:
                changes.append((field, str(old_value), str(new_value)))
                setattr(task, field, new_value)

        # Create audit logs for each change
        for field, old_val, new_val in changes:
            await self._create_audit_log(
                task_id=task.id,
                user_id=user_id,
                action="updated",
                field_changed=field,
                old_value=old_val,
                new_value=new_val,
            )

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def transition_task(
        self,
        task_id: str,
        organization_id: str,
        transition: RemediationTransition,
        user_id: str,
    ) -> RemediationTask | None:
        """Transition task to a new status."""
        task = await self.get_task(task_id, organization_id)
        if not task:
            return None

        # Validate transition
        new_status = RemediationStatus(transition.new_status)
        if not task.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition from {task.status} to {transition.new_status}"
            )

        old_status = task.status
        task.status = new_status.value

        # Handle special status transitions
        if new_status == RemediationStatus.VERIFIED:
            task.verified_at = datetime.now(timezone.utc)
            task.verified_by_id = user_id

        if new_status == RemediationStatus.CLOSED:
            task.resolved_at = datetime.now(timezone.utc)

        if new_status == RemediationStatus.EXCEPTION_REQUESTED:
            task.exception_reason = transition.exception_reason

        if new_status == RemediationStatus.EXCEPTION_APPROVED:
            task.exception_approved_by_id = user_id
            task.exception_approved_at = datetime.now(timezone.utc)

        # Create audit log
        await self._create_audit_log(
            task_id=task.id,
            user_id=user_id,
            action="status_change",
            field_changed="status",
            old_value=old_status,
            new_value=new_status.value,
            notes=transition.notes,
        )

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def add_comment(
        self,
        task_id: str,
        organization_id: str,
        comment_data: RemediationCommentCreate,
        user_id: str,
    ) -> RemediationComment | None:
        """Add a comment to a task."""
        task = await self.get_task(task_id, organization_id)
        if not task:
            return None

        comment = RemediationComment(
            task_id=task_id,
            user_id=user_id,
            content=comment_data.content,
            is_internal=comment_data.is_internal,
        )

        self.db.add(comment)

        # Create audit log
        await self._create_audit_log(
            task_id=task_id,
            user_id=user_id,
            action="comment_added",
            notes=f"Comment added (internal={comment_data.is_internal})",
        )

        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def get_comments(
        self, task_id: str, organization_id: str
    ) -> list[RemediationComment]:
        """Get all comments for a task."""
        task = await self.get_task(task_id, organization_id)
        if not task:
            return []

        query = (
            select(RemediationComment)
            .where(RemediationComment.task_id == task_id)
            .order_by(RemediationComment.created_at.desc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_audit_logs(
        self, task_id: str, organization_id: str
    ) -> list[RemediationAuditLog]:
        """Get audit trail for a task."""
        task = await self.get_task(task_id, organization_id)
        if not task:
            return []

        query = (
            select(RemediationAuditLog)
            .where(RemediationAuditLog.task_id == task_id)
            .order_by(RemediationAuditLog.created_at.desc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_dashboard_stats(
        self, organization_id: str
    ) -> RemediationDashboardStats:
        """Get dashboard statistics for remediation tasks."""
        # Total tasks
        total_query = select(func.count()).where(
            RemediationTask.organization_id == organization_id
        )
        total_result = await self.db.execute(total_query)
        total_tasks = total_result.scalar() or 0

        # Open tasks (not closed or verified)
        open_statuses = [
            RemediationStatus.DRAFT.value,
            RemediationStatus.PENDING_ASSIGNMENT.value,
            RemediationStatus.ASSIGNED.value,
            RemediationStatus.IN_PROGRESS.value,
            RemediationStatus.PENDING_REVIEW.value,
            RemediationStatus.PENDING_VERIFICATION.value,
            RemediationStatus.EXCEPTION_REQUESTED.value,
            RemediationStatus.REOPENED.value,
        ]
        open_query = select(func.count()).where(
            and_(
                RemediationTask.organization_id == organization_id,
                RemediationTask.status.in_(open_statuses),
            )
        )
        open_result = await self.db.execute(open_query)
        open_tasks = open_result.scalar() or 0

        # Overdue tasks
        now = datetime.now(timezone.utc)
        overdue_query = select(func.count()).where(
            and_(
                RemediationTask.organization_id == organization_id,
                RemediationTask.due_date < now,
                RemediationTask.status.in_(open_statuses),
            )
        )
        overdue_result = await self.db.execute(overdue_query)
        overdue_tasks = overdue_result.scalar() or 0

        # SLA breached
        breached_query = select(func.count()).where(
            and_(
                RemediationTask.organization_id == organization_id,
                RemediationTask.sla_breached == True,  # noqa: E712
            )
        )
        breached_result = await self.db.execute(breached_query)
        sla_breached = breached_result.scalar() or 0

        # By status
        status_query = select(
            RemediationTask.status, func.count()
        ).where(
            RemediationTask.organization_id == organization_id
        ).group_by(RemediationTask.status)
        status_result = await self.db.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result.all()}

        # By priority
        priority_query = select(
            RemediationTask.priority, func.count()
        ).where(
            RemediationTask.organization_id == organization_id
        ).group_by(RemediationTask.priority)
        priority_result = await self.db.execute(priority_query)
        by_priority = {row[0]: row[1] for row in priority_result.all()}

        return RemediationDashboardStats(
            total_tasks=total_tasks,
            open_tasks=open_tasks,
            overdue_tasks=overdue_tasks,
            sla_breached=sla_breached,
            by_status=by_status,
            by_priority=by_priority,
        )

    async def get_default_sla_policy(
        self, organization_id: str
    ) -> SLAPolicy | None:
        """Get the default SLA policy for an organization."""
        query = select(SLAPolicy).where(
            and_(
                SLAPolicy.organization_id == organization_id,
                SLAPolicy.is_default == True,  # noqa: E712
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_sla_policy(
        self,
        policy_data: SLAPolicyCreate,
        organization_id: str,
    ) -> SLAPolicy:
        """Create an SLA policy for an organization."""
        # If this is default, unset other defaults
        if policy_data.is_default:
            await self.db.execute(
                select(SLAPolicy).where(
                    and_(
                        SLAPolicy.organization_id == organization_id,
                        SLAPolicy.is_default == True,  # noqa: E712
                    )
                )
            )
            # Update existing defaults to non-default
            existing = await self.db.execute(
                select(SLAPolicy).where(
                    and_(
                        SLAPolicy.organization_id == organization_id,
                        SLAPolicy.is_default == True,  # noqa: E712
                    )
                )
            )
            for policy in existing.scalars().all():
                policy.is_default = False

        policy = SLAPolicy(
            organization_id=organization_id,
            name=policy_data.name,
            is_default=policy_data.is_default,
            critical_sla_days=policy_data.critical_sla_days,
            high_sla_days=policy_data.high_sla_days,
            medium_sla_days=policy_data.medium_sla_days,
            low_sla_days=policy_data.low_sla_days,
        )

        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def check_sla_breaches(self, organization_id: str) -> int:
        """Check and mark SLA breaches for all overdue tasks."""
        now = datetime.now(timezone.utc)

        # Find tasks that are overdue but not yet marked as breached
        query = select(RemediationTask).where(
            and_(
                RemediationTask.organization_id == organization_id,
                RemediationTask.due_date < now,
                RemediationTask.sla_breached == False,  # noqa: E712
                RemediationTask.status.notin_(
                    [
                        RemediationStatus.CLOSED.value,
                        RemediationStatus.VERIFIED.value,
                        RemediationStatus.EXCEPTION_APPROVED.value,
                    ]
                ),
            )
        )

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        breach_count = 0
        for task in tasks:
            task.sla_breached = True
            task.sla_breached_at = now
            breach_count += 1

            # Create audit log
            await self._create_audit_log(
                task_id=task.id,
                user_id=None,
                action="sla_breach",
                notes="SLA breached - task is overdue",
            )

        if breach_count > 0:
            await self.db.commit()

        return breach_count

    async def _create_audit_log(
        self,
        task_id: str,
        user_id: str | None,
        action: str,
        field_changed: str | None = None,
        old_value: str | None = None,
        new_value: str | None = None,
        notes: str | None = None,
    ) -> RemediationAuditLog:
        """Create an audit log entry."""
        log = RemediationAuditLog(
            task_id=task_id,
            user_id=user_id,
            action=action,
            field_changed=field_changed,
            old_value=old_value,
            new_value=new_value,
            notes=notes,
        )
        self.db.add(log)
        await self.db.flush()
        return log


def get_remediation_service(db: AsyncSession) -> RemediationService:
    """Factory function to create remediation service."""
    return RemediationService(db)
