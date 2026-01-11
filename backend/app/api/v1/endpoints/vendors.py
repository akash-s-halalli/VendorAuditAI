"""Vendor management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.models.audit_log import AuditAction
from app.schemas.vendor import (
    VendorCreate,
    VendorListResponse,
    VendorResponse,
    VendorUpdate,
)
from app.services import vendor as vendor_service
from app.services.audit import get_audit_service

router = APIRouter(tags=["Vendors"])


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


@router.get("", response_model=VendorListResponse)
async def list_vendors(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    tier: str | None = Query(None, description="Filter by tier"),
    status: str | None = Query(None, description="Filter by status"),
    search: str | None = Query(None, description="Search by name"),
) -> VendorListResponse:
    """
    List vendors for the current user's organization.

    Supports pagination, filtering by tier/status, and search by name.
    """
    skip = (page - 1) * limit
    vendors, total = await vendor_service.get_vendors(
        db=db,
        org_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        tier=tier,
        status=status,
        search=search,
    )
    return VendorListResponse(
        data=[VendorResponse.model_validate(v) for v in vendors],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    request: Request,
    vendor_data: VendorCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VendorResponse:
    """
    Create a new vendor for the current user's organization.
    """
    try:
        vendor = await vendor_service.create_vendor(
            db=db,
            org_id=current_user.organization_id,
            vendor_data=vendor_data,
        )

        # Log vendor creation
        audit_service = get_audit_service(db)
        await audit_service.log_action(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            action=AuditAction.CREATE,
            resource_type="vendor",
            resource_id=vendor.id,
            new_values={
                "name": vendor.name,
                "tier": vendor.tier,
                "status": vendor.status,
            },
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details=f"Created vendor: {vendor.name}",
        )
        await db.commit()

        return VendorResponse.model_validate(vendor)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VendorResponse:
    """
    Get a specific vendor by ID.
    """
    vendor = await vendor_service.get_vendor_by_id(
        db=db,
        vendor_id=vendor_id,
        org_id=current_user.organization_id,
    )
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )
    return VendorResponse.model_validate(vendor)


@router.patch("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    request: Request,
    vendor_id: str,
    vendor_data: VendorUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VendorResponse:
    """
    Update a vendor's information.

    Only provided fields will be updated.
    """
    try:
        # Get old values for audit
        old_vendor = await vendor_service.get_vendor_by_id(
            db=db,
            vendor_id=vendor_id,
            org_id=current_user.organization_id,
        )
        if not old_vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found",
            )

        old_values = {
            "name": old_vendor.name,
            "tier": old_vendor.tier,
            "status": old_vendor.status,
            "description": old_vendor.description,
        }

        vendor = await vendor_service.update_vendor(
            db=db,
            vendor_id=vendor_id,
            org_id=current_user.organization_id,
            vendor_data=vendor_data,
        )

        # Log vendor update
        audit_service = get_audit_service(db)
        new_values = vendor_data.model_dump(exclude_unset=True)
        await audit_service.log_action(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            action=AuditAction.UPDATE,
            resource_type="vendor",
            resource_id=vendor_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details=f"Updated vendor: {vendor.name}",
        )
        await db.commit()

        return VendorResponse.model_validate(vendor)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    request: Request,
    vendor_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Delete a vendor.

    This will also delete all associated documents and findings.
    """
    # Get vendor info for audit before deletion
    vendor = await vendor_service.get_vendor_by_id(
        db=db,
        vendor_id=vendor_id,
        org_id=current_user.organization_id,
    )
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )

    vendor_name = vendor.name
    old_values = {
        "name": vendor.name,
        "tier": vendor.tier,
        "status": vendor.status,
    }

    deleted = await vendor_service.delete_vendor(
        db=db,
        vendor_id=vendor_id,
        org_id=current_user.organization_id,
    )

    if deleted:
        # Log vendor deletion
        audit_service = get_audit_service(db)
        await audit_service.log_action(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            action=AuditAction.DELETE,
            resource_type="vendor",
            resource_id=vendor_id,
            old_values=old_values,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details=f"Deleted vendor: {vendor_name}",
        )
        await db.commit()
