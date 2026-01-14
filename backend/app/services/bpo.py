"""BPO (Business Process Outsourcing) service layer for risk management.

Provides business logic for managing BPO providers, processes, assessments,
and controls with full multi-tenant organization isolation.
"""

from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bpo import (
    BPOAssessment,
    BPOControl,
    BPOProcess,
    BPOProvider,
    AssessmentStatus,
    ControlStatus,
    ProcessCriticality,
)
from app.schemas.bpo import (
    BPOAssessmentCreate,
    BPOAssessmentUpdate,
    BPOControlCreate,
    BPOControlUpdate,
    BPOProcessCreate,
    BPOProcessUpdate,
    BPOProviderCreate,
    BPOProviderUpdate,
    BPODashboardStats,
)


# =============================================================================
# BPO Provider Functions
# =============================================================================


async def get_providers(
    db: AsyncSession,
    org_id: str,
    skip: int = 0,
    limit: int = 20,
    service_type: str | None = None,
    search: str | None = None,
) -> tuple[list[BPOProvider], int]:
    """List BPO providers with pagination and filtering."""
    query = select(BPOProvider).where(BPOProvider.organization_id == org_id)

    if service_type:
        query = query.where(BPOProvider.service_type == service_type)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(BPOProvider.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    providers = list(result.scalars().all())

    return providers, total


async def get_provider_by_id(
    db: AsyncSession,
    provider_id: str,
    org_id: str,
    include_processes: bool = False,
) -> BPOProvider | None:
    """Get a single BPO provider by ID."""
    query = select(BPOProvider).where(
        BPOProvider.id == provider_id,
        BPOProvider.organization_id == org_id,
    )

    if include_processes:
        query = query.options(selectinload(BPOProvider.processes))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_provider(
    db: AsyncSession,
    org_id: str,
    provider_data: BPOProviderCreate,
) -> BPOProvider:
    """Create a new BPO provider."""
    provider = BPOProvider(
        organization_id=org_id,
        vendor_id=provider_data.vendor_id,
        service_type=provider_data.service_type,
        process_category=provider_data.process_category,
        geographic_locations=provider_data.geographic_locations,
        data_access_level=provider_data.data_access_level,
        employee_count=provider_data.employee_count,
        contract_value=provider_data.contract_value,
        sla_requirements=provider_data.sla_requirements,
        primary_contact_name=provider_data.primary_contact_name,
        primary_contact_email=provider_data.primary_contact_email,
        contract_start_date=provider_data.contract_start_date,
        contract_end_date=provider_data.contract_end_date,
    )

    db.add(provider)
    await db.flush()
    await db.refresh(provider)
    return provider


async def update_provider(
    db: AsyncSession,
    provider_id: str,
    org_id: str,
    provider_data: BPOProviderUpdate,
) -> BPOProvider | None:
    """Update a BPO provider."""
    provider = await get_provider_by_id(db, provider_id, org_id)
    if not provider:
        return None

    update_data = provider_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(provider, field, value)

    await db.flush()
    await db.refresh(provider)
    return provider


async def delete_provider(
    db: AsyncSession,
    provider_id: str,
    org_id: str,
) -> bool:
    """Delete a BPO provider."""
    provider = await get_provider_by_id(db, provider_id, org_id)
    if not provider:
        return False

    await db.delete(provider)
    await db.flush()
    return True


# =============================================================================
# BPO Process Functions
# =============================================================================


async def get_processes(
    db: AsyncSession,
    provider_id: str,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[BPOProcess], int]:
    """Get processes for a provider."""
    query = select(BPOProcess).where(BPOProcess.provider_id == provider_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(BPOProcess.process_name).offset(skip).limit(limit)

    result = await db.execute(query)
    processes = list(result.scalars().all())

    return processes, total


async def get_process_by_id(
    db: AsyncSession,
    process_id: str,
    org_id: str,
) -> BPOProcess | None:
    """Get a process by ID with org verification."""
    result = await db.execute(
        select(BPOProcess)
        .join(BPOProvider)
        .where(
            BPOProcess.id == process_id,
            BPOProvider.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def create_process(
    db: AsyncSession,
    provider_id: str,
    process_data: BPOProcessCreate,
) -> BPOProcess:
    """Create a new process for a provider."""
    process = BPOProcess(
        provider_id=provider_id,
        process_name=process_data.process_name,
        description=process_data.description,
        criticality=process_data.criticality,
        data_types=process_data.data_types,
        controls_required=process_data.controls_required,
        volume_per_month=process_data.volume_per_month,
    )

    db.add(process)
    await db.flush()
    await db.refresh(process)
    return process


async def update_process(
    db: AsyncSession,
    process_id: str,
    org_id: str,
    process_data: BPOProcessUpdate,
) -> BPOProcess | None:
    """Update a process."""
    process = await get_process_by_id(db, process_id, org_id)
    if not process:
        return None

    update_data = process_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(process, field, value)

    await db.flush()
    await db.refresh(process)
    return process


async def delete_process(
    db: AsyncSession,
    process_id: str,
    org_id: str,
) -> bool:
    """Delete a process."""
    process = await get_process_by_id(db, process_id, org_id)
    if not process:
        return False

    await db.delete(process)
    await db.flush()
    return True


# =============================================================================
# BPO Control Functions
# =============================================================================


async def get_controls(
    db: AsyncSession,
    process_id: str,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[BPOControl], int]:
    """Get controls for a process."""
    query = select(BPOControl).where(BPOControl.process_id == process_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(BPOControl.control_name).offset(skip).limit(limit)

    result = await db.execute(query)
    controls = list(result.scalars().all())

    return controls, total


async def get_control_by_id(
    db: AsyncSession,
    control_id: str,
    org_id: str,
) -> BPOControl | None:
    """Get a control by ID with org verification."""
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


async def create_control(
    db: AsyncSession,
    process_id: str,
    control_data: BPOControlCreate,
) -> BPOControl:
    """Create a new control for a process."""
    control = BPOControl(
        process_id=process_id,
        control_name=control_data.control_name,
        control_description=control_data.control_description,
        control_type=control_data.control_type,
        control_category=control_data.control_category,
        status=control_data.status,
        evidence=control_data.evidence,
        last_tested_date=control_data.last_tested_date,
        test_result=control_data.test_result,
    )

    db.add(control)
    await db.flush()
    await db.refresh(control)
    return control


async def update_control(
    db: AsyncSession,
    control_id: str,
    org_id: str,
    control_data: BPOControlUpdate,
) -> BPOControl | None:
    """Update a control."""
    control = await get_control_by_id(db, control_id, org_id)
    if not control:
        return None

    update_data = control_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(control, field, value)

    await db.flush()
    await db.refresh(control)
    return control


async def delete_control(
    db: AsyncSession,
    control_id: str,
    org_id: str,
) -> bool:
    """Delete a control."""
    control = await get_control_by_id(db, control_id, org_id)
    if not control:
        return False

    await db.delete(control)
    await db.flush()
    return True


# =============================================================================
# BPO Assessment Functions
# =============================================================================


async def get_assessments(
    db: AsyncSession,
    org_id: str,
    skip: int = 0,
    limit: int = 20,
    provider_id: str | None = None,
    status: str | None = None,
) -> tuple[list[BPOAssessment], int]:
    """List assessments with pagination and filtering."""
    query = select(BPOAssessment).where(BPOAssessment.organization_id == org_id)

    if provider_id:
        query = query.where(BPOAssessment.provider_id == provider_id)
    if status:
        query = query.where(BPOAssessment.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(BPOAssessment.assessment_date.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    assessments = list(result.scalars().all())

    return assessments, total


async def get_assessment_by_id(
    db: AsyncSession,
    assessment_id: str,
    org_id: str,
) -> BPOAssessment | None:
    """Get an assessment by ID."""
    result = await db.execute(
        select(BPOAssessment).where(
            BPOAssessment.id == assessment_id,
            BPOAssessment.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def create_assessment(
    db: AsyncSession,
    org_id: str,
    assessment_data: BPOAssessmentCreate,
    created_by: str,
) -> BPOAssessment:
    """Create a new assessment."""
    assessment = BPOAssessment(
        organization_id=org_id,
        provider_id=assessment_data.provider_id,
        assessor_id=created_by,
        assessment_type=assessment_data.assessment_type,
        status=AssessmentStatus.SCHEDULED.value,
        assessment_date=assessment_data.assessment_date,
        overall_score=assessment_data.overall_score,
        findings=assessment_data.findings,
        recommendations=assessment_data.recommendations,
        next_review_date=assessment_data.next_review_date,
    )

    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)
    return assessment


async def update_assessment(
    db: AsyncSession,
    assessment_id: str,
    org_id: str,
    assessment_data: BPOAssessmentUpdate,
    updated_by: str,
) -> BPOAssessment | None:
    """Update an assessment."""
    assessment = await get_assessment_by_id(db, assessment_id, org_id)
    if not assessment:
        return None

    update_data = assessment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assessment, field, value)

    await db.flush()
    await db.refresh(assessment)
    return assessment


# =============================================================================
# BPO Dashboard Stats
# =============================================================================


async def get_dashboard_stats(
    db: AsyncSession,
    org_id: str,
) -> BPODashboardStats:
    """Get BPO dashboard statistics."""
    today = date.today()
    month_start = today.replace(day=1)
    next_30_days = today + timedelta(days=30)

    # Provider counts
    providers_result = await db.execute(
        select(func.count()).where(BPOProvider.organization_id == org_id)
    )
    total_providers = providers_result.scalar() or 0

    # All providers are considered active (no is_active column)
    active_providers = total_providers

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
            BPOProcess.criticality == ProcessCriticality.CRITICAL.value,
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

    completed_result = await db.execute(
        select(func.count()).where(
            BPOAssessment.organization_id == org_id,
            BPOAssessment.status == AssessmentStatus.COMPLETED.value,
        )
    )
    assessments_completed_this_month = completed_result.scalar() or 0

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

    # Providers by service type
    service_type_result = await db.execute(
        select(BPOProvider.service_type, func.count())
        .where(BPOProvider.organization_id == org_id)
        .group_by(BPOProvider.service_type)
    )
    providers_by_service_type = {
        row[0]: row[1] for row in service_type_result.fetchall()
    }

    # Providers by data access level (using as criticality proxy)
    criticality_result = await db.execute(
        select(BPOProvider.data_access_level, func.count())
        .where(BPOProvider.organization_id == org_id)
        .group_by(BPOProvider.data_access_level)
    )
    providers_by_criticality = {
        row[0]: row[1] for row in criticality_result.fetchall()
    }

    # Upcoming assessments
    upcoming_result = await db.execute(
        select(func.count()).where(
            BPOAssessment.organization_id == org_id,
            BPOAssessment.status == AssessmentStatus.SCHEDULED.value,
        )
    )
    upcoming_assessments = upcoming_result.scalar() or 0

    # Contracts expiring soon
    contracts_expiring_result = await db.execute(
        select(func.count()).where(
            BPOProvider.organization_id == org_id,
            BPOProvider.contract_end_date.isnot(None),
            BPOProvider.contract_end_date <= next_30_days,
            BPOProvider.contract_end_date >= today,
        )
    )
    contracts_expiring_soon = contracts_expiring_result.scalar() or 0

    return BPODashboardStats(
        total_providers=total_providers,
        active_providers=active_providers,
        total_processes=total_processes,
        critical_processes=critical_processes,
        total_assessments=total_assessments,
        assessments_in_progress=assessments_in_progress,
        assessments_overdue=assessments_overdue,
        assessments_completed_this_month=assessments_completed_this_month,
        total_controls=total_controls,
        controls_implemented=controls_implemented,
        controls_partial=controls_partial,
        controls_not_implemented=controls_not_implemented,
        average_risk_score=None,
        providers_by_service_type=providers_by_service_type,
        providers_by_criticality=providers_by_criticality,
        upcoming_assessments=upcoming_assessments,
        contracts_expiring_soon=contracts_expiring_soon,
    )
