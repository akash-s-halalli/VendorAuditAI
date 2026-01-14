"""AI Governance Playbook API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_current_admin_user
from app.db import get_db
from app.models import User
from app.schemas.playbook import (
    ApprovalRequestCreate,
    ApprovalResponseData,
    PlaybookApprovalListResponse,
    PlaybookApprovalResponse,
    PlaybookCreate,
    PlaybookDetailResponse,
    PlaybookListResponse,
    PlaybookProgressCreate,
    PlaybookProgressListResponse,
    PlaybookProgressResponse,
    PlaybookResponse,
    PlaybookStepCreate,
    PlaybookStepResponse,
    PlaybookUpdate,
    StepCompletionData,
)
from app.services import playbook as playbook_service

router = APIRouter(tags=["AI Governance Playbooks"])


# ============================================================================
# Playbook CRUD Endpoints
# ============================================================================


@router.get("/", response_model=PlaybookListResponse)
async def list_playbooks(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    phase: str | None = None,
    department: str | None = None,
    target_audience: str | None = None,
    is_active: bool | None = True,
) -> PlaybookListResponse:
    """List all available playbooks with optional filtering."""
    skip = (page - 1) * limit
    playbooks, total = await playbook_service.get_playbooks(
        db,
        org_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        phase=phase,
        department=department,
        target_audience=target_audience,
        is_active=is_active,
    )

    return PlaybookListResponse(
        data=[
            PlaybookResponse(
                id=p.id,
                organization_id=p.organization_id,
                name=p.name,
                description=p.description,
                phase=p.phase,
                target_audience=p.target_audience,
                department=p.department,
                version=p.version,
                is_active=p.is_active,
                is_default=p.is_default,
                estimated_duration_minutes=p.estimated_duration_minutes,
                icon=p.icon,
                color=p.color,
                created_at=p.created_at,
                updated_at=p.updated_at,
                total_steps=len(p.steps) if p.steps else 0,
            )
            for p in playbooks
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{playbook_id}", response_model=PlaybookDetailResponse)
async def get_playbook(
    playbook_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaybookDetailResponse:
    """Get a playbook with all its steps."""
    playbook = await playbook_service.get_playbook_by_id(
        db,
        playbook_id=playbook_id,
        org_id=current_user.organization_id,
        include_steps=True,
    )

    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook not found",
        )

    return PlaybookDetailResponse.model_validate(playbook)


@router.post("/", response_model=PlaybookResponse, status_code=status.HTTP_201_CREATED)
async def create_playbook(
    playbook_data: PlaybookCreate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaybookResponse:
    """Create a new playbook (admin only)."""
    playbook = await playbook_service.create_playbook(
        db,
        org_id=current_user.organization_id,
        user_id=current_user.id,
        playbook_data=playbook_data,
    )

    return PlaybookResponse.model_validate(playbook)


@router.put("/{playbook_id}", response_model=PlaybookResponse)
async def update_playbook(
    playbook_id: str,
    playbook_data: PlaybookUpdate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaybookResponse:
    """Update an existing playbook (admin only)."""
    playbook = await playbook_service.get_playbook_by_id(
        db,
        playbook_id=playbook_id,
        org_id=current_user.organization_id,
    )

    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook not found",
        )

    updated = await playbook_service.update_playbook(db, playbook, playbook_data)
    return PlaybookResponse.model_validate(updated)


@router.delete("/{playbook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playbook(
    playbook_id: str,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a playbook (admin only)."""
    playbook = await playbook_service.get_playbook_by_id(
        db,
        playbook_id=playbook_id,
        org_id=current_user.organization_id,
    )

    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook not found",
        )

    await playbook_service.delete_playbook(db, playbook)


# ============================================================================
# Playbook Step Endpoints
# ============================================================================


@router.post("/{playbook_id}/steps", response_model=PlaybookStepResponse, status_code=status.HTTP_201_CREATED)
async def add_playbook_step(
    playbook_id: str,
    step_data: PlaybookStepCreate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaybookStepResponse:
    """Add a step to a playbook (admin only)."""
    playbook = await playbook_service.get_playbook_by_id(
        db,
        playbook_id=playbook_id,
        org_id=current_user.organization_id,
    )

    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook not found",
        )

    step = await playbook_service.add_step_to_playbook(db, playbook, step_data)
    return PlaybookStepResponse.model_validate(step)


# ============================================================================
# Playbook Progress Endpoints
# ============================================================================


@router.post("/{playbook_id}/start", response_model=PlaybookProgressResponse, status_code=status.HTTP_201_CREATED)
async def start_playbook(
    playbook_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    vendor_id: str | None = None,
) -> PlaybookProgressResponse:
    """Start a playbook for a specific vendor."""
    # Verify playbook exists
    playbook = await playbook_service.get_playbook_by_id(
        db,
        playbook_id=playbook_id,
        org_id=current_user.organization_id,
        include_steps=True,
    )

    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook not found",
        )

    if not playbook.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Playbook is not active",
        )

    try:
        progress_data = PlaybookProgressCreate(
            playbook_id=playbook_id,
            vendor_id=vendor_id,
        )
        progress = await playbook_service.start_playbook(
            db,
            user_id=current_user.id,
            org_id=current_user.organization_id,
            progress_data=progress_data,
        )

        return PlaybookProgressResponse(
            id=progress.id,
            organization_id=progress.organization_id,
            user_id=progress.user_id,
            playbook_id=progress.playbook_id,
            vendor_id=progress.vendor_id,
            current_step=progress.current_step,
            status=progress.status,
            step_completions=None,
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            progress_percentage=progress.progress_percentage,
            created_at=progress.created_at,
            updated_at=progress.updated_at,
            playbook_name=playbook.name,
            vendor_name=None,
            total_steps=len(playbook.steps) if playbook.steps else 0,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/progress/", response_model=PlaybookProgressListResponse)
async def list_my_progress(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    progress_status: str | None = None,
) -> PlaybookProgressListResponse:
    """List current user's playbook progress."""
    skip = (page - 1) * limit
    progress_list, total = await playbook_service.get_user_progress(
        db,
        user_id=current_user.id,
        org_id=current_user.organization_id,
        status=progress_status,
        skip=skip,
        limit=limit,
    )

    return PlaybookProgressListResponse(
        data=[
            PlaybookProgressResponse(
                id=p.id,
                organization_id=p.organization_id,
                user_id=p.user_id,
                playbook_id=p.playbook_id,
                vendor_id=p.vendor_id,
                current_step=p.current_step,
                status=p.status,
                step_completions=None,
                started_at=p.started_at,
                completed_at=p.completed_at,
                progress_percentage=p.progress_percentage,
                created_at=p.created_at,
                updated_at=p.updated_at,
                playbook_name=p.playbook.name if p.playbook else None,
                vendor_name=p.vendor.name if p.vendor else None,
                total_steps=len(p.playbook.steps) if p.playbook and p.playbook.steps else 0,
            )
            for p in progress_list
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/progress/{progress_id}", response_model=PlaybookProgressResponse)
async def get_progress(
    progress_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaybookProgressResponse:
    """Get playbook progress by ID."""
    progress = await playbook_service.get_progress_by_id(
        db,
        progress_id=progress_id,
        org_id=current_user.organization_id,
    )

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )

    return PlaybookProgressResponse(
        id=progress.id,
        organization_id=progress.organization_id,
        user_id=progress.user_id,
        playbook_id=progress.playbook_id,
        vendor_id=progress.vendor_id,
        current_step=progress.current_step,
        status=progress.status,
        step_completions=progress.step_completions,
        started_at=progress.started_at,
        completed_at=progress.completed_at,
        progress_percentage=progress.progress_percentage,
        created_at=progress.created_at,
        updated_at=progress.updated_at,
        playbook_name=progress.playbook.name if progress.playbook else None,
        vendor_name=progress.vendor.name if progress.vendor else None,
        total_steps=len(progress.playbook.steps) if progress.playbook and progress.playbook.steps else 0,
    )


@router.post("/progress/{progress_id}/complete-step/{step_id}", response_model=PlaybookProgressResponse)
async def complete_step(
    progress_id: str,
    step_id: str,
    completion_data: StepCompletionData,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaybookProgressResponse:
    """Mark a step as complete."""
    progress = await playbook_service.get_progress_by_id(
        db,
        progress_id=progress_id,
        org_id=current_user.organization_id,
    )

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )

    if progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this progress",
        )

    updated = await playbook_service.complete_step(
        db, progress, step_id, completion_data
    )

    return PlaybookProgressResponse(
        id=updated.id,
        organization_id=updated.organization_id,
        user_id=updated.user_id,
        playbook_id=updated.playbook_id,
        vendor_id=updated.vendor_id,
        current_step=updated.current_step,
        status=updated.status,
        step_completions=updated.step_completions,
        started_at=updated.started_at,
        completed_at=updated.completed_at,
        progress_percentage=updated.progress_percentage,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        playbook_name=updated.playbook.name if updated.playbook else None,
        vendor_name=updated.vendor.name if updated.vendor else None,
        total_steps=len(updated.playbook.steps) if updated.playbook and updated.playbook.steps else 0,
    )


@router.post("/progress/{progress_id}/abandon", response_model=PlaybookProgressResponse)
async def abandon_playbook(
    progress_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaybookProgressResponse:
    """Mark a playbook as abandoned."""
    progress = await playbook_service.get_progress_by_id(
        db,
        progress_id=progress_id,
        org_id=current_user.organization_id,
    )

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )

    if progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this progress",
        )

    updated = await playbook_service.abandon_playbook(db, progress)
    return PlaybookProgressResponse.model_validate(updated)


# ============================================================================
# Approval Endpoints
# ============================================================================


@router.get("/approvals/pending", response_model=PlaybookApprovalListResponse)
async def list_pending_approvals(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> PlaybookApprovalListResponse:
    """List approvals pending for current user."""
    skip = (page - 1) * limit
    approvals, total = await playbook_service.get_pending_approvals(
        db,
        approver_id=current_user.id,
        org_id=current_user.organization_id,
        skip=skip,
        limit=limit,
    )

    return PlaybookApprovalListResponse(
        data=[
            PlaybookApprovalResponse(
                id=a.id,
                progress_id=a.progress_id,
                step_id=a.step_id,
                requested_by_id=a.requested_by_id,
                approver_id=a.approver_id,
                status=a.status,
                comments=a.comments,
                required_role=a.required_role,
                requested_at=a.requested_at,
                responded_at=a.responded_at,
                created_at=a.created_at,
                step_title=a.step.title if a.step else None,
                requested_by_name=None,
                approver_name=None,
            )
            for a in approvals
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/progress/{progress_id}/request-approval", response_model=PlaybookApprovalResponse)
async def request_approval(
    progress_id: str,
    approval_request: ApprovalRequestCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaybookApprovalResponse:
    """Request approval for a step."""
    progress = await playbook_service.get_progress_by_id(
        db,
        progress_id=progress_id,
        org_id=current_user.organization_id,
    )

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )

    if progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    approval = await playbook_service.request_approval(
        db,
        progress=progress,
        step_id=approval_request.step_id,
        requested_by_id=current_user.id,
        required_role=approval_request.required_role,
    )

    return PlaybookApprovalResponse.model_validate(approval)


@router.post("/approvals/{approval_id}/respond", response_model=PlaybookApprovalResponse)
async def respond_to_approval(
    approval_id: str,
    response: ApprovalResponseData,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaybookApprovalResponse:
    """Approve or reject an approval request."""
    approval = await playbook_service.get_approval_by_id(db, approval_id)

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )

    updated = await playbook_service.respond_to_approval(
        db,
        approval=approval,
        approver_id=current_user.id,
        status=response.status,
        comments=response.comments,
    )

    return PlaybookApprovalResponse.model_validate(updated)


# ============================================================================
# Stats Endpoint
# ============================================================================


@router.get("/stats/summary")
async def get_playbook_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Get playbook statistics for the organization."""
    stats = await playbook_service.get_playbook_stats(
        db, org_id=current_user.organization_id
    )
    return stats
