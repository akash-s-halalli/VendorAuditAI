"""Seed database with example vendors from EXAMPLE_VENDOR_TAXONOMY.

This script populates the demo organization with 50+ example vendors
including confirmed DoorDash partners and industry-standard vendors.

Usage:
    python -m app.scripts.seed_vendors
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker, init_db
from app.models.organization import Organization
from app.models.user import User
from app.models.vendor import Vendor
from app.services.vendor_categorization import (
    EXAMPLE_VENDOR_TAXONOMY,
    RiskLevel,
    VendorCategory,
)


# Map risk levels to tier strings
RISK_TO_TIER = {
    RiskLevel.CRITICAL: "critical",
    RiskLevel.HIGH: "high",
    RiskLevel.MEDIUM: "medium",
    RiskLevel.LOW: "low",
}


async def get_demo_organization(db: AsyncSession) -> Organization | None:
    """Find the demo organization by looking for demo user."""
    # Look for demo user
    result = await db.execute(
        select(User).where(User.email == "demo@vendorauditai.com")
    )
    demo_user = result.scalar_one_or_none()

    if demo_user:
        # Get their organization
        result = await db.execute(
            select(Organization).where(Organization.id == demo_user.organization_id)
        )
        return result.scalar_one_or_none()

    # Also try newdemo user
    result = await db.execute(
        select(User).where(User.email == "newdemo@vendorauditai.com")
    )
    newdemo_user = result.scalar_one_or_none()

    if newdemo_user:
        result = await db.execute(
            select(Organization).where(Organization.id == newdemo_user.organization_id)
        )
        return result.scalar_one_or_none()

    return None


async def seed_vendors(db: AsyncSession, organization_id: str) -> int:
    """Seed vendors from EXAMPLE_VENDOR_TAXONOMY into the database.

    Args:
        db: Database session
        organization_id: Organization to seed vendors into

    Returns:
        Number of vendors created
    """
    created_count = 0
    skipped_count = 0

    for vendor_key, vendor_data in EXAMPLE_VENDOR_TAXONOMY.items():
        # Check if vendor already exists
        result = await db.execute(
            select(Vendor).where(
                Vendor.organization_id == organization_id,
                Vendor.name == vendor_data["name"]
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            skipped_count += 1
            continue

        # Map data to Vendor model
        category: VendorCategory = vendor_data["category"]
        risk_level: RiskLevel = vendor_data["risk_level"]

        # Create vendor
        vendor = Vendor(
            organization_id=organization_id,
            name=vendor_data["name"],
            description=vendor_data.get("service_description", ""),
            category=category.value,
            tier=RISK_TO_TIER.get(risk_level, "medium"),
            status="active",
            recommended_frameworks=json.dumps(vendor_data.get("frameworks", [])),
            data_types=json.dumps(vendor_data.get("data_access", [])),
            categorization_confidence=0.95 if vendor_data.get("doordash_confirmed") else 0.85,
            tags=json.dumps([
                vendor_data.get("tier", ""),
                "doordash_confirmed" if vendor_data.get("doordash_confirmed") else "",
            ]),
        )

        db.add(vendor)
        created_count += 1

    await db.commit()

    print(f"[+] Created {created_count} vendors")
    print(f"[*] Skipped {skipped_count} existing vendors")

    return created_count


async def main():
    """Main entry point for seeding vendors."""
    print("[*] VendorAuditAI - Vendor Seeding Script")
    print("[*] =====================================")

    # Initialize database
    print("[*] Initializing database connection...")
    await init_db()

    async with async_session_maker() as db:
        # Find demo organization
        print("[*] Looking for demo organization...")
        org = await get_demo_organization(db)

        if not org:
            print("[!] ERROR: Demo organization not found!")
            print("[!] Please ensure demo@vendorauditai.com or newdemo@vendorauditai.com exists")
            return

        print(f"[+] Found organization: {org.name} (ID: {org.id})")

        # Count vendors in taxonomy
        total_vendors = len(EXAMPLE_VENDOR_TAXONOMY)
        print(f"[*] Found {total_vendors} vendors in EXAMPLE_VENDOR_TAXONOMY")

        # Seed vendors
        print("[*] Seeding vendors...")
        created = await seed_vendors(db, org.id)

        # Verify
        result = await db.execute(
            select(Vendor).where(Vendor.organization_id == org.id)
        )
        final_count = len(result.scalars().all())

        print(f"[+] Total vendors in organization: {final_count}")
        print("[+] Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
