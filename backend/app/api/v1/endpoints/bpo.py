"""BPO Risk Management API endpoints.

Provides endpoints for managing Business Process Outsourcing (BPO) providers,
their processes, controls, and risk assessments.

Endpoints:
- BPO Providers: CRUD operations for BPO provider management
- Processes: Manage outsourced processes for each provider
- Controls: Define and track risk controls for processes
- Assessments: Conduct and track risk assessments
- Dashboard: Get BPO-specific metrics and statistics
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.schemas.bpo import (
    # Provider schemas
    BPOProviderCreate,
    BPOProviderListResponse,
    BPOProviderResponse,
    BPOProviderUpdate,
    BPOProviderDetailResponse,
    # Process schemas
    BPOProcessCreate,
    BPOProcessResponse,
    BPOProcessUpdate,
    BPOProcessListResponse,
    # Control schemas
    BPOControlCreate,
    BPOControlResponse,
    BPOControlUpdate,
    BPOControlListResponse,
    # Assessment schemas
    BPOAssessmentCreate,
    BPOAssessmentListResponse,
    BPOAssessmentResponse,
    BPOAssessmentUpdate,
    # Dashboard schemas
    BPODashboardStats,
)
from app.services import bpo as bpo_service

router = APIRouter(tags=["BPO Risk Management"])


# =============================================================================
# BPO Provider Endpoints
# =============================================================================


@router.get("/providers", response_model=BPOProviderListResponse)
async def list_providers(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    service_type: str | None = Query(None, description="Filter by service type"),
    search: str | None = Query(None, description="Search by provider name"),
) -> BPOProviderListResponse:
    """
    List all BPO providers for the current user's organization.

    Supports pagination, filtering by service type, and search by name.
    Service types include: IT, Finance, HR, Customer Service, Operations, etc.
    """
    skip = (page - 1) * limit
    providers, total = await bpo_service.get_providers(
        db=db,
        org_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        service_type=service_type,
        search=search,
    )
    return BPOProviderListResponse(
        data=[BPOProviderResponse.model_validate(p) for p in providers],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/providers/{provider_id}", response_model=BPOProviderDetailResponse)
async def get_provider(
    provider_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPOProviderDetailResponse:
    """
    Get a specific BPO provider by ID with all associated processes.

    Returns the provider details along with a list of all outsourced processes,
    including their risk ratings and control status.
    """
    provider = await bpo_service.get_provider_by_id(
        db=db,
        provider_id=provider_id,
        org_id=current_user.organization_id,
        include_processes=True,
    )
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BPO provider not found",
        )
    return BPOProviderDetailResponse.model_validate(provider)


@router.post(
    "/providers",
    response_model=BPOProviderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_provider(
    provider_data: BPOProviderCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPOProviderResponse:
    """
    Create a new BPO provider for the current user's organization.

    Required fields:
    - name: Provider's company name
    - service_type: Type of service provided (IT, Finance, HR, etc.)
    - country: Provider's country of operation

    Optional fields:
    - description: Detailed description of services
    - contract_start_date: When the contract began
    - contract_end_date: When the contract expires
    - risk_tier: Initial risk classification (low, medium, high, critical)
    - contact_email: Primary contact email
    - contact_name: Primary contact person
    """
    try:
        provider = await bpo_service.create_provider(
            db=db,
            org_id=current_user.organization_id,
            provider_data=provider_data,
        )
        return BPOProviderResponse.model_validate(provider)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put("/providers/{provider_id}", response_model=BPOProviderResponse)
async def update_provider(
    provider_id: str,
    provider_data: BPOProviderUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPOProviderResponse:
    """
    Update a BPO provider's information.

    All fields are optional - only provided fields will be updated.
    Use this to update contract dates, risk tier, contact information, etc.
    """
    try:
        provider = await bpo_service.update_provider(
            db=db,
            provider_id=provider_id,
            org_id=current_user.organization_id,
            provider_data=provider_data,
        )
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BPO provider not found",
            )
        return BPOProviderResponse.model_validate(provider)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Delete a BPO provider.

    This will also delete all associated processes, controls, and assessments.
    This action cannot be undone.
    """
    deleted = await bpo_service.delete_provider(
        db=db,
        provider_id=provider_id,
        org_id=current_user.organization_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BPO provider not found",
        )


# =============================================================================
# BPO Process Endpoints
# =============================================================================


@router.get(
    "/providers/{provider_id}/processes",
    response_model=BPOProcessListResponse,
)
async def list_processes(
    provider_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
) -> BPOProcessListResponse:
    """
    List all processes for a specific BPO provider.

    Returns a paginated list of outsourced business processes,
    including their risk ratings and compliance status.
    """
    # Verify provider exists and belongs to organization
    provider = await bpo_service.get_provider_by_id(
        db=db,
        provider_id=provider_id,
        org_id=current_user.organization_id,
    )
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BPO provider not found",
        )

    skip = (page - 1) * limit
    processes, total = await bpo_service.get_processes(
        db=db,
        provider_id=provider_id,
        skip=skip,
        limit=limit,
    )
    return BPOProcessListResponse(
        data=[BPOProcessResponse.model_validate(p) for p in processes],
        total=total,
        page=page,
        limit=limit,
    )


@router.post(
    "/providers/{provider_id}/processes",
    response_model=BPOProcessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_process(
    provider_id: str,
    process_data: BPOProcessCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPOProcessResponse:
    """
    Add a new process to a BPO provider.

    Required fields:
    - name: Process name (e.g., "Payroll Processing", "Customer Support")
    - category: Process category (e.g., "Finance", "HR", "IT")

    Optional fields:
    - description: Detailed process description
    - criticality: Business criticality (low, medium, high, critical)
    - data_classification: Data sensitivity level (public, internal, confidential, restricted)
    - sla_requirements: Service level agreement details
    - regulatory_requirements: Applicable regulations (SOC2, GDPR, HIPAA, etc.)
    """
    # Verify provider exists and belongs to organization
    provider = await bpo_service.get_provider_by_id(
        db=db,
        provider_id=provider_id,
        org_id=current_user.organization_id,
    )
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BPO provider not found",
        )

    try:
        process = await bpo_service.create_process(
            db=db,
            provider_id=provider_id,
            process_data=process_data,
        )
        return BPOProcessResponse.model_validate(process)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put("/processes/{process_id}", response_model=BPOProcessResponse)
async def update_process(
    process_id: str,
    process_data: BPOProcessUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPOProcessResponse:
    """
    Update a BPO process.

    All fields are optional - only provided fields will be updated.
    """
    try:
        process = await bpo_service.update_process(
            db=db,
            process_id=process_id,
            org_id=current_user.organization_id,
            process_data=process_data,
        )
        if not process:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BPO process not found",
            )
        return BPOProcessResponse.model_validate(process)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/processes/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_process(
    process_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Delete a BPO process.

    This will also delete all associated controls.
    This action cannot be undone.
    """
    deleted = await bpo_service.delete_process(
        db=db,
        process_id=process_id,
        org_id=current_user.organization_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BPO process not found",
        )


# =============================================================================
# BPO Control Endpoints
# =============================================================================


@router.get(
    "/processes/{process_id}/controls",
    response_model=BPOControlListResponse,
)
async def list_controls(
    process_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> BPOControlListResponse:
    """
    List all controls for a specific BPO process.

    Returns a paginated list of risk controls defined for the process,
    including their implementation status and effectiveness ratings.
    """
    # Verify process exists and belongs to organization
    process = await bpo_service.get_process_by_id(
        db=db,
        process_id=process_id,
        org_id=current_user.organization_id,
    )
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BPO process not found",
        )

    skip = (page - 1) * limit
    controls, total = await bpo_service.get_controls(
        db=db,
        process_id=process_id,
        skip=skip,
        limit=limit,
    )
    return BPOControlListResponse(
        data=[BPOControlResponse.model_validate(c) for c in controls],
        total=total,
        page=page,
        limit=limit,
    )


@router.post(
    "/processes/{process_id}/controls",
    response_model=BPOControlResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_control(
    process_id: str,
    control_data: BPOControlCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPOControlResponse:
    """
    Add a new control to a BPO process.

    Required fields:
    - name: Control name (e.g., "Access Review", "Encryption at Rest")
    - control_type: Type of control (preventive, detective, corrective)
    - category: Control category (access, data, operational, compliance)

    Optional fields:
    - description: Detailed control description
    - implementation_status: Current status (not_started, in_progress, implemented, verified)
    - effectiveness: Effectiveness rating (not_tested, ineffective, partially_effective, effective)
    - owner: Person responsible for the control
    - evidence_requirements: Required evidence for verification
    - test_frequency: How often the control should be tested
    - last_tested_date: When the control was last tested
    - next_test_date: When the control should next be tested
    """
    # Verify process exists and belongs to organization
    process = await bpo_service.get_process_by_id(
        db=db,
        process_id=process_id,
        org_id=current_user.organization_id,
    )
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BPO process not found",
        )

    try:
        control = await bpo_service.create_control(
            db=db,
            process_id=process_id,
            control_data=control_data,
        )
        return BPOControlResponse.model_validate(control)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put("/controls/{control_id}", response_model=BPOControlResponse)
async def update_control(
    control_id: str,
    control_data: BPOControlUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPOControlResponse:
    """
    Update a BPO control.

    All fields are optional - only provided fields will be updated.
    Use this to update implementation status, effectiveness ratings,
    test dates, and other control attributes.
    """
    try:
        control = await bpo_service.update_control(
            db=db,
            control_id=control_id,
            org_id=current_user.organization_id,
            control_data=control_data,
        )
        if not control:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BPO control not found",
            )
        return BPOControlResponse.model_validate(control)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/controls/{control_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_control(
    control_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Delete a BPO control.

    This action cannot be undone.
    """
    deleted = await bpo_service.delete_control(
        db=db,
        control_id=control_id,
        org_id=current_user.organization_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BPO control not found",
        )


# =============================================================================
# BPO Assessment Endpoints
# =============================================================================


@router.get("/assessments", response_model=BPOAssessmentListResponse)
async def list_assessments(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    provider_id: str | None = Query(None, description="Filter by provider ID"),
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by status (draft, in_progress, completed, approved)",
    ),
) -> BPOAssessmentListResponse:
    """
    List all BPO risk assessments for the organization.

    Supports filtering by:
    - provider_id: Show assessments for a specific provider
    - status: Filter by assessment status (draft, in_progress, completed, approved)

    Returns assessments sorted by most recent first.
    """
    skip = (page - 1) * limit
    assessments, total = await bpo_service.get_assessments(
        db=db,
        org_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        provider_id=provider_id,
        status=status_filter,
    )
    return BPOAssessmentListResponse(
        data=[BPOAssessmentResponse.model_validate(a) for a in assessments],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/assessments/{assessment_id}", response_model=BPOAssessmentResponse)
async def get_assessment(
    assessment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPOAssessmentResponse:
    """
    Get a specific BPO risk assessment by ID.

    Returns the full assessment details including:
    - Assessment metadata (dates, status, assessor)
    - Risk ratings for each area
    - Findings and recommendations
    - Control effectiveness evaluations
    - Action items and remediation status
    """
    assessment = await bpo_service.get_assessment_by_id(
        db=db,
        assessment_id=assessment_id,
        org_id=current_user.organization_id,
    )
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BPO assessment not found",
        )
    return BPOAssessmentResponse.model_validate(assessment)


@router.post(
    "/assessments",
    response_model=BPOAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assessment(
    assessment_data: BPOAssessmentCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPOAssessmentResponse:
    """
    Create a new BPO risk assessment.

    Required fields:
    - provider_id: The BPO provider being assessed
    - assessment_type: Type of assessment (initial, periodic, triggered, follow_up)
    - assessment_date: Date of the assessment

    Optional fields:
    - assessor_name: Name of the person conducting the assessment
    - scope: Assessment scope and boundaries
    - methodology: Assessment methodology used
    - overall_risk_rating: Overall risk rating (low, medium, high, critical)
    - findings: List of assessment findings
    - recommendations: List of recommendations
    - next_assessment_date: Scheduled date for next assessment
    """
    # Verify provider exists and belongs to organization
    provider = await bpo_service.get_provider_by_id(
        db=db,
        provider_id=assessment_data.provider_id,
        org_id=current_user.organization_id,
    )
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BPO provider not found",
        )

    try:
        assessment = await bpo_service.create_assessment(
            db=db,
            org_id=current_user.organization_id,
            assessment_data=assessment_data,
            created_by=current_user.id,
        )
        return BPOAssessmentResponse.model_validate(assessment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put("/assessments/{assessment_id}", response_model=BPOAssessmentResponse)
async def update_assessment(
    assessment_id: str,
    assessment_data: BPOAssessmentUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPOAssessmentResponse:
    """
    Update a BPO risk assessment.

    All fields are optional - only provided fields will be updated.
    Use this to:
    - Update assessment status (draft -> in_progress -> completed -> approved)
    - Add or update findings and recommendations
    - Update risk ratings
    - Schedule the next assessment
    """
    try:
        assessment = await bpo_service.update_assessment(
            db=db,
            assessment_id=assessment_id,
            org_id=current_user.organization_id,
            assessment_data=assessment_data,
            updated_by=current_user.id,
        )
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BPO assessment not found",
            )
        return BPOAssessmentResponse.model_validate(assessment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# =============================================================================
# BPO Dashboard Endpoint
# =============================================================================


@router.get("/dashboard", response_model=BPODashboardStats)
async def get_bpo_dashboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BPODashboardStats:
    """
    Get BPO risk management dashboard statistics.

    Returns comprehensive metrics including:
    - Total provider count by service type
    - Total process count by category
    - Risk tier distribution (providers and processes)
    - Control implementation status summary
    - Control effectiveness breakdown
    - Assessment status summary
    - Upcoming assessment deadlines
    - High-risk items requiring attention
    - Trend data for risk metrics
    """
    return await bpo_service.get_dashboard_stats(
        db=db,
        org_id=current_user.organization_id,
    )
