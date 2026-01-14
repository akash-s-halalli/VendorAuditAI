"""AI Governance Playbook service layer for business logic."""

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.playbook import (
    AIPlaybook,
    ApprovalStatus,
    PlaybookApproval,
    PlaybookProgress,
    PlaybookProgressStatus,
    PlaybookStep,
)
from app.models.vendor import Vendor
from app.schemas.playbook import (
    PlaybookCreate,
    PlaybookProgressCreate,
    PlaybookStepCreate,
    PlaybookUpdate,
    StepCompletionData,
)


# ============================================================================
# Playbook CRUD Operations
# ============================================================================


async def get_playbook_by_id(
    db: AsyncSession,
    playbook_id: str,
    org_id: str,
    include_steps: bool = False,
) -> AIPlaybook | None:
    """Get a single playbook by ID with organization isolation."""
    query = select(AIPlaybook).where(
        AIPlaybook.id == playbook_id,
        AIPlaybook.organization_id == org_id,
    )

    if include_steps:
        query = query.options(selectinload(AIPlaybook.steps))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_playbooks(
    db: AsyncSession,
    org_id: str,
    skip: int = 0,
    limit: int = 20,
    phase: str | None = None,
    department: str | None = None,
    target_audience: str | None = None,
    is_active: bool | None = True,
) -> tuple[list[AIPlaybook], int]:
    """List playbooks with pagination and filtering."""
    query = select(AIPlaybook).where(AIPlaybook.organization_id == org_id)

    if phase:
        query = query.where(AIPlaybook.phase == phase)
    if department:
        query = query.where(
            (AIPlaybook.department == department) | (AIPlaybook.department == "all")
        )
    if target_audience:
        query = query.where(
            (AIPlaybook.target_audience == target_audience)
            | (AIPlaybook.target_audience == "all")
        )
    if is_active is not None:
        query = query.where(AIPlaybook.is_active == is_active)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(AIPlaybook.created_at.desc())
    query = query.options(selectinload(AIPlaybook.steps))

    result = await db.execute(query)
    playbooks = list(result.scalars().all())

    return playbooks, total


async def create_playbook(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    playbook_data: PlaybookCreate,
) -> AIPlaybook:
    """Create a new playbook with optional steps."""
    playbook = AIPlaybook(
        organization_id=org_id,
        created_by_id=user_id,
        name=playbook_data.name,
        description=playbook_data.description,
        phase=playbook_data.phase,
        target_audience=playbook_data.target_audience,
        department=playbook_data.department,
        estimated_duration_minutes=playbook_data.estimated_duration_minutes,
        is_active=playbook_data.is_active,
        icon=playbook_data.icon,
        color=playbook_data.color,
    )
    db.add(playbook)
    await db.flush()

    # Create steps if provided
    if playbook_data.steps:
        for step_data in playbook_data.steps:
            step = create_playbook_step_object(playbook.id, step_data)
            db.add(step)

    await db.commit()
    await db.refresh(playbook)
    return playbook


async def update_playbook(
    db: AsyncSession,
    playbook: AIPlaybook,
    playbook_data: PlaybookUpdate,
) -> AIPlaybook:
    """Update an existing playbook."""
    update_data = playbook_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(playbook, field, value)

    await db.commit()
    await db.refresh(playbook)
    return playbook


async def delete_playbook(db: AsyncSession, playbook: AIPlaybook) -> None:
    """Delete a playbook and all its steps."""
    await db.delete(playbook)
    await db.commit()


# ============================================================================
# Playbook Step Operations
# ============================================================================


def create_playbook_step_object(
    playbook_id: str,
    step_data: PlaybookStepCreate,
) -> PlaybookStep:
    """Create a PlaybookStep object (not saved to DB yet)."""
    return PlaybookStep(
        playbook_id=playbook_id,
        step_number=step_data.step_number,
        title=step_data.title,
        description=step_data.description,
        instructions=step_data.instructions,
        checklist=json.dumps(
            [item.model_dump() for item in step_data.checklist]
        ) if step_data.checklist else None,
        required_approvals=json.dumps(step_data.required_approvals) if step_data.required_approvals else None,
        estimated_time_minutes=step_data.estimated_time_minutes,
        resources=json.dumps(
            [r.model_dump() for r in step_data.resources]
        ) if step_data.resources else None,
        tips=step_data.tips,
        warning=step_data.warning,
    )


async def add_step_to_playbook(
    db: AsyncSession,
    playbook: AIPlaybook,
    step_data: PlaybookStepCreate,
) -> PlaybookStep:
    """Add a new step to an existing playbook."""
    step = create_playbook_step_object(playbook.id, step_data)
    db.add(step)
    await db.commit()
    await db.refresh(step)
    return step


async def get_playbook_step(
    db: AsyncSession,
    step_id: str,
) -> PlaybookStep | None:
    """Get a playbook step by ID."""
    result = await db.execute(
        select(PlaybookStep).where(PlaybookStep.id == step_id)
    )
    return result.scalar_one_or_none()


# ============================================================================
# Playbook Progress Operations
# ============================================================================


async def get_progress_by_id(
    db: AsyncSession,
    progress_id: str,
    org_id: str,
) -> PlaybookProgress | None:
    """Get playbook progress by ID."""
    result = await db.execute(
        select(PlaybookProgress)
        .where(
            PlaybookProgress.id == progress_id,
            PlaybookProgress.organization_id == org_id,
        )
        .options(
            selectinload(PlaybookProgress.playbook).selectinload(AIPlaybook.steps),
            selectinload(PlaybookProgress.vendor),
        )
    )
    return result.scalar_one_or_none()


async def get_user_progress(
    db: AsyncSession,
    user_id: str,
    org_id: str,
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[PlaybookProgress], int]:
    """Get playbook progress records for a user."""
    query = select(PlaybookProgress).where(
        PlaybookProgress.user_id == user_id,
        PlaybookProgress.organization_id == org_id,
    )

    if status:
        query = query.where(PlaybookProgress.status == status)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch with pagination - include playbook.steps for total_steps calculation
    query = (
        query.options(
            selectinload(PlaybookProgress.playbook).selectinload(AIPlaybook.steps),
            selectinload(PlaybookProgress.vendor),
        )
        .offset(skip)
        .limit(limit)
        .order_by(PlaybookProgress.updated_at.desc())
    )

    result = await db.execute(query)
    progress_list = list(result.scalars().all())

    return progress_list, total


async def start_playbook(
    db: AsyncSession,
    user_id: str,
    org_id: str,
    progress_data: PlaybookProgressCreate,
) -> PlaybookProgress:
    """Start a playbook for a user/vendor combination."""
    # Check if already in progress
    existing = await db.execute(
        select(PlaybookProgress).where(
            PlaybookProgress.user_id == user_id,
            PlaybookProgress.playbook_id == progress_data.playbook_id,
            PlaybookProgress.vendor_id == progress_data.vendor_id,
            PlaybookProgress.status.in_([
                PlaybookProgressStatus.IN_PROGRESS.value,
                PlaybookProgressStatus.PENDING_APPROVAL.value,
            ]),
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Playbook already in progress for this vendor")

    progress = PlaybookProgress(
        organization_id=org_id,
        user_id=user_id,
        playbook_id=progress_data.playbook_id,
        vendor_id=progress_data.vendor_id,
        current_step=1,
        status=PlaybookProgressStatus.IN_PROGRESS.value,
        started_at=datetime.now(timezone.utc),
        step_completions=json.dumps({}),
        progress_percentage=0.0,
    )
    db.add(progress)
    await db.commit()
    await db.refresh(progress)
    return progress


async def complete_step(
    db: AsyncSession,
    progress: PlaybookProgress,
    step_id: str,
    completion_data: StepCompletionData,
) -> PlaybookProgress:
    """Mark a step as complete and advance progress."""
    # Parse existing completions
    completions: dict[str, Any] = {}
    if progress.step_completions:
        if isinstance(progress.step_completions, str):
            completions = json.loads(progress.step_completions)
        else:
            completions = progress.step_completions

    # Add this step's completion
    completions[step_id] = {
        "completed": True,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "notes": completion_data.notes,
        "checklist_status": completion_data.checklist_completions,
        "evidence_urls": completion_data.evidence_urls,
    }

    progress.step_completions = json.dumps(completions)

    # Get playbook to determine total steps
    playbook = await get_playbook_by_id(
        db, progress.playbook_id, progress.organization_id, include_steps=True
    )
    if playbook:
        total_steps = len(playbook.steps)
        completed_steps = len(completions)
        progress.progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0

        # Advance to next step
        if progress.current_step < total_steps:
            progress.current_step += 1
        elif completed_steps >= total_steps:
            progress.status = PlaybookProgressStatus.COMPLETED.value
            progress.completed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(progress)
    return progress


async def abandon_playbook(
    db: AsyncSession,
    progress: PlaybookProgress,
) -> PlaybookProgress:
    """Mark a playbook as abandoned."""
    progress.status = PlaybookProgressStatus.ABANDONED.value
    await db.commit()
    await db.refresh(progress)
    return progress


# ============================================================================
# Approval Operations
# ============================================================================


async def get_pending_approvals(
    db: AsyncSession,
    approver_id: str,
    org_id: str,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[PlaybookApproval], int]:
    """Get pending approvals for an approver."""
    query = (
        select(PlaybookApproval)
        .join(PlaybookProgress)
        .where(
            PlaybookProgress.organization_id == org_id,
            PlaybookApproval.status == ApprovalStatus.PENDING.value,
        )
    )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch
    query = (
        query.options(
            selectinload(PlaybookApproval.step),
            selectinload(PlaybookApproval.progress),
        )
        .offset(skip)
        .limit(limit)
        .order_by(PlaybookApproval.requested_at.desc())
    )

    result = await db.execute(query)
    approvals = list(result.scalars().all())

    return approvals, total


async def request_approval(
    db: AsyncSession,
    progress: PlaybookProgress,
    step_id: str,
    requested_by_id: str,
    required_role: str | None = None,
) -> PlaybookApproval:
    """Create an approval request for a step."""
    approval = PlaybookApproval(
        progress_id=progress.id,
        step_id=step_id,
        requested_by_id=requested_by_id,
        required_role=required_role,
        status=ApprovalStatus.PENDING.value,
        requested_at=datetime.now(timezone.utc),
    )
    db.add(approval)

    # Update progress status
    progress.status = PlaybookProgressStatus.PENDING_APPROVAL.value

    await db.commit()
    await db.refresh(approval)
    return approval


async def respond_to_approval(
    db: AsyncSession,
    approval: PlaybookApproval,
    approver_id: str,
    status: str,
    comments: str | None = None,
) -> PlaybookApproval:
    """Respond to an approval request."""
    approval.approver_id = approver_id
    approval.status = status
    approval.comments = comments
    approval.responded_at = datetime.now(timezone.utc)

    # If approved, update progress status back to in_progress
    if status == ApprovalStatus.APPROVED.value:
        progress = await get_progress_by_id(
            db, approval.progress_id, approval.progress.organization_id
        )
        if progress:
            progress.status = PlaybookProgressStatus.IN_PROGRESS.value

    await db.commit()
    await db.refresh(approval)
    return approval


async def get_approval_by_id(
    db: AsyncSession,
    approval_id: str,
) -> PlaybookApproval | None:
    """Get an approval by ID."""
    result = await db.execute(
        select(PlaybookApproval)
        .where(PlaybookApproval.id == approval_id)
        .options(
            selectinload(PlaybookApproval.progress),
            selectinload(PlaybookApproval.step),
        )
    )
    return result.scalar_one_or_none()


# ============================================================================
# Dashboard / Stats
# ============================================================================


async def get_playbook_stats(
    db: AsyncSession,
    org_id: str,
) -> dict[str, Any]:
    """Get playbook statistics for an organization."""
    # Total playbooks
    total_playbooks_result = await db.execute(
        select(func.count()).where(AIPlaybook.organization_id == org_id)
    )
    total_playbooks = total_playbooks_result.scalar() or 0

    # Active progress
    active_progress_result = await db.execute(
        select(func.count()).where(
            PlaybookProgress.organization_id == org_id,
            PlaybookProgress.status == PlaybookProgressStatus.IN_PROGRESS.value,
        )
    )
    active_progress = active_progress_result.scalar() or 0

    # Completed this month
    start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    completed_this_month_result = await db.execute(
        select(func.count()).where(
            PlaybookProgress.organization_id == org_id,
            PlaybookProgress.status == PlaybookProgressStatus.COMPLETED.value,
            PlaybookProgress.completed_at >= start_of_month,
        )
    )
    completed_this_month = completed_this_month_result.scalar() or 0

    # Pending approvals
    pending_approvals_result = await db.execute(
        select(func.count())
        .select_from(PlaybookApproval)
        .join(PlaybookProgress)
        .where(
            PlaybookProgress.organization_id == org_id,
            PlaybookApproval.status == ApprovalStatus.PENDING.value,
        )
    )
    pending_approvals = pending_approvals_result.scalar() or 0

    return {
        "total_playbooks": total_playbooks,
        "active_progress": active_progress,
        "completed_this_month": completed_this_month,
        "pending_approvals": pending_approvals,
    }
