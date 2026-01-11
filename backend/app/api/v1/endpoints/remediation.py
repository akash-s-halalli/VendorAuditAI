"""Remediation workflow API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.schemas.remediation import (
    RemediationCommentCreate,
    RemediationCommentResponse,
    RemediationDashboardStats,
    RemediationTaskCreate,
    RemediationTaskDetail,
    RemediationTaskListResponse,
    RemediationTaskResponse,
    RemediationTaskUpdate,
    RemediationTransition,
    SLAPolicyCreate,
    SLAPolicyResponse,
)
from app.services.remediation import get_remediation_service

router = APIRouter(tags=["Remediation"])


@router.get("/tasks", response_model=RemediationTaskListResponse)
async def list_tasks(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status"),
    priority: str | None = Query(None, description="Filter by priority"),
    assignee_id: str | None = Query(None, description="Filter by assignee"),
    vendor_id: str | None = Query(None, description="Filter by vendor"),
    is_overdue: bool | None = Query(None, description="Filter overdue tasks"),
) -> RemediationTaskListResponse:
    """
    List remediation tasks for the current user's organization.

    Supports pagination and filtering by status, priority, assignee, vendor, and overdue status.
    """
    service = get_remediation_service(db)
    tasks, total = await service.list_tasks(
        organization_id=current_user.organization_id,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        vendor_id=vendor_id,
        is_overdue=is_overdue,
        page=page,
        limit=limit,
    )

    return RemediationTaskListResponse(
        data=[RemediationTaskResponse.model_validate(t) for t in tasks],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/tasks", response_model=RemediationTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: RemediationTaskCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RemediationTaskResponse:
    """
    Create a new remediation task from a finding.

    The task will be initialized in DRAFT status. SLA is calculated
    based on priority and the organization's default SLA policy.
    """
    service = get_remediation_service(db)
    task = await service.create_task(
        task_data=task_data,
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
    )
    return RemediationTaskResponse.model_validate(task)


@router.get("/tasks/{task_id}", response_model=RemediationTaskDetail)
async def get_task(
    task_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RemediationTaskDetail:
    """
    Get a remediation task by ID with full audit trail and comments.
    """
    service = get_remediation_service(db)
    task = await service.get_task(
        task_id=task_id,
        organization_id=current_user.organization_id,
        include_details=True,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation task not found",
        )

    return RemediationTaskDetail.model_validate(task)


@router.patch("/tasks/{task_id}", response_model=RemediationTaskResponse)
async def update_task(
    task_id: str,
    update_data: RemediationTaskUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RemediationTaskResponse:
    """
    Update a remediation task.

    Changes are tracked in the audit trail.
    """
    service = get_remediation_service(db)
    task = await service.update_task(
        task_id=task_id,
        organization_id=current_user.organization_id,
        update_data=update_data,
        user_id=current_user.id,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation task not found",
        )

    return RemediationTaskResponse.model_validate(task)


@router.post("/tasks/{task_id}/transition", response_model=RemediationTaskResponse)
async def transition_task(
    task_id: str,
    transition: RemediationTransition,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RemediationTaskResponse:
    """
    Transition a task to a new status.

    Valid transitions are enforced by the state machine:
    - draft -> pending_assignment
    - pending_assignment -> assigned
    - assigned -> in_progress, exception_requested
    - in_progress -> pending_review, exception_requested
    - pending_review -> in_progress, pending_verification
    - pending_verification -> pending_review, verified
    - verified -> closed
    - closed -> reopened
    - exception_requested -> exception_approved, exception_denied
    - exception_denied -> in_progress
    - reopened -> in_progress
    """
    service = get_remediation_service(db)

    try:
        task = await service.transition_task(
            task_id=task_id,
            organization_id=current_user.organization_id,
            transition=transition,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation task not found",
        )

    return RemediationTaskResponse.model_validate(task)


@router.get("/tasks/{task_id}/comments", response_model=list[RemediationCommentResponse])
async def get_comments(
    task_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[RemediationCommentResponse]:
    """
    Get all comments for a remediation task.
    """
    service = get_remediation_service(db)
    comments = await service.get_comments(
        task_id=task_id,
        organization_id=current_user.organization_id,
    )
    return [RemediationCommentResponse.model_validate(c) for c in comments]


@router.post(
    "/tasks/{task_id}/comments",
    response_model=RemediationCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    task_id: str,
    comment_data: RemediationCommentCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RemediationCommentResponse:
    """
    Add a comment to a remediation task.
    """
    service = get_remediation_service(db)
    comment = await service.add_comment(
        task_id=task_id,
        organization_id=current_user.organization_id,
        comment_data=comment_data,
        user_id=current_user.id,
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation task not found",
        )

    return RemediationCommentResponse.model_validate(comment)


@router.get("/dashboard", response_model=RemediationDashboardStats)
async def get_dashboard_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RemediationDashboardStats:
    """
    Get dashboard statistics for remediation tasks.

    Returns:
    - Total tasks
    - Open tasks count
    - Overdue tasks count
    - SLA breached count
    - Tasks by status
    - Tasks by priority
    """
    service = get_remediation_service(db)
    return await service.get_dashboard_stats(
        organization_id=current_user.organization_id
    )


@router.post("/sla-policies", response_model=SLAPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_sla_policy(
    policy_data: SLAPolicyCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SLAPolicyResponse:
    """
    Create an SLA policy for the organization.

    Defines default SLA days based on task priority.
    """
    # Only admins can create SLA policies
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create SLA policies",
        )

    service = get_remediation_service(db)
    policy = await service.create_sla_policy(
        policy_data=policy_data,
        organization_id=current_user.organization_id,
    )
    return SLAPolicyResponse.model_validate(policy)


@router.post("/check-sla-breaches")
async def check_sla_breaches(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Check and mark SLA breaches for overdue tasks.

    This is typically called by a scheduler but can be triggered manually.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can trigger SLA breach checks",
        )

    service = get_remediation_service(db)
    breach_count = await service.check_sla_breaches(
        organization_id=current_user.organization_id
    )

    return {"breaches_marked": breach_count}
