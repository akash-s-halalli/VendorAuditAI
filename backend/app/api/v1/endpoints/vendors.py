"""Vendor management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.schemas.vendor import (
    VendorCreate,
    VendorListResponse,
    VendorResponse,
    VendorUpdate,
)
from app.services import vendor as vendor_service

router = APIRouter(tags=["Vendors"])


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
        vendor = await vendor_service.update_vendor(
            db=db,
            vendor_id=vendor_id,
            org_id=current_user.organization_id,
            vendor_data=vendor_data,
        )
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found",
            )
        return VendorResponse.model_validate(vendor)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    vendor_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Delete a vendor.

    This will also delete all associated documents and findings.
    """
    deleted = await vendor_service.delete_vendor(
        db=db,
        vendor_id=vendor_id,
        org_id=current_user.organization_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )
