"""Vendor service layer for business logic."""

import json

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate


async def get_vendor_by_id(
    db: AsyncSession,
    vendor_id: str,
    org_id: str,
) -> Vendor | None:
    """Get a single vendor by ID with organization isolation.

    Args:
        db: Database session
        vendor_id: Vendor UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        Vendor if found, None otherwise
    """
    result = await db.execute(
        select(Vendor).where(
            Vendor.id == vendor_id,
            Vendor.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def get_vendor_by_name(
    db: AsyncSession,
    name: str,
    org_id: str,
) -> Vendor | None:
    """Get a vendor by name within an organization.

    Args:
        db: Database session
        name: Vendor name
        org_id: Organization ID

    Returns:
        Vendor if found, None otherwise
    """
    result = await db.execute(
        select(Vendor).where(
            Vendor.name == name,
            Vendor.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def get_vendors(
    db: AsyncSession,
    org_id: str,
    skip: int = 0,
    limit: int = 20,
    tier: str | None = None,
    status: str | None = None,
    search: str | None = None,
) -> tuple[list[Vendor], int]:
    """List vendors with pagination and filtering.

    Args:
        db: Database session
        org_id: Organization ID for multi-tenant isolation
        skip: Number of records to skip
        limit: Maximum number of records to return
        tier: Filter by tier (optional)
        status: Filter by status (optional)
        search: Search term for name (optional)

    Returns:
        Tuple of (list of vendors, total count)
    """
    # Base query
    query = select(Vendor).where(Vendor.organization_id == org_id)

    # Apply filters
    if tier:
        query = query.where(Vendor.tier == tier)
    if status:
        query = query.where(Vendor.status == status)
    if search:
        query = query.where(Vendor.name.ilike(f"%{search}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(Vendor.name).offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    vendors = list(result.scalars().all())

    return vendors, total


async def create_vendor(
    db: AsyncSession,
    org_id: str,
    vendor_data: VendorCreate,
) -> Vendor:
    """Create a new vendor.

    Args:
        db: Database session
        org_id: Organization ID
        vendor_data: Vendor creation data

    Returns:
        Created vendor

    Raises:
        ValueError: If vendor name already exists in organization
    """
    # Check for duplicate name
    existing = await get_vendor_by_name(db, vendor_data.name, org_id)
    if existing:
        raise ValueError(f"Vendor with name '{vendor_data.name}' already exists")

    # Convert tags list to JSON string for storage
    tags_json = json.dumps(vendor_data.tags) if vendor_data.tags else None

    vendor = Vendor(
        organization_id=org_id,
        name=vendor_data.name,
        description=vendor_data.description,
        website=vendor_data.website,
        tier=vendor_data.tier or "medium",
        status=vendor_data.status or "onboarding",
        criticality_score=vendor_data.criticality_score,
        data_classification=vendor_data.data_classification,
        tags=tags_json,
    )
    db.add(vendor)
    await db.flush()
    await db.refresh(vendor)
    return vendor


async def update_vendor(
    db: AsyncSession,
    vendor_id: str,
    org_id: str,
    vendor_data: VendorUpdate,
) -> Vendor | None:
    """Update a vendor's information.

    Args:
        db: Database session
        vendor_id: Vendor UUID
        org_id: Organization ID for multi-tenant isolation
        vendor_data: Fields to update

    Returns:
        Updated vendor or None if not found

    Raises:
        ValueError: If updating name to one that already exists
    """
    vendor = await get_vendor_by_id(db, vendor_id, org_id)
    if not vendor:
        return None

    # Get update data, excluding unset fields
    update_data = vendor_data.model_dump(exclude_unset=True)

    # Check for duplicate name if name is being updated
    if "name" in update_data and update_data["name"] != vendor.name:
        existing = await get_vendor_by_name(db, update_data["name"], org_id)
        if existing:
            raise ValueError(f"Vendor with name '{update_data['name']}' already exists")

    # Handle tags serialization
    if "tags" in update_data:
        update_data["tags"] = json.dumps(update_data["tags"]) if update_data["tags"] else None

    # Apply updates
    for field, value in update_data.items():
        setattr(vendor, field, value)

    await db.flush()
    await db.refresh(vendor)
    return vendor


async def delete_vendor(
    db: AsyncSession,
    vendor_id: str,
    org_id: str,
) -> bool:
    """Delete a vendor.

    Args:
        db: Database session
        vendor_id: Vendor UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        True if deleted, False if not found
    """
    vendor = await get_vendor_by_id(db, vendor_id, org_id)
    if not vendor:
        return False

    await db.delete(vendor)
    await db.flush()
    return True
