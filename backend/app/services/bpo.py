"""BPO (Business Process Outsourcing) service layer for risk management.

Provides business logic for managing BPO providers, processes, assessments,
and controls with full multi-tenant organization isolation.
"""

import json
from datetime import date, datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bpo import BPOAssessment, BPOControl, BPOProcess, BPOProvider
from app.schemas.bpo import (
    AssessmentStatus,
    BPOAssessmentCreate,
    BPOAssessmentUpdate,
    BPOControlCreate,
    BPOControlUpdate,
    BPOProcessCreate,
    BPOProviderCreate,
    BPOProviderUpdate,
    ControlStatus,
    Criticality,
    ServiceType,
)


# --- BPO Provider Functions ---


async def get_bpo_providers(
    db: AsyncSession,
    org_id: str,
    service_type: ServiceType | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[BPOProvider], int]:
    """List BPO providers with pagination and filtering.

    Args:
        db: Database session
        org_id: Organization ID for multi-tenant isolation
        service_type: Optional filter by service type
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of providers, total count)
    """
    # Base query with organization isolation
    query = select(BPOProvider).where(BPOProvider.organization_id == org_id)

    # Apply service type filter
    if service_type:
        query = query.where(BPOProvider.service_type == service_type.value)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(BPOProvider.name).offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    providers = list(result.scalars().all())

    return providers, total


async def get_bpo_provider(
    db: AsyncSession,
    provider_id: str,
    org_id: str,
) -> BPOProvider | None:
    """Get a single BPO provider by ID with organization isolation.

    Args:
        db: Database session
        provider_id: Provider UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        BPOProvider if found, None otherwise
    """
    result = await db.execute(
        select(BPOProvider)
        .options(selectinload(BPOProvider.processes))
        .where(
            BPOProvider.id == provider_id,
            BPOProvider.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def get_bpo_provider_by_name(
    db: AsyncSession,
    name: str,
    org_id: str,
) -> BPOProvider | None:
    """Get a BPO provider by name within an organization.

    Args:
        db: Database session
        name: Provider name
        org_id: Organization ID

    Returns:
        BPOProvider if found, None otherwise
    """
    result = await db.execute(
        select(BPOProvider).where(
            BPOProvider.name == name,
            BPOProvider.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def create_bpo_provider(
    db: AsyncSession,
    org_id: str,
    data: BPOProviderCreate,
) -> BPOProvider:
    """Create a new BPO provider.

    Args:
        db: Database session
        org_id: Organization ID
        data: Provider creation data

    Returns:
        Created BPOProvider

    Raises:
        ValueError: If provider name already exists in organization
    """
    # Check for duplicate name
    existing = await get_bpo_provider_by_name(db, data.name, org_id)
    if existing:
        raise ValueError(f"BPO provider with name '{data.name}' already exists")

    # Serialize list fields to JSON
    certifications_json = json.dumps(data.certifications) if data.certifications else None
    tags_json = json.dumps(data.tags) if data.tags else None

    provider = BPOProvider(
        organization_id=org_id,
        name=data.name,
        description=data.description,
        service_type=data.service_type.value,
        country=data.country,
        city=data.city,
        contact_name=data.contact_name,
        contact_email=data.contact_email,
        contact_phone=data.contact_phone,
        contract_start_date=data.contract_start_date,
        contract_end_date=data.contract_end_date,
        data_access_level=data.data_access_level.value,
        criticality=data.criticality.value,
        employee_count=data.employee_count,
        certifications=certifications_json,
        tags=tags_json,
        is_active=True,
    )

    db.add(provider)
    await db.flush()
    await db.refresh(provider)
    return provider


async def update_bpo_provider(
    db: AsyncSession,
    provider_id: str,
    org_id: str,
    data: BPOProviderUpdate,
) -> BPOProvider | None:
    """Update a BPO provider's information.

    Args:
        db: Database session
        provider_id: Provider UUID
        org_id: Organization ID for multi-tenant isolation
        data: Fields to update

    Returns:
        Updated BPOProvider or None if not found

    Raises:
        ValueError: If updating name to one that already exists
    """
    provider = await get_bpo_provider(db, provider_id, org_id)
    if not provider:
        return None

    # Get update data, excluding unset fields
    update_data = data.model_dump(exclude_unset=True)

    # Check for duplicate name if name is being updated
    if "name" in update_data and update_data["name"] != provider.name:
        existing = await get_bpo_provider_by_name(db, update_data["name"], org_id)
        if existing:
            raise ValueError(f"BPO provider with name '{update_data['name']}' already exists")

    # Handle enum serialization
    if "service_type" in update_data and update_data["service_type"]:
        update_data["service_type"] = update_data["service_type"].value
    if "data_access_level" in update_data and update_data["data_access_level"]:
        update_data["data_access_level"] = update_data["data_access_level"].value
    if "criticality" in update_data and update_data["criticality"]:
        update_data["criticality"] = update_data["criticality"].value

    # Handle list serialization
    if "certifications" in update_data:
        update_data["certifications"] = (
            json.dumps(update_data["certifications"])
            if update_data["certifications"]
            else None
        )
    if "tags" in update_data:
        update_data["tags"] = (
            json.dumps(update_data["tags"])
            if update_data["tags"]
            else None
        )

    # Apply updates
    for field, value in update_data.items():
        setattr(provider, field, value)

    await db.flush()
    await db.refresh(provider)
    return provider


async def delete_bpo_provider(
    db: AsyncSession,
    provider_id: str,
    org_id: str,
) -> bool:
    """Delete a BPO provider.

    Args:
        db: Database session
        provider_id: Provider UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        True if deleted, False if not found
    """
    provider = await get_bpo_provider(db, provider_id, org_id)
    if not provider:
        return False

    await db.delete(provider)
    await db.flush()
    return True


# --- BPO Process Functions ---


async def add_process(
    db: AsyncSession,
    provider_id: str,
    org_id: str,
    data: BPOProcessCreate,
) -> BPOProcess | None:
    """Add a process to a BPO provider.

    Args:
        db: Database session
        provider_id: Provider UUID
        org_id: Organization ID for verification
        data: Process creation data

    Returns:
        Created BPOProcess or None if provider not found
    """
    # Verify provider exists and belongs to organization
    provider = await get_bpo_provider(db, provider_id, org_id)
    if not provider:
        return None

    # Serialize list fields
    data_types_json = (
        json.dumps(data.data_types_handled)
        if data.data_types_handled
        else None
    )

    process = BPOProcess(
        provider_id=provider_id,
        name=data.name,
        description=data.description,
        category=data.category.value,
        criticality=data.criticality.value,
        data_types_handled=data_types_json,
        volume_per_month=data.volume_per_month,
        sla_response_time_hours=data.sla_response_time_hours,
        sla_resolution_time_hours=data.sla_resolution_time_hours,
        is_active=data.is_active,
    )

    db.add(process)
    await db.flush()
    await db.refresh(process)
    return process


async def get_processes(
    db: AsyncSession,
    provider_id: str,
    org_id: str,
) -> list[BPOProcess]:
    """Get all processes for a BPO provider.

    Args:
        db: Database session
        provider_id: Provider UUID
        org_id: Organization ID for verification

    Returns:
        List of BPOProcess objects
    """
    # Verify provider exists and belongs to organization
    provider = await get_bpo_provider(db, provider_id, org_id)
    if not provider:
        return []

    result = await db.execute(
        select(BPOProcess)
        .where(BPOProcess.provider_id == provider_id)
        .order_by(BPOProcess.name)
    )
    return list(result.scalars().all())


# --- BPO Assessment Functions ---


async def create_assessment(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    data: BPOAssessmentCreate,
) -> BPOAssessment:
    """Create a new BPO assessment.

    Args:
        db: Database session
        org_id: Organization ID
        user_id: ID of the user creating/assigned to the assessment
        data: Assessment creation data

    Returns:
        Created BPOAssessment

    Raises:
        ValueError: If provider not found in organization
    """
    # Verify provider exists and belongs to organization
    provider_result = await db.execute(
        select(BPOProvider).where(
            BPOProvider.id == data.provider_id,
            BPOProvider.organization_id == org_id,
        )
    )
    provider = provider_result.scalar_one_or_none()
    if not provider:
        raise ValueError(f"BPO provider with ID '{data.provider_id}' not found")

    # Serialize list fields
    scope_json = json.dumps(data.scope) if data.scope else None

    # Determine initial status based on scheduled date
    status = AssessmentStatus.SCHEDULED
    if data.scheduled_date <= date.today():
        status = AssessmentStatus.IN_PROGRESS

    assessment = BPOAssessment(
        organization_id=org_id,
        provider_id=data.provider_id,
        assessor_id=user_id,
        assessment_type=data.assessment_type.value,
        status=status.value,
        scheduled_date=data.scheduled_date,
        title=data.title,
        description=data.description,
        scope=scope_json,
    )

    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)
    return assessment


async def get_assessments(
    db: AsyncSession,
    org_id: str,
    provider_id: str | None = None,
    status: AssessmentStatus | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[BPOAssessment], int]:
    """List BPO assessments with pagination and filtering.

    Args:
        db: Database session
        org_id: Organization ID for multi-tenant isolation
        provider_id: Optional filter by provider
        status: Optional filter by status
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of assessments, total count)
    """
    # Base query with organization isolation
    query = select(BPOAssessment).where(BPOAssessment.organization_id == org_id)

    # Apply filters
    if provider_id:
        query = query.where(BPOAssessment.provider_id == provider_id)
    if status:
        query = query.where(BPOAssessment.status == status.value)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering (most recent first)
    query = query.order_by(BPOAssessment.scheduled_date.desc()).offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    assessments = list(result.scalars().all())

    return assessments, total


async def get_assessment(
    db: AsyncSession,
    assessment_id: str,
    org_id: str,
) -> BPOAssessment | None:
    """Get a single assessment by ID.

    Args:
        db: Database session
        assessment_id: Assessment UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        BPOAssessment if found, None otherwise
    """
    result = await db.execute(
        select(BPOAssessment).where(
            BPOAssessment.id == assessment_id,
            BPOAssessment.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def update_assessment(
    db: AsyncSession,
    assessment_id: str,
    org_id: str,
    data: BPOAssessmentUpdate,
) -> BPOAssessment | None:
    """Update a BPO assessment.

    Args:
        db: Database session
        assessment_id: Assessment UUID
        org_id: Organization ID for multi-tenant isolation
        data: Fields to update

    Returns:
        Updated BPOAssessment or None if not found
    """
    assessment = await get_assessment(db, assessment_id, org_id)
    if not assessment:
        return None

    # Get update data, excluding unset fields
    update_data = data.model_dump(exclude_unset=True)

    # Handle enum serialization
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value

    # Handle list serialization
    if "scope" in update_data:
        update_data["scope"] = (
            json.dumps(update_data["scope"])
            if update_data["scope"]
            else None
        )
    if "recommendations" in update_data:
        update_data["recommendations"] = (
            json.dumps(update_data["recommendations"])
            if update_data["recommendations"]
            else None
        )

    # Apply updates
    for field, value in update_data.items():
        setattr(assessment, field, value)

    # If completing assessment, update provider's last_assessed
    if data.status == AssessmentStatus.COMPLETED:
        provider_result = await db.execute(
            select(BPOProvider).where(BPOProvider.id == assessment.provider_id)
        )
        provider = provider_result.scalar_one_or_none()
        if provider:
            provider.last_assessed = datetime.now()
            # Set next assessment due (default: 1 year)
            provider.next_assessment_due = date.today() + timedelta(days=365)

    await db.flush()
    await db.refresh(assessment)
    return assessment


# --- BPO Control Functions ---


async def get_process_by_id(
    db: AsyncSession,
    process_id: str,
    org_id: str,
) -> BPOProcess | None:
    """Get a process by ID with organization verification.

    Args:
        db: Database session
        process_id: Process UUID
        org_id: Organization ID for verification

    Returns:
        BPOProcess if found and belongs to org, None otherwise
    """
    result = await db.execute(
        select(BPOProcess)
        .join(BPOProvider)
        .where(
            BPOProcess.id == process_id,
            BPOProvider.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def add_control(
    db: AsyncSession,
    process_id: str,
    org_id: str,
    data: BPOControlCreate,
) -> BPOControl | None:
    """Add a control to a BPO process.

    Args:
        db: Database session
        process_id: Process UUID
        org_id: Organization ID for verification
        data: Control creation data

    Returns:
        Created BPOControl or None if process not found
    """
    # Verify process exists and belongs to organization
    process = await get_process_by_id(db, process_id, org_id)
    if not process:
        return None

    control = BPOControl(
        process_id=process_id,
        name=data.name,
        description=data.description,
        control_type=data.control_type.value,
        control_category=data.control_category.value,
        status=data.status.value,
        effectiveness_score=data.effectiveness_score,
        last_tested=data.last_tested,
        next_test_due=data.next_test_due,
        evidence_required=data.evidence_required,
        notes=data.notes,
    )

    db.add(control)
    await db.flush()
    await db.refresh(control)
    return control


async def get_control_by_id(
    db: AsyncSession,
    control_id: str,
    org_id: str,
) -> BPOControl | None:
    """Get a control by ID with organization verification.

    Args:
        db: Database session
        control_id: Control UUID
        org_id: Organization ID for verification

    Returns:
        BPOControl if found and belongs to org, None otherwise
    """
    result = await db.execute(
        select(BPOControl)
        .join(BPOProcess)
        .join(BPOProvider)
        .where(
            BPOControl.id == control_id,
            BPOProvider.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def update_control(
    db: AsyncSession,
    control_id: str,
    org_id: str,
    data: BPOControlUpdate,
) -> BPOControl | None:
    """Update a BPO control.

    Args:
        db: Database session
        control_id: Control UUID
        org_id: Organization ID for verification
        data: Fields to update

    Returns:
        Updated BPOControl or None if not found
    """
    control = await get_control_by_id(db, control_id, org_id)
    if not control:
        return None

    # Get update data, excluding unset fields
    update_data = data.model_dump(exclude_unset=True)

    # Handle enum serialization
    if "control_type" in update_data and update_data["control_type"]:
        update_data["control_type"] = update_data["control_type"].value
    if "control_category" in update_data and update_data["control_category"]:
        update_data["control_category"] = update_data["control_category"].value
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value

    # Apply updates
    for field, value in update_data.items():
        setattr(control, field, value)

    await db.flush()
    await db.refresh(control)
    return control


# --- Dashboard Stats ---


async def get_bpo_dashboard_stats(
    db: AsyncSession,
    org_id: str,
) -> dict:
    """Get comprehensive BPO dashboard statistics.

    Args:
        db: Database session
        org_id: Organization ID

    Returns:
        Dictionary with dashboard statistics
    """
    today = date.today()
    month_start = today.replace(day=1)
    next_30_days = today + timedelta(days=30)
    next_90_days = today + timedelta(days=90)

    # Provider counts
    providers_result = await db.execute(
        select(func.count()).where(BPOProvider.organization_id == org_id)
    )
    total_providers = providers_result.scalar() or 0

    active_providers_result = await db.execute(
        select(func.count()).where(
            BPOProvider.organization_id == org_id,
            BPOProvider.is_active == True,  # noqa: E712
        )
    )
    active_providers = active_providers_result.scalar() or 0

    # Process counts
    processes_result = await db.execute(
        select(func.count())
        .select_from(BPOProcess)
        .join(BPOProvider)
        .where(BPOProvider.organization_id == org_id)
    )
    total_processes = processes_result.scalar() or 0

    critical_processes_result = await db.execute(
        select(func.count())
        .select_from(BPOProcess)
        .join(BPOProvider)
        .where(
            BPOProvider.organization_id == org_id,
            BPOProcess.criticality == Criticality.CRITICAL.value,
        )
    )
    critical_processes = critical_processes_result.scalar() or 0

    # Assessment counts
    assessments_result = await db.execute(
        select(func.count()).where(BPOAssessment.organization_id == org_id)
    )
    total_assessments = assessments_result.scalar() or 0

    in_progress_result = await db.execute(
        select(func.count()).where(
            BPOAssessment.organization_id == org_id,
            BPOAssessment.status == AssessmentStatus.IN_PROGRESS.value,
        )
    )
    assessments_in_progress = in_progress_result.scalar() or 0

    overdue_result = await db.execute(
        select(func.count()).where(
            BPOAssessment.organization_id == org_id,
            BPOAssessment.status == AssessmentStatus.OVERDUE.value,
        )
    )
    assessments_overdue = overdue_result.scalar() or 0

    completed_this_month_result = await db.execute(
        select(func.count()).where(
            BPOAssessment.organization_id == org_id,
            BPOAssessment.status == AssessmentStatus.COMPLETED.value,
            BPOAssessment.completed_date >= month_start,
        )
    )
    assessments_completed_this_month = completed_this_month_result.scalar() or 0

    upcoming_assessments_result = await db.execute(
        select(func.count()).where(
            BPOAssessment.organization_id == org_id,
            BPOAssessment.status == AssessmentStatus.SCHEDULED.value,
            BPOAssessment.scheduled_date <= next_30_days,
        )
    )
    upcoming_assessments = upcoming_assessments_result.scalar() or 0

    # Control counts
    controls_result = await db.execute(
        select(func.count())
        .select_from(BPOControl)
        .join(BPOProcess)
        .join(BPOProvider)
        .where(BPOProvider.organization_id == org_id)
    )
    total_controls = controls_result.scalar() or 0

    implemented_result = await db.execute(
        select(func.count())
        .select_from(BPOControl)
        .join(BPOProcess)
        .join(BPOProvider)
        .where(
            BPOProvider.organization_id == org_id,
            BPOControl.status == ControlStatus.IMPLEMENTED.value,
        )
    )
    controls_implemented = implemented_result.scalar() or 0

    partial_result = await db.execute(
        select(func.count())
        .select_from(BPOControl)
        .join(BPOProcess)
        .join(BPOProvider)
        .where(
            BPOProvider.organization_id == org_id,
            BPOControl.status == ControlStatus.PARTIAL.value,
        )
    )
    controls_partial = partial_result.scalar() or 0

    not_implemented_result = await db.execute(
        select(func.count())
        .select_from(BPOControl)
        .join(BPOProcess)
        .join(BPOProvider)
        .where(
            BPOProvider.organization_id == org_id,
            BPOControl.status == ControlStatus.NOT_IMPLEMENTED.value,
        )
    )
    controls_not_implemented = not_implemented_result.scalar() or 0

    # Average risk score
    avg_risk_result = await db.execute(
        select(func.avg(BPOProvider.risk_score)).where(
            BPOProvider.organization_id == org_id,
            BPOProvider.risk_score.isnot(None),
        )
    )
    average_risk_score = avg_risk_result.scalar()
    if average_risk_score:
        average_risk_score = round(float(average_risk_score), 2)

    # Providers by service type
    service_type_result = await db.execute(
        select(BPOProvider.service_type, func.count())
        .where(BPOProvider.organization_id == org_id)
        .group_by(BPOProvider.service_type)
    )
    providers_by_service_type = {
        row[0]: row[1] for row in service_type_result.fetchall()
    }

    # Providers by criticality
    criticality_result = await db.execute(
        select(BPOProvider.criticality, func.count())
        .where(BPOProvider.organization_id == org_id)
        .group_by(BPOProvider.criticality)
    )
    providers_by_criticality = {
        row[0]: row[1] for row in criticality_result.fetchall()
    }

    # Contracts expiring soon
    contracts_expiring_result = await db.execute(
        select(func.count()).where(
            BPOProvider.organization_id == org_id,
            BPOProvider.contract_end_date.isnot(None),
            BPOProvider.contract_end_date <= next_90_days,
            BPOProvider.contract_end_date >= today,
        )
    )
    contracts_expiring_soon = contracts_expiring_result.scalar() or 0

    return {
        "total_providers": total_providers,
        "active_providers": active_providers,
        "total_processes": total_processes,
        "critical_processes": critical_processes,
        "total_assessments": total_assessments,
        "assessments_in_progress": assessments_in_progress,
        "assessments_overdue": assessments_overdue,
        "assessments_completed_this_month": assessments_completed_this_month,
        "total_controls": total_controls,
        "controls_implemented": controls_implemented,
        "controls_partial": controls_partial,
        "controls_not_implemented": controls_not_implemented,
        "average_risk_score": average_risk_score,
        "providers_by_service_type": providers_by_service_type,
        "providers_by_criticality": providers_by_criticality,
        "upcoming_assessments": upcoming_assessments,
        "contracts_expiring_soon": contracts_expiring_soon,
    }
