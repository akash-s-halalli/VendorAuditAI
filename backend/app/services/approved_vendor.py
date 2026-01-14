"""Approved AI Vendor Registry service layer.

Provides business logic for managing the self-service approved vendor registry,
including vendor approvals, use cases, deployments, and tool requests.
"""

from datetime import datetime

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.approved_vendor import (
    ApprovedAIVendor,
    ApprovedUseCase,
    VendorDeployment,
    AIToolRequest,
    ApprovalStatus,
    DeploymentStatus,
    RequestStatus,
)


# =============================================================================
# ApprovedAIVendor CRUD Operations
# =============================================================================


async def get_approved_vendors(
    db: AsyncSession,
    org_id: str,
    status: str | None = None,
    department: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[ApprovedAIVendor], int]:
    """List approved vendors with filtering and pagination.

    Args:
        db: Database session
        org_id: Organization ID for multi-tenant isolation
        status: Filter by approval status (optional)
        department: Filter by approved department (optional)
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of approved vendors, total count)
    """
    query = select(ApprovedAIVendor).where(
        ApprovedAIVendor.organization_id == org_id
    )

    if status:
        query = query.where(ApprovedAIVendor.approval_status == status)

    if department:
        # Filter where department is in the approved_departments JSON array
        query = query.where(
            ApprovedAIVendor.approved_departments.contains([department])
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering with eager loading
    query = (
        query
        .options(selectinload(ApprovedAIVendor.vendor))
        .options(selectinload(ApprovedAIVendor.use_cases))
        .order_by(ApprovedAIVendor.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    vendors = list(result.scalars().all())

    return vendors, total


async def get_approved_vendor(
    db: AsyncSession,
    approved_vendor_id: str,
    org_id: str,
) -> ApprovedAIVendor | None:
    """Get a single approved vendor by ID.

    Args:
        db: Database session
        approved_vendor_id: Approved vendor UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        ApprovedAIVendor if found, None otherwise
    """
    result = await db.execute(
        select(ApprovedAIVendor)
        .options(selectinload(ApprovedAIVendor.vendor))
        .options(selectinload(ApprovedAIVendor.use_cases))
        .options(selectinload(ApprovedAIVendor.deployments))
        .where(
            and_(
                ApprovedAIVendor.id == approved_vendor_id,
                ApprovedAIVendor.organization_id == org_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def get_approved_vendor_by_vendor_id(
    db: AsyncSession,
    vendor_id: str,
    org_id: str,
) -> ApprovedAIVendor | None:
    """Get approved vendor entry by the linked vendor ID.

    Args:
        db: Database session
        vendor_id: Original vendor UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        ApprovedAIVendor if found, None otherwise
    """
    result = await db.execute(
        select(ApprovedAIVendor)
        .options(selectinload(ApprovedAIVendor.vendor))
        .options(selectinload(ApprovedAIVendor.use_cases))
        .where(
            and_(
                ApprovedAIVendor.vendor_id == vendor_id,
                ApprovedAIVendor.organization_id == org_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def create_approved_vendor(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    data: dict,
) -> ApprovedAIVendor:
    """Create a new approved vendor entry.

    Args:
        db: Database session
        org_id: Organization ID
        user_id: User ID who is approving
        data: Approved vendor data including:
            - vendor_id: Required - linked vendor UUID
            - approval_status: Default "pending"
            - expiration_date: Optional
            - approved_departments: Optional list
            - approved_use_cases: Optional list
            - prohibited_uses: Optional list
            - data_classification_limit: Default "internal"
            - conditions: Optional text
            - required_settings: Optional dict
            - required_training: Default False
            - training_url: Optional
            - review_notes: Optional
            - risk_score: Optional
            - max_deployment_count: Optional

    Returns:
        Created ApprovedAIVendor

    Raises:
        ValueError: If vendor_id is already in the approved registry
    """
    # Check for existing approved entry for this vendor
    existing = await get_approved_vendor_by_vendor_id(db, data["vendor_id"], org_id)
    if existing:
        raise ValueError("Vendor is already in the approved registry")

    # Determine approval date based on status
    approval_date = None
    approved_by_id = None
    status = data.get("approval_status", ApprovalStatus.PENDING.value)

    if status in [ApprovalStatus.APPROVED.value, ApprovalStatus.CONDITIONAL.value]:
        approval_date = datetime.utcnow()
        approved_by_id = user_id

    approved_vendor = ApprovedAIVendor(
        vendor_id=data["vendor_id"],
        organization_id=org_id,
        approval_status=status,
        approval_date=approval_date,
        expiration_date=data.get("expiration_date"),
        approved_by_id=approved_by_id,
        approved_departments=data.get("approved_departments"),
        approved_use_cases=data.get("approved_use_cases"),
        prohibited_uses=data.get("prohibited_uses"),
        data_classification_limit=data.get("data_classification_limit", "internal"),
        conditions=data.get("conditions"),
        required_settings=data.get("required_settings"),
        required_training=data.get("required_training", False),
        training_url=data.get("training_url"),
        review_notes=data.get("review_notes"),
        risk_score=data.get("risk_score"),
        max_deployment_count=data.get("max_deployment_count"),
    )

    db.add(approved_vendor)
    await db.flush()
    await db.refresh(approved_vendor)
    return approved_vendor


async def update_approved_vendor(
    db: AsyncSession,
    approved_vendor_id: str,
    org_id: str,
    data: dict,
) -> ApprovedAIVendor | None:
    """Update an approved vendor entry.

    Args:
        db: Database session
        approved_vendor_id: Approved vendor UUID
        org_id: Organization ID for multi-tenant isolation
        data: Fields to update

    Returns:
        Updated ApprovedAIVendor or None if not found
    """
    approved_vendor = await get_approved_vendor(db, approved_vendor_id, org_id)
    if not approved_vendor:
        return None

    # Track if status is being changed to approved
    old_status = approved_vendor.approval_status
    new_status = data.get("approval_status", old_status)

    # Update approval date if status is changing to approved
    if old_status != new_status and new_status in [
        ApprovalStatus.APPROVED.value,
        ApprovalStatus.CONDITIONAL.value,
    ]:
        data["approval_date"] = datetime.utcnow()

    # Apply updates
    allowed_fields = [
        "approval_status",
        "approval_date",
        "expiration_date",
        "approved_by_id",
        "approved_departments",
        "approved_use_cases",
        "prohibited_uses",
        "data_classification_limit",
        "conditions",
        "required_settings",
        "required_training",
        "training_url",
        "review_notes",
        "risk_score",
        "max_deployment_count",
    ]

    for field in allowed_fields:
        if field in data:
            setattr(approved_vendor, field, data[field])

    await db.flush()
    await db.refresh(approved_vendor)
    return approved_vendor


async def delete_approved_vendor(
    db: AsyncSession,
    approved_vendor_id: str,
    org_id: str,
) -> bool:
    """Delete an approved vendor entry.

    This will cascade delete all associated use cases and deployments.

    Args:
        db: Database session
        approved_vendor_id: Approved vendor UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        True if deleted, False if not found
    """
    approved_vendor = await get_approved_vendor(db, approved_vendor_id, org_id)
    if not approved_vendor:
        return False

    await db.delete(approved_vendor)
    await db.flush()
    return True


# =============================================================================
# Use Case Operations
# =============================================================================


async def add_use_case(
    db: AsyncSession,
    approved_vendor_id: str,
    org_id: str,
    data: dict,
) -> ApprovedUseCase | None:
    """Add a use case to an approved vendor.

    Args:
        db: Database session
        approved_vendor_id: Approved vendor UUID
        org_id: Organization ID for multi-tenant isolation
        data: Use case data including:
            - use_case_name: Required
            - description: Optional
            - data_types_allowed: Optional list
            - restrictions: Optional text
            - example_prompts: Optional list
            - prohibited_actions: Optional list

    Returns:
        Created ApprovedUseCase or None if approved vendor not found
    """
    # Verify approved vendor exists and belongs to organization
    approved_vendor = await get_approved_vendor(db, approved_vendor_id, org_id)
    if not approved_vendor:
        return None

    use_case = ApprovedUseCase(
        approved_vendor_id=approved_vendor_id,
        use_case_name=data["use_case_name"],
        description=data.get("description"),
        data_types_allowed=data.get("data_types_allowed"),
        restrictions=data.get("restrictions"),
        example_prompts=data.get("example_prompts"),
        prohibited_actions=data.get("prohibited_actions"),
    )

    db.add(use_case)
    await db.flush()
    await db.refresh(use_case)
    return use_case


async def remove_use_case(
    db: AsyncSession,
    use_case_id: str,
    org_id: str,
) -> bool:
    """Remove a use case from an approved vendor.

    Args:
        db: Database session
        use_case_id: Use case UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        True if deleted, False if not found
    """
    # Join to verify organization ownership
    result = await db.execute(
        select(ApprovedUseCase)
        .join(ApprovedAIVendor)
        .where(
            and_(
                ApprovedUseCase.id == use_case_id,
                ApprovedAIVendor.organization_id == org_id,
            )
        )
    )
    use_case = result.scalar_one_or_none()

    if not use_case:
        return False

    await db.delete(use_case)
    await db.flush()
    return True


# =============================================================================
# Deployment Operations (Self-Service)
# =============================================================================


async def create_deployment(
    db: AsyncSession,
    approved_vendor_id: str,
    org_id: str,
    user_id: str,
    data: dict,
) -> VendorDeployment | None:
    """Create a new deployment for an approved vendor.

    Args:
        db: Database session
        approved_vendor_id: Approved vendor UUID
        org_id: Organization ID
        user_id: User ID creating the deployment
        data: Deployment data including:
            - department: Optional
            - team: Optional
            - use_case: Optional
            - configuration: Optional dict
            - data_classification: Default "internal"
            - notes: Optional

    Returns:
        Created VendorDeployment or None if approved vendor not found

    Raises:
        ValueError: If max deployment count exceeded or vendor not approved
    """
    # Get approved vendor with deployments for count check
    approved_vendor = await get_approved_vendor(db, approved_vendor_id, org_id)
    if not approved_vendor:
        return None

    # Verify vendor is approved
    if approved_vendor.approval_status not in [
        ApprovalStatus.APPROVED.value,
        ApprovalStatus.CONDITIONAL.value,
    ]:
        raise ValueError("Cannot deploy vendor that is not approved")

    # Check expiration
    if approved_vendor.expiration_date and approved_vendor.expiration_date < datetime.utcnow():
        raise ValueError("Vendor approval has expired")

    # Check max deployment count
    if approved_vendor.max_deployment_count:
        active_deployments = len([
            d for d in approved_vendor.deployments
            if d.status in [DeploymentStatus.ACTIVE.value, DeploymentStatus.PENDING_APPROVAL.value]
        ])
        if active_deployments >= approved_vendor.max_deployment_count:
            raise ValueError("Maximum deployment count reached for this vendor")

    # Check department restriction
    department = data.get("department")
    if department and approved_vendor.approved_departments:
        if department not in approved_vendor.approved_departments:
            raise ValueError(f"Department '{department}' is not approved for this vendor")

    # Determine initial status
    initial_status = DeploymentStatus.ACTIVE.value
    activated_at = datetime.utcnow()

    # If conditional approval, require manual approval
    if approved_vendor.approval_status == ApprovalStatus.CONDITIONAL.value:
        initial_status = DeploymentStatus.PENDING_APPROVAL.value
        activated_at = None

    deployment = VendorDeployment(
        approved_vendor_id=approved_vendor_id,
        organization_id=org_id,
        deployed_by_id=user_id,
        department=department,
        team=data.get("team"),
        use_case=data.get("use_case"),
        status=initial_status,
        configuration=data.get("configuration"),
        data_classification=data.get("data_classification", "internal"),
        activated_at=activated_at,
        notes=data.get("notes"),
    )

    db.add(deployment)
    await db.flush()
    await db.refresh(deployment)
    return deployment


async def get_user_deployments(
    db: AsyncSession,
    user_id: str,
    org_id: str,
) -> list[VendorDeployment]:
    """Get all deployments created by a specific user.

    Args:
        db: Database session
        user_id: User ID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        List of VendorDeployment for the user
    """
    result = await db.execute(
        select(VendorDeployment)
        .options(selectinload(VendorDeployment.approved_vendor))
        .where(
            and_(
                VendorDeployment.deployed_by_id == user_id,
                VendorDeployment.organization_id == org_id,
            )
        )
        .order_by(VendorDeployment.created_at.desc())
    )
    return list(result.scalars().all())


async def get_all_deployments(
    db: AsyncSession,
    org_id: str,
    approved_vendor_id: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[VendorDeployment], int]:
    """Get all deployments with filtering and pagination.

    Args:
        db: Database session
        org_id: Organization ID for multi-tenant isolation
        approved_vendor_id: Filter by approved vendor (optional)
        status: Filter by deployment status (optional)
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of deployments, total count)
    """
    query = select(VendorDeployment).where(
        VendorDeployment.organization_id == org_id
    )

    if approved_vendor_id:
        query = query.where(VendorDeployment.approved_vendor_id == approved_vendor_id)

    if status:
        query = query.where(VendorDeployment.status == status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and eager loading
    query = (
        query
        .options(selectinload(VendorDeployment.approved_vendor))
        .options(selectinload(VendorDeployment.deployed_by))
        .order_by(VendorDeployment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    deployments = list(result.scalars().all())

    return deployments, total


async def update_deployment_status(
    db: AsyncSession,
    deployment_id: str,
    org_id: str,
    status: str,
) -> VendorDeployment | None:
    """Update a deployment's status.

    Args:
        db: Database session
        deployment_id: Deployment UUID
        org_id: Organization ID for multi-tenant isolation
        status: New status value

    Returns:
        Updated VendorDeployment or None if not found
    """
    result = await db.execute(
        select(VendorDeployment).where(
            and_(
                VendorDeployment.id == deployment_id,
                VendorDeployment.organization_id == org_id,
            )
        )
    )
    deployment = result.scalar_one_or_none()

    if not deployment:
        return None

    deployment.status = status

    # Update activation timestamp if being activated
    if status == DeploymentStatus.ACTIVE.value and not deployment.activated_at:
        deployment.activated_at = datetime.utcnow()

    # Update deactivation timestamp if being deactivated
    if status in [DeploymentStatus.INACTIVE.value, DeploymentStatus.SUSPENDED.value]:
        deployment.deactivated_at = datetime.utcnow()

    await db.flush()
    await db.refresh(deployment)
    return deployment


async def deactivate_deployment(
    db: AsyncSession,
    deployment_id: str,
    org_id: str,
) -> bool:
    """Deactivate a deployment (soft delete).

    Args:
        db: Database session
        deployment_id: Deployment UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        True if deactivated, False if not found
    """
    deployment = await update_deployment_status(
        db, deployment_id, org_id, DeploymentStatus.INACTIVE.value
    )
    return deployment is not None


# =============================================================================
# Tool Request Operations
# =============================================================================


async def create_tool_request(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    data: dict,
) -> AIToolRequest:
    """Create a new AI tool request.

    Args:
        db: Database session
        org_id: Organization ID
        user_id: User ID submitting the request
        data: Request data including:
            - vendor_name: Required
            - vendor_website: Optional
            - tool_description: Optional
            - use_case_description: Optional
            - department: Optional
            - business_justification: Optional
            - expected_data_types: Optional list
            - urgency: Optional ("low", "medium", "high", "critical")

    Returns:
        Created AIToolRequest
    """
    request = AIToolRequest(
        organization_id=org_id,
        requested_by_id=user_id,
        vendor_name=data["vendor_name"],
        vendor_website=data.get("vendor_website"),
        tool_description=data.get("tool_description"),
        use_case_description=data.get("use_case_description"),
        department=data.get("department"),
        business_justification=data.get("business_justification"),
        expected_data_types=data.get("expected_data_types"),
        urgency=data.get("urgency"),
        status=RequestStatus.SUBMITTED.value,
    )

    db.add(request)
    await db.flush()
    await db.refresh(request)
    return request


async def get_tool_requests(
    db: AsyncSession,
    org_id: str,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[AIToolRequest], int]:
    """Get all tool requests with filtering and pagination.

    Args:
        db: Database session
        org_id: Organization ID for multi-tenant isolation
        status: Filter by request status (optional)
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of requests, total count)
    """
    query = select(AIToolRequest).where(
        AIToolRequest.organization_id == org_id
    )

    if status:
        query = query.where(AIToolRequest.status == status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and eager loading
    query = (
        query
        .options(selectinload(AIToolRequest.requested_by))
        .options(selectinload(AIToolRequest.assigned_reviewer))
        .order_by(AIToolRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    requests = list(result.scalars().all())

    return requests, total


async def get_user_requests(
    db: AsyncSession,
    user_id: str,
    org_id: str,
) -> list[AIToolRequest]:
    """Get all tool requests submitted by a specific user.

    Args:
        db: Database session
        user_id: User ID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        List of AIToolRequest for the user
    """
    result = await db.execute(
        select(AIToolRequest)
        .where(
            and_(
                AIToolRequest.requested_by_id == user_id,
                AIToolRequest.organization_id == org_id,
            )
        )
        .order_by(AIToolRequest.created_at.desc())
    )
    return list(result.scalars().all())


async def update_request_status(
    db: AsyncSession,
    request_id: str,
    org_id: str,
    reviewer_id: str,
    status: str,
    notes: str | None = None,
) -> AIToolRequest | None:
    """Update a tool request's status.

    Args:
        db: Database session
        request_id: Request UUID
        org_id: Organization ID for multi-tenant isolation
        reviewer_id: User ID of the reviewer
        status: New status value
        notes: Optional review notes

    Returns:
        Updated AIToolRequest or None if not found
    """
    result = await db.execute(
        select(AIToolRequest).where(
            and_(
                AIToolRequest.id == request_id,
                AIToolRequest.organization_id == org_id,
            )
        )
    )
    request = result.scalar_one_or_none()

    if not request:
        return None

    request.status = status
    request.assigned_reviewer_id = reviewer_id

    if notes:
        request.review_notes = notes

    # Set decision date for final statuses
    if status in [RequestStatus.APPROVED.value, RequestStatus.REJECTED.value]:
        request.decision_date = datetime.utcnow()

    await db.flush()
    await db.refresh(request)
    return request


# =============================================================================
# Dashboard Statistics
# =============================================================================


async def get_approved_vendor_stats(
    db: AsyncSession,
    org_id: str,
) -> dict:
    """Get dashboard statistics for approved vendors.

    Args:
        db: Database session
        org_id: Organization ID for multi-tenant isolation

    Returns:
        Dictionary with counts and statistics:
        - total_approved_vendors: Total count of approved vendors
        - vendors_by_status: Dict of status -> count
        - total_deployments: Total deployment count
        - active_deployments: Active deployment count
        - pending_requests: Pending tool request count
        - deployments_by_department: Dict of department -> count
    """
    stats = {}

    # Count approved vendors by status
    vendor_status_result = await db.execute(
        select(
            ApprovedAIVendor.approval_status,
            func.count(ApprovedAIVendor.id)
        )
        .where(ApprovedAIVendor.organization_id == org_id)
        .group_by(ApprovedAIVendor.approval_status)
    )
    vendors_by_status = {row[0]: row[1] for row in vendor_status_result.all()}
    stats["vendors_by_status"] = vendors_by_status
    stats["total_approved_vendors"] = sum(vendors_by_status.values())

    # Count deployments by status
    deployment_status_result = await db.execute(
        select(
            VendorDeployment.status,
            func.count(VendorDeployment.id)
        )
        .where(VendorDeployment.organization_id == org_id)
        .group_by(VendorDeployment.status)
    )
    deployments_by_status = {row[0]: row[1] for row in deployment_status_result.all()}
    stats["total_deployments"] = sum(deployments_by_status.values())
    stats["active_deployments"] = deployments_by_status.get(DeploymentStatus.ACTIVE.value, 0)
    stats["deployments_by_status"] = deployments_by_status

    # Count deployments by department
    dept_result = await db.execute(
        select(
            VendorDeployment.department,
            func.count(VendorDeployment.id)
        )
        .where(
            and_(
                VendorDeployment.organization_id == org_id,
                VendorDeployment.status == DeploymentStatus.ACTIVE.value,
            )
        )
        .group_by(VendorDeployment.department)
    )
    deployments_by_department = {
        row[0] or "Unassigned": row[1] for row in dept_result.all()
    }
    stats["deployments_by_department"] = deployments_by_department

    # Count pending tool requests
    pending_result = await db.execute(
        select(func.count(AIToolRequest.id))
        .where(
            and_(
                AIToolRequest.organization_id == org_id,
                AIToolRequest.status.in_([
                    RequestStatus.SUBMITTED.value,
                    RequestStatus.UNDER_REVIEW.value,
                    RequestStatus.MORE_INFO_NEEDED.value,
                ]),
            )
        )
    )
    stats["pending_requests"] = pending_result.scalar() or 0

    # Count requests by status
    request_status_result = await db.execute(
        select(
            AIToolRequest.status,
            func.count(AIToolRequest.id)
        )
        .where(AIToolRequest.organization_id == org_id)
        .group_by(AIToolRequest.status)
    )
    stats["requests_by_status"] = {row[0]: row[1] for row in request_status_result.all()}

    return stats
