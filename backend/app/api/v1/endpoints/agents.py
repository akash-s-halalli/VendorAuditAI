"""AI Agent management API endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import Agent, AgentLog, AgentStatus, AgentTask, AgentType, TaskStatus, User
from app.schemas.agent import (
    AgentConfigUpdate,
    AgentListResponse,
    AgentResponse,
    AgentStats,
    LogListResponse,
    LogResponse,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
)

router = APIRouter(tags=["AI Agents"])


async def get_or_create_default_agents(
    db: AsyncSession, org_id: str
) -> list[Agent]:
    """Get or create the default 4 agents for an organization."""
    # Check if agents exist
    result = await db.execute(
        select(Agent).where(Agent.organization_id == org_id)
    )
    agents = list(result.scalars().all())

    if len(agents) >= 4:
        return agents

    # Default agent configurations
    default_agents = [
        {
            "name": "Sentinel Prime",
            "agent_type": AgentType.THREAT_DETECTION,
            "role": "Threat Detection",
            "description": "Advanced threat detection agent that continuously monitors documents and vendor data for potential security risks, anomalies, and emerging threats.",
            "configuration": {
                "scan_frequency": "hourly",
                "alert_threshold": 7,
                "enabled_checks": ["malware_indicators", "data_exfiltration", "phishing_patterns", "vulnerability_exploitation"],
                "notification_enabled": True,
            },
        },
        {
            "name": "Vector Analyst",
            "agent_type": AgentType.RISK_ASSESSMENT,
            "role": "Risk Assessment",
            "description": "Risk scoring and assessment agent that calculates vendor risk scores based on multiple factors including findings, compliance status, and historical data.",
            "configuration": {
                "scan_frequency": "daily",
                "risk_model": "weighted_average",
                "factors": ["findings_severity", "compliance_coverage", "data_classification", "vendor_tier"],
                "notification_enabled": True,
            },
        },
        {
            "name": "Watchdog Zero",
            "agent_type": AgentType.VULNERABILITY_SCANNER,
            "role": "Vulnerability Scanner",
            "description": "Continuous vulnerability scanning agent that identifies security gaps, missing controls, expired certifications, and potential weaknesses in vendor security posture.",
            "configuration": {
                "scan_frequency": "daily",
                "scan_depth": "comprehensive",
                "check_certifications": True,
                "check_controls": True,
                "notification_enabled": True,
            },
        },
        {
            "name": "Audit Core",
            "agent_type": AgentType.COMPLIANCE_VERIFICATION,
            "role": "Compliance Verification",
            "description": "Compliance verification agent that maps vendor documents to regulatory frameworks, calculates compliance coverage, and identifies control gaps.",
            "configuration": {
                "scan_frequency": "weekly",
                "frameworks": ["soc2_tsc", "iso_27001", "nist_800_53", "hipaa", "pci_dss"],
                "auto_map_controls": True,
                "notification_enabled": True,
            },
        },
    ]

    # Create missing agents
    existing_types = {a.agent_type for a in agents}
    for agent_config in default_agents:
        if agent_config["agent_type"] not in existing_types:
            agent = Agent(
                organization_id=org_id,
                status=AgentStatus.IDLE,
                uptime_percentage=99.5 + (hash(agent_config["name"]) % 5) / 10,  # 99.5-100%
                **agent_config,
            )
            db.add(agent)
            agents.append(agent)

    await db.commit()
    for agent in agents:
        await db.refresh(agent)

    return agents


@router.get("", response_model=AgentListResponse)
async def list_agents(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentListResponse:
    """
    List all AI agents for the current user's organization.

    Returns the 4 default agents (created on first access):
    - Sentinel Prime: Threat Detection
    - Vector Analyst: Risk Assessment
    - Watchdog Zero: Vulnerability Scanner
    - Audit Core: Compliance Verification
    """
    agents = await get_or_create_default_agents(db, current_user.organization_id)
    return AgentListResponse(
        data=[AgentResponse.model_validate(a) for a in agents],
        total=len(agents),
    )


@router.get("/stats", response_model=AgentStats)
async def get_agent_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentStats:
    """
    Get aggregate statistics for all agents.

    Useful for dashboard displays showing agent health and activity.
    """
    agents = await get_or_create_default_agents(db, current_user.organization_id)

    # Count by status
    status_counts = {
        "active": 0,
        "processing": 0,
        "error": 0,
    }
    for agent in agents:
        if agent.status == AgentStatus.ACTIVE:
            status_counts["active"] += 1
        elif agent.status == AgentStatus.PROCESSING:
            status_counts["processing"] += 1
        elif agent.status == AgentStatus.ERROR:
            status_counts["error"] += 1

    # Get today's task counts
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    agent_ids = [a.id for a in agents]

    # Total tasks today
    total_tasks_result = await db.execute(
        select(func.count(AgentTask.id))
        .where(AgentTask.agent_id.in_(agent_ids))
        .where(AgentTask.created_at >= today_start)
    )
    total_tasks_today = total_tasks_result.scalar() or 0

    # Completed tasks today
    completed_tasks_result = await db.execute(
        select(func.count(AgentTask.id))
        .where(AgentTask.agent_id.in_(agent_ids))
        .where(AgentTask.created_at >= today_start)
        .where(AgentTask.status == TaskStatus.COMPLETED)
    )
    completed_tasks_today = completed_tasks_result.scalar() or 0

    # Total findings today
    findings_result = await db.execute(
        select(func.sum(AgentTask.findings_count))
        .where(AgentTask.agent_id.in_(agent_ids))
        .where(AgentTask.created_at >= today_start)
        .where(AgentTask.status == TaskStatus.COMPLETED)
    )
    total_findings_today = findings_result.scalar() or 0

    return AgentStats(
        total_agents=len(agents),
        active_agents=status_counts["active"],
        processing_agents=status_counts["processing"],
        error_agents=status_counts["error"],
        total_tasks_today=total_tasks_today,
        completed_tasks_today=completed_tasks_today,
        total_findings_today=total_findings_today,
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentResponse:
    """
    Get a specific agent by ID.
    """
    result = await db.execute(
        select(Agent)
        .where(Agent.id == agent_id)
        .where(Agent.organization_id == current_user.organization_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return AgentResponse.model_validate(agent)


@router.patch("/{agent_id}/config", response_model=AgentResponse)
async def update_agent_config(
    agent_id: str,
    config: AgentConfigUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentResponse:
    """
    Update an agent's configuration.

    Allows customizing agent behavior like scan frequency, alert thresholds,
    and enabled checks.
    """
    result = await db.execute(
        select(Agent)
        .where(Agent.id == agent_id)
        .where(Agent.organization_id == current_user.organization_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Update configuration
    current_config = agent.configuration or {}
    update_data = config.model_dump(exclude_unset=True)
    current_config.update(update_data)
    agent.configuration = current_config

    await db.commit()
    await db.refresh(agent)

    return AgentResponse.model_validate(agent)


@router.get("/{agent_id}/logs", response_model=LogListResponse)
async def get_agent_logs(
    agent_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200, description="Number of logs to return"),
    task_id: str | None = Query(None, description="Filter logs by task ID"),
) -> LogListResponse:
    """
    Get recent logs for an agent.

    Returns the most recent log entries, optionally filtered by task.
    """
    # Verify agent belongs to user's org
    agent_result = await db.execute(
        select(Agent)
        .where(Agent.id == agent_id)
        .where(Agent.organization_id == current_user.organization_id)
    )
    if not agent_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Build query
    query = select(AgentLog).where(AgentLog.agent_id == agent_id)
    if task_id:
        query = query.where(AgentLog.task_id == task_id)
    query = query.order_by(AgentLog.created_at.desc()).limit(limit)

    result = await db.execute(query)
    logs = list(result.scalars().all())

    return LogListResponse(
        data=[LogResponse.model_validate(log) for log in logs],
        total=len(logs),
    )


@router.get("/{agent_id}/tasks", response_model=TaskListResponse)
async def get_agent_tasks(
    agent_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100, description="Number of tasks to return"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
) -> TaskListResponse:
    """
    Get task history for an agent.

    Returns recent tasks with their status, timing, and results.
    """
    # Verify agent belongs to user's org
    agent_result = await db.execute(
        select(Agent)
        .where(Agent.id == agent_id)
        .where(Agent.organization_id == current_user.organization_id)
    )
    if not agent_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Build query
    query = select(AgentTask).where(AgentTask.agent_id == agent_id)
    if status_filter:
        query = query.where(AgentTask.status == status_filter)
    query = query.order_by(AgentTask.created_at.desc()).limit(limit)

    result = await db.execute(query)
    tasks = list(result.scalars().all())

    return TaskListResponse(
        data=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
    )


@router.post("/{agent_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_agent_task(
    agent_id: str,
    task_data: TaskCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """
    Trigger a new task for an agent.

    Creates a task that will be executed by the agent's processing service.
    The task runs asynchronously and results can be retrieved via GET /tasks.
    """
    from app.services.agents import agent_manager

    # Verify agent belongs to user's org
    result = await db.execute(
        select(Agent)
        .where(Agent.id == agent_id)
        .where(Agent.organization_id == current_user.organization_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    if agent.status == AgentStatus.DISABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is disabled",
        )

    # Execute the task
    try:
        task = await agent_manager.execute_task(
            db=db,
            agent=agent,
            task_type=task_data.task_type,
            input_data=task_data.input_data,
        )
        await db.commit()
        await db.refresh(task)
        return TaskResponse.model_validate(task)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute task: {str(e)}",
        ) from e


@router.post("/{agent_id}/toggle", response_model=AgentResponse)
async def toggle_agent(
    agent_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentResponse:
    """
    Toggle an agent's enabled/disabled status.

    Disabled agents cannot execute tasks.
    """
    result = await db.execute(
        select(Agent)
        .where(Agent.id == agent_id)
        .where(Agent.organization_id == current_user.organization_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Toggle status
    if agent.status == AgentStatus.DISABLED:
        agent.status = AgentStatus.IDLE
    else:
        agent.status = AgentStatus.DISABLED

    await db.commit()
    await db.refresh(agent)

    return AgentResponse.model_validate(agent)
