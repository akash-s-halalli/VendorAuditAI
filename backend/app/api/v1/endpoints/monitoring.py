"""Monitoring and alerting API endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.models.monitoring import (
    Alert,
    AlertRule,
    AlertSeverity,
    AlertStatus,
    MonitoringSchedule,
    NotificationChannel,
    ScheduledRun,
    ScheduleFrequency,
    ScheduleStatus,
)
from app.schemas.monitoring import (
    AlertAcknowledge,
    AlertListResponse,
    AlertResolve,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    MonitoringDashboardStats,
    MonitoringScheduleCreate,
    MonitoringScheduleResponse,
    MonitoringScheduleUpdate,
    NotificationChannelCreate,
    NotificationChannelResponse,
    NotificationChannelTest,
    ScheduledRunResponse,
)

router = APIRouter(tags=["Monitoring"])


# Helper function to calculate next run time
def calculate_next_run(frequency: str, from_time: datetime | None = None) -> datetime:
    """Calculate the next run time based on frequency."""
    now = from_time or datetime.now(timezone.utc)
    deltas = {
        ScheduleFrequency.DAILY.value: timedelta(days=1),
        ScheduleFrequency.WEEKLY.value: timedelta(weeks=1),
        ScheduleFrequency.BIWEEKLY.value: timedelta(weeks=2),
        ScheduleFrequency.MONTHLY.value: timedelta(days=30),
        ScheduleFrequency.QUARTERLY.value: timedelta(days=90),
    }
    return now + deltas.get(frequency, timedelta(days=30))


# === Monitoring Schedules ===


@router.get("/schedules", response_model=list[MonitoringScheduleResponse])
async def list_schedules(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = Query(None, description="Filter by status"),
) -> list[MonitoringScheduleResponse]:
    """List all monitoring schedules for the organization."""
    query = select(MonitoringSchedule).where(
        MonitoringSchedule.organization_id == current_user.organization_id
    )

    if status:
        query = query.where(MonitoringSchedule.status == status)

    query = query.order_by(MonitoringSchedule.created_at.desc())

    result = await db.execute(query)
    schedules = result.scalars().all()

    return [MonitoringScheduleResponse.model_validate(s) for s in schedules]


@router.post("/schedules", response_model=MonitoringScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: MonitoringScheduleCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MonitoringScheduleResponse:
    """Create a new monitoring schedule."""
    schedule = MonitoringSchedule(
        organization_id=current_user.organization_id,
        vendor_id=schedule_data.vendor_id,
        name=schedule_data.name,
        description=schedule_data.description,
        frequency=schedule_data.frequency,
        framework=schedule_data.framework,
        include_all_vendors=schedule_data.include_all_vendors,
        notify_on_completion=schedule_data.notify_on_completion,
        notify_on_findings=schedule_data.notify_on_findings,
        next_run_at=calculate_next_run(schedule_data.frequency),
        status=ScheduleStatus.ACTIVE.value,
    )

    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)

    return MonitoringScheduleResponse.model_validate(schedule)


@router.get("/schedules/{schedule_id}", response_model=MonitoringScheduleResponse)
async def get_schedule(
    schedule_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MonitoringScheduleResponse:
    """Get a monitoring schedule by ID."""
    query = select(MonitoringSchedule).where(
        and_(
            MonitoringSchedule.id == schedule_id,
            MonitoringSchedule.organization_id == current_user.organization_id,
        )
    )

    result = await db.execute(query)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring schedule not found",
        )

    return MonitoringScheduleResponse.model_validate(schedule)


@router.patch("/schedules/{schedule_id}", response_model=MonitoringScheduleResponse)
async def update_schedule(
    schedule_id: str,
    update_data: MonitoringScheduleUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MonitoringScheduleResponse:
    """Update a monitoring schedule."""
    query = select(MonitoringSchedule).where(
        and_(
            MonitoringSchedule.id == schedule_id,
            MonitoringSchedule.organization_id == current_user.organization_id,
        )
    )

    result = await db.execute(query)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring schedule not found",
        )

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(schedule, field, value)

    # Recalculate next run if frequency changed
    if "frequency" in update_dict:
        schedule.next_run_at = calculate_next_run(update_dict["frequency"])

    await db.commit()
    await db.refresh(schedule)

    return MonitoringScheduleResponse.model_validate(schedule)


@router.post("/schedules/{schedule_id}/run", response_model=ScheduledRunResponse)
async def trigger_schedule_run(
    schedule_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ScheduledRunResponse:
    """Manually trigger a scheduled assessment run."""
    query = select(MonitoringSchedule).where(
        and_(
            MonitoringSchedule.id == schedule_id,
            MonitoringSchedule.organization_id == current_user.organization_id,
        )
    )

    result = await db.execute(query)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring schedule not found",
        )

    # Create a scheduled run record
    run = ScheduledRun(
        schedule_id=schedule.id,
        organization_id=current_user.organization_id,
        status="pending",
    )

    db.add(run)
    await db.commit()
    await db.refresh(run)

    # In a real implementation, this would trigger an async task
    # For now, we just record the run request

    return ScheduledRunResponse.model_validate(run)


# === Alerts ===


@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, description="Filter by status"),
    severity: str | None = Query(None, description="Filter by severity"),
    vendor_id: str | None = Query(None, description="Filter by vendor"),
) -> AlertListResponse:
    """List alerts for the organization."""
    query = select(Alert).where(
        Alert.organization_id == current_user.organization_id
    )

    if status:
        query = query.where(Alert.status == status)
    if severity:
        query = query.where(Alert.severity == severity)
    if vendor_id:
        query = query.where(Alert.vendor_id == vendor_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(Alert.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    return AlertListResponse(
        data=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: str,
    ack_data: AlertAcknowledge,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AlertResponse:
    """Acknowledge an alert."""
    query = select(Alert).where(
        and_(
            Alert.id == alert_id,
            Alert.organization_id == current_user.organization_id,
        )
    )

    result = await db.execute(query)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    alert.status = AlertStatus.ACKNOWLEDGED.value
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by_id = current_user.id

    await db.commit()
    await db.refresh(alert)

    return AlertResponse.model_validate(alert)


@router.post("/alerts/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: str,
    resolve_data: AlertResolve,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AlertResponse:
    """Resolve an alert."""
    query = select(Alert).where(
        and_(
            Alert.id == alert_id,
            Alert.organization_id == current_user.organization_id,
        )
    )

    result = await db.execute(query)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    alert.status = AlertStatus.RESOLVED.value
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolved_by_id = current_user.id
    alert.resolution_notes = resolve_data.resolution_notes

    await db.commit()
    await db.refresh(alert)

    return AlertResponse.model_validate(alert)


# === Alert Rules ===


@router.get("/rules", response_model=list[AlertRuleResponse])
async def list_alert_rules(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AlertRuleResponse]:
    """List alert rules for the organization."""
    query = select(AlertRule).where(
        AlertRule.organization_id == current_user.organization_id
    ).order_by(AlertRule.created_at.desc())

    result = await db.execute(query)
    rules = result.scalars().all()

    return [AlertRuleResponse.model_validate(r) for r in rules]


@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AlertRuleResponse:
    """Create an alert rule."""
    rule = AlertRule(
        organization_id=current_user.organization_id,
        name=rule_data.name,
        description=rule_data.description,
        trigger_type=rule_data.trigger_type,
        trigger_conditions=rule_data.trigger_conditions,
        severity=rule_data.severity,
        is_active=True,
    )

    db.add(rule)
    await db.commit()
    await db.refresh(rule)

    return AlertRuleResponse.model_validate(rule)


# === Notification Channels ===


@router.get("/channels", response_model=list[NotificationChannelResponse])
async def list_notification_channels(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[NotificationChannelResponse]:
    """List notification channels for the organization."""
    query = select(NotificationChannel).where(
        NotificationChannel.organization_id == current_user.organization_id
    ).order_by(NotificationChannel.created_at.desc())

    result = await db.execute(query)
    channels = result.scalars().all()

    return [NotificationChannelResponse.model_validate(c) for c in channels]


@router.post("/channels", response_model=NotificationChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_channel(
    channel_data: NotificationChannelCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> NotificationChannelResponse:
    """Create a notification channel."""
    channel = NotificationChannel(
        organization_id=current_user.organization_id,
        name=channel_data.name,
        channel_type=channel_data.channel_type,
        config=channel_data.config,
        is_active=True,
    )

    db.add(channel)
    await db.commit()
    await db.refresh(channel)

    return NotificationChannelResponse.model_validate(channel)


@router.post("/channels/{channel_id}/test")
async def test_notification_channel(
    channel_id: str,
    test_data: NotificationChannelTest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Test a notification channel by sending a test message."""
    query = select(NotificationChannel).where(
        and_(
            NotificationChannel.id == channel_id,
            NotificationChannel.organization_id == current_user.organization_id,
        )
    )

    result = await db.execute(query)
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification channel not found",
        )

    # In a real implementation, this would send a test notification
    # For now, we just simulate success
    channel.last_used_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "success": True,
        "message": f"Test notification sent to {channel.name}",
        "channel_type": channel.channel_type,
    }


# === Dashboard ===


@router.get("/dashboard", response_model=MonitoringDashboardStats)
async def get_monitoring_dashboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MonitoringDashboardStats:
    """Get monitoring dashboard statistics."""
    org_id = current_user.organization_id

    # Active schedules
    active_query = select(func.count()).where(
        and_(
            MonitoringSchedule.organization_id == org_id,
            MonitoringSchedule.status == ScheduleStatus.ACTIVE.value,
        )
    )
    active_result = await db.execute(active_query)
    active_schedules = active_result.scalar() or 0

    # Total alerts
    total_query = select(func.count()).where(
        Alert.organization_id == org_id
    )
    total_result = await db.execute(total_query)
    total_alerts = total_result.scalar() or 0

    # Open alerts
    open_statuses = [AlertStatus.NEW.value, AlertStatus.ACKNOWLEDGED.value, AlertStatus.IN_PROGRESS.value]
    open_query = select(func.count()).where(
        and_(
            Alert.organization_id == org_id,
            Alert.status.in_(open_statuses),
        )
    )
    open_result = await db.execute(open_query)
    open_alerts = open_result.scalar() or 0

    # Critical alerts
    critical_query = select(func.count()).where(
        and_(
            Alert.organization_id == org_id,
            Alert.severity == AlertSeverity.CRITICAL.value,
            Alert.status.in_(open_statuses),
        )
    )
    critical_result = await db.execute(critical_query)
    critical_alerts = critical_result.scalar() or 0

    # Recent runs (last 7 days)
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_query = select(func.count()).where(
        and_(
            ScheduledRun.organization_id == org_id,
            ScheduledRun.created_at >= week_ago,
        )
    )
    recent_result = await db.execute(recent_query)
    recent_runs = recent_result.scalar() or 0

    # Alerts by severity
    severity_query = select(
        Alert.severity, func.count()
    ).where(
        Alert.organization_id == org_id
    ).group_by(Alert.severity)
    severity_result = await db.execute(severity_query)
    alerts_by_severity = {row[0]: row[1] for row in severity_result.all()}

    # Alerts by status
    status_query = select(
        Alert.status, func.count()
    ).where(
        Alert.organization_id == org_id
    ).group_by(Alert.status)
    status_result = await db.execute(status_query)
    alerts_by_status = {row[0]: row[1] for row in status_result.all()}

    return MonitoringDashboardStats(
        active_schedules=active_schedules,
        total_alerts=total_alerts,
        open_alerts=open_alerts,
        critical_alerts=critical_alerts,
        recent_runs=recent_runs,
        alerts_by_severity=alerts_by_severity,
        alerts_by_status=alerts_by_status,
    )
