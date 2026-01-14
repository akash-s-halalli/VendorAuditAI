"""Approved AI Vendor Registry API endpoints.

Provides self-service access to pre-approved AI vendors, use case management,
self-service deployments, and tool evaluation requests.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_current_admin_user
from app.db import get_db
from app.models import User
from app.models.audit_log import AuditAction
from app.schemas.approved_vendor import (
    ApprovedVendorCreate,
    ApprovedVendorDetailResponse,
    ApprovedVendorListResponse,
    ApprovedVendorResponse,
    ApprovedVendorStats,
    ApprovedVendorUpdate,
    DeploymentCreate,
    DeploymentListResponse,
    DeploymentResponse,
    DeploymentStatus,
    ToolRequestCreate,
    ToolRequestListResponse,
    ToolRequestResponse,
    ToolRequestUpdate,
    UseCaseCreate,
    UseCaseResponse,
)
from app.services import approved_vendor as approved_vendor_service
from app.services.audit import get_audit_service

router = APIRouter(tags=["Approved Vendors"])


def _get_client_ip(request: Request) -> str | None:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request.client:
        return request.client.host
    return None


def _get_user_agent(request: Request) -> str | None:
    """Extract user agent from request."""
    return request.headers.get("User-Agent")


# =============================================================================
# Approved Vendor CRUD Endpoints
# =============================================================================


@router.get("", response_model=ApprovedVendorListResponse)
async def list_approved_vendors(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = Query(None, description="Filter by approval status"),
    department: str | None = Query(None, description="Filter by approved department"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
) -> ApprovedVendorListResponse:
    """
    List all approved AI vendors for the organization.

    Supports filtering by approval status and department.
    Returns paginated results with use case information.
    """
    vendors, total = await approved_vendor_service.get_approved_vendors(
        db=db,
        org_id=current_user.organization_id,
        status=status,
        department=department,
        skip=skip,
        limit=limit,
    )

    return ApprovedVendorListResponse(
        data=[ApprovedVendorResponse.model_validate(v) for v in vendors],
        total=total,
    )


@router.get("/stats", response_model=ApprovedVendorStats)
async def get_approved_vendor_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApprovedVendorStats:
    """
    Get summary statistics for the approved vendor registry.

    Returns counts for vendors by status, deployments by department,
    pending requests, and other key metrics.
    """
    stats = await approved_vendor_service.get_approved_vendor_stats(
        db=db,
        org_id=current_user.organization_id,
    )

    return ApprovedVendorStats(
        total_approved_vendors=stats.get("total_approved_vendors", 0),
        total_pending_approval=stats.get("vendors_by_status", {}).get("pending", 0),
        total_conditional_approval=stats.get("vendors_by_status", {}).get("conditional", 0),
        total_expired=stats.get("vendors_by_status", {}).get("expired", 0),
        total_active_deployments=stats.get("active_deployments", 0),
        total_pending_requests=stats.get("pending_requests", 0),
        deployments_by_department=stats.get("deployments_by_department", {}),
        vendors_by_classification=stats.get("vendors_by_classification", {}),
        expiring_soon=stats.get("expiring_soon", 0),
    )


@router.get("/my-deployments", response_model=list[DeploymentResponse])
async def get_my_deployments(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[DeploymentResponse]:
    """
    Get all deployments created by the current user.

    Returns a list of all deployments the user has initiated,
    regardless of their current status.
    """
    deployments = await approved_vendor_service.get_user_deployments(
        db=db,
        user_id=current_user.id,
        org_id=current_user.organization_id,
    )

    return [DeploymentResponse.model_validate(d) for d in deployments]


@router.get("/my-requests", response_model=list[ToolRequestResponse])
async def get_my_requests(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ToolRequestResponse]:
    """
    Get all tool requests submitted by the current user.

    Returns a list of all AI tool evaluation requests the user has
    submitted, including their current status.
    """
    requests = await approved_vendor_service.get_user_requests(
        db=db,
        user_id=current_user.id,
        org_id=current_user.organization_id,
    )

    return [ToolRequestResponse.model_validate(r) for r in requests]


@router.get("/deployments", response_model=DeploymentListResponse)
async def list_all_deployments(
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    approved_vendor_id: str | None = Query(None, description="Filter by approved vendor"),
    status: str | None = Query(None, description="Filter by deployment status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
) -> DeploymentListResponse:
    """
    List all deployments in the organization (admin only).

    Supports filtering by approved vendor ID and deployment status.
    Returns paginated results with deployment details.
    """
    deployments, total = await approved_vendor_service.get_all_deployments(
        db=db,
        org_id=current_user.organization_id,
        approved_vendor_id=approved_vendor_id,
        status=status,
        skip=skip,
        limit=limit,
    )

    return DeploymentListResponse(
        data=[DeploymentResponse.model_validate(d) for d in deployments],
        total=total,
    )


@router.get("/requests", response_model=ToolRequestListResponse)
async def list_all_requests(
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = Query(None, description="Filter by request status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
) -> ToolRequestListResponse:
    """
    List all tool requests in the organization (admin only).

    Supports filtering by request status.
    Returns paginated results with request details.
    """
    requests, total = await approved_vendor_service.get_tool_requests(
        db=db,
        org_id=current_user.organization_id,
        status=status,
        skip=skip,
        limit=limit,
    )

    return ToolRequestListResponse(
        data=[ToolRequestResponse.model_validate(r) for r in requests],
        total=total,
    )


@router.get("/{approved_vendor_id}", response_model=ApprovedVendorDetailResponse)
async def get_approved_vendor(
    approved_vendor_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApprovedVendorDetailResponse:
    """
    Get a specific approved vendor by ID.

    Returns detailed information including use cases, deployment
    restrictions, and approval conditions.
    """
    vendor = await approved_vendor_service.get_approved_vendor(
        db=db,
        approved_vendor_id=approved_vendor_id,
        org_id=current_user.organization_id,
    )

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approved vendor not found",
        )

    # Convert use cases
    use_cases = [UseCaseResponse.model_validate(uc) for uc in vendor.use_cases]

    response_data = ApprovedVendorDetailResponse.model_validate(vendor)
    response_data.use_cases = use_cases

    return response_data


@router.post("", response_model=ApprovedVendorResponse, status_code=status.HTTP_201_CREATED)
async def create_approved_vendor(
    request: Request,
    vendor_data: ApprovedVendorCreate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApprovedVendorResponse:
    """
    Add a vendor to the approved AI vendor registry (admin only).

    Creates a new approved vendor entry linked to an existing vendor.
    Sets approval status, restrictions, and conditions.
    """
    try:
        vendor = await approved_vendor_service.create_approved_vendor(
            db=db,
            org_id=current_user.organization_id,
            user_id=current_user.id,
            data=vendor_data.model_dump(exclude_unset=True),
        )

        # Log the creation
        audit_service = get_audit_service(db)
        await audit_service.log_action(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            action=AuditAction.CREATE,
            resource_type="approved_vendor",
            resource_id=vendor.id,
            new_values={
                "vendor_id": vendor.vendor_id,
                "approval_status": vendor.approval_status,
                "data_classification_limit": vendor.data_classification_limit,
            },
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details=f"Added vendor to approved registry: {vendor.vendor_id}",
        )
        await db.commit()
        await db.refresh(vendor)

        return ApprovedVendorResponse.model_validate(vendor)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put("/{approved_vendor_id}", response_model=ApprovedVendorResponse)
async def update_approved_vendor(
    request: Request,
    approved_vendor_id: str,
    vendor_data: ApprovedVendorUpdate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApprovedVendorResponse:
    """
    Update an approved vendor entry (admin only).

    Updates approval status, restrictions, conditions, or other
    settings for an approved vendor.
    """
    # Get old values for audit
    old_vendor = await approved_vendor_service.get_approved_vendor(
        db=db,
        approved_vendor_id=approved_vendor_id,
        org_id=current_user.organization_id,
    )

    if not old_vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approved vendor not found",
        )

    old_values = {
        "approval_status": old_vendor.approval_status,
        "data_classification_limit": old_vendor.data_classification_limit,
        "conditions": old_vendor.conditions,
    }

    # Include approver ID if status is being set to approved
    update_data = vendor_data.model_dump(exclude_unset=True)
    if update_data.get("approval_status") in ["approved", "conditional"]:
        update_data["approved_by_id"] = current_user.id

    vendor = await approved_vendor_service.update_approved_vendor(
        db=db,
        approved_vendor_id=approved_vendor_id,
        org_id=current_user.organization_id,
        data=update_data,
    )

    # Log the update
    audit_service = get_audit_service(db)
    await audit_service.log_action(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        resource_type="approved_vendor",
        resource_id=approved_vendor_id,
        old_values=old_values,
        new_values=vendor_data.model_dump(exclude_unset=True),
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details=f"Updated approved vendor: {approved_vendor_id}",
    )
    await db.commit()
    await db.refresh(vendor)

    return ApprovedVendorResponse.model_validate(vendor)


@router.delete("/{approved_vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_approved_vendor(
    request: Request,
    approved_vendor_id: str,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Remove a vendor from the approved registry (admin only).

    This will cascade delete all associated use cases and deployments.
    Consider using status update to "rejected" or "expired" instead
    for maintaining history.
    """
    # Get vendor info for audit before deletion
    vendor = await approved_vendor_service.get_approved_vendor(
        db=db,
        approved_vendor_id=approved_vendor_id,
        org_id=current_user.organization_id,
    )

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approved vendor not found",
        )

    old_values = {
        "vendor_id": vendor.vendor_id,
        "approval_status": vendor.approval_status,
    }

    deleted = await approved_vendor_service.delete_approved_vendor(
        db=db,
        approved_vendor_id=approved_vendor_id,
        org_id=current_user.organization_id,
    )

    if deleted:
        # Log the deletion
        audit_service = get_audit_service(db)
        await audit_service.log_action(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            action=AuditAction.DELETE,
            resource_type="approved_vendor",
            resource_id=approved_vendor_id,
            old_values=old_values,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details=f"Removed vendor from approved registry: {vendor.vendor_id}",
        )
        await db.commit()


# =============================================================================
# Use Case Endpoints
# =============================================================================


@router.post("/{approved_vendor_id}/use-cases", response_model=UseCaseResponse, status_code=status.HTTP_201_CREATED)
async def add_use_case(
    request: Request,
    approved_vendor_id: str,
    use_case_data: UseCaseCreate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UseCaseResponse:
    """
    Add a use case to an approved vendor (admin only).

    Defines an approved use case with allowed data types,
    restrictions, example prompts, and prohibited actions.
    """
    use_case = await approved_vendor_service.add_use_case(
        db=db,
        approved_vendor_id=approved_vendor_id,
        org_id=current_user.organization_id,
        data=use_case_data.model_dump(exclude_unset=True),
    )

    if not use_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approved vendor not found",
        )

    # Log the creation
    audit_service = get_audit_service(db)
    await audit_service.log_action(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        resource_type="approved_use_case",
        resource_id=use_case.id,
        new_values={
            "approved_vendor_id": approved_vendor_id,
            "use_case_name": use_case.use_case_name,
        },
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details=f"Added use case '{use_case.use_case_name}' to vendor {approved_vendor_id}",
    )
    await db.commit()
    await db.refresh(use_case)

    return UseCaseResponse.model_validate(use_case)


@router.delete("/use-cases/{use_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_use_case(
    request: Request,
    use_case_id: str,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Remove a use case from an approved vendor (admin only).

    Permanently deletes the use case definition.
    """
    deleted = await approved_vendor_service.remove_use_case(
        db=db,
        use_case_id=use_case_id,
        org_id=current_user.organization_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Use case not found",
        )

    # Log the deletion
    audit_service = get_audit_service(db)
    await audit_service.log_action(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        resource_type="approved_use_case",
        resource_id=use_case_id,
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details=f"Removed use case: {use_case_id}",
    )
    await db.commit()


# =============================================================================
# Deployment Endpoints (Self-Service)
# =============================================================================


@router.post("/{approved_vendor_id}/deploy", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    request: Request,
    approved_vendor_id: str,
    deployment_data: DeploymentCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeploymentResponse:
    """
    Create a self-service deployment of an approved vendor.

    Any user can deploy an approved vendor to their department/team.
    Deployment may require approval if the vendor has conditional status.
    """
    try:
        deployment = await approved_vendor_service.create_deployment(
            db=db,
            approved_vendor_id=approved_vendor_id,
            org_id=current_user.organization_id,
            user_id=current_user.id,
            data=deployment_data.model_dump(exclude_unset=True),
        )

        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approved vendor not found",
            )

        # Log the deployment
        audit_service = get_audit_service(db)
        await audit_service.log_action(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            action=AuditAction.CREATE,
            resource_type="vendor_deployment",
            resource_id=deployment.id,
            new_values={
                "approved_vendor_id": approved_vendor_id,
                "department": deployment.department,
                "team": deployment.team,
                "status": deployment.status,
            },
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details=f"Created deployment for vendor {approved_vendor_id}",
        )
        await db.commit()
        await db.refresh(deployment)

        return DeploymentResponse.model_validate(deployment)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put("/deployments/{deployment_id}/status", response_model=DeploymentResponse)
async def update_deployment_status(
    request: Request,
    deployment_id: str,
    status_value: DeploymentStatus = Query(..., alias="status", description="New deployment status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DeploymentResponse:
    """
    Update a deployment's status (admin only).

    Used to approve pending deployments or suspend/reactivate
    existing deployments.
    """
    deployment = await approved_vendor_service.update_deployment_status(
        db=db,
        deployment_id=deployment_id,
        org_id=current_user.organization_id,
        status=status_value.value,
    )

    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )

    # Log the status change
    audit_service = get_audit_service(db)
    await audit_service.log_action(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGE,
        resource_type="vendor_deployment",
        resource_id=deployment_id,
        new_values={"status": status_value.value},
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details=f"Updated deployment status to {status_value.value}",
    )
    await db.commit()
    await db.refresh(deployment)

    return DeploymentResponse.model_validate(deployment)


@router.delete("/deployments/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_deployment(
    request: Request,
    deployment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Deactivate a deployment (soft delete).

    Users can deactivate their own deployments. Admins can
    deactivate any deployment in the organization.
    """
    # Check if user owns the deployment or is admin
    deployments = await approved_vendor_service.get_user_deployments(
        db=db,
        user_id=current_user.id,
        org_id=current_user.organization_id,
    )

    user_deployment_ids = [d.id for d in deployments]
    is_owner = deployment_id in user_deployment_ids
    is_admin = current_user.role == "admin"

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only deactivate your own deployments",
        )

    deactivated = await approved_vendor_service.deactivate_deployment(
        db=db,
        deployment_id=deployment_id,
        org_id=current_user.organization_id,
    )

    if not deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )

    # Log the deactivation
    audit_service = get_audit_service(db)
    await audit_service.log_action(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGE,
        resource_type="vendor_deployment",
        resource_id=deployment_id,
        new_values={"status": "inactive"},
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details=f"Deactivated deployment: {deployment_id}",
    )
    await db.commit()


# =============================================================================
# Tool Request Endpoints
# =============================================================================


@router.post("/request", response_model=ToolRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_tool_request(
    request: Request,
    request_data: ToolRequestCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ToolRequestResponse:
    """
    Request evaluation of a new AI tool.

    Any user can submit a request for a new AI tool to be evaluated
    and potentially added to the approved registry.
    """
    tool_request = await approved_vendor_service.create_tool_request(
        db=db,
        org_id=current_user.organization_id,
        user_id=current_user.id,
        data=request_data.model_dump(exclude_unset=True),
    )

    # Log the request
    audit_service = get_audit_service(db)
    await audit_service.log_action(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        resource_type="ai_tool_request",
        resource_id=tool_request.id,
        new_values={
            "vendor_name": tool_request.vendor_name,
            "department": tool_request.department,
            "urgency": tool_request.urgency,
        },
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details=f"Submitted tool request for: {tool_request.vendor_name}",
    )
    await db.commit()
    await db.refresh(tool_request)

    return ToolRequestResponse.model_validate(tool_request)


@router.put("/requests/{request_id}", response_model=ToolRequestResponse)
async def update_tool_request(
    request: Request,
    request_id: str,
    request_data: ToolRequestUpdate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ToolRequestResponse:
    """
    Update a tool request status (admin only).

    Allows admins to review requests, change status, add notes,
    and link to created vendors upon approval.
    """
    tool_request = await approved_vendor_service.update_request_status(
        db=db,
        request_id=request_id,
        org_id=current_user.organization_id,
        reviewer_id=current_user.id,
        status=request_data.status.value if request_data.status else None,
        notes=request_data.review_notes,
    )

    if not tool_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool request not found",
        )

    # Log the update
    audit_service = get_audit_service(db)
    await audit_service.log_action(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGE,
        resource_type="ai_tool_request",
        resource_id=request_id,
        new_values=request_data.model_dump(exclude_unset=True),
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details=f"Updated tool request status for: {tool_request.vendor_name}",
    )
    await db.commit()
    await db.refresh(tool_request)

    return ToolRequestResponse.model_validate(tool_request)
