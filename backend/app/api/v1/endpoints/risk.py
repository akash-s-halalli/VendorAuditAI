"""Risk scoring API endpoints.

Provides endpoints for:
- GET /risk/vendors - Get risk scores for all vendors
- GET /risk/vendors/{vendor_id} - Get detailed risk breakdown for a vendor
- POST /risk/calculate - Trigger risk recalculation for all vendors
- GET /risk/trends - Get risk score trends over time
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.schemas.risk import (
    RiskCalculationRequest,
    RiskCalculationResponse,
    RiskScore,
    RiskScoreListResponse,
    RiskTrendsResponse,
)
from app.services import risk_scoring

router = APIRouter(tags=["Risk Scoring"])


@router.get("/vendors", response_model=RiskScoreListResponse)
async def get_all_vendor_risk_scores(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> RiskScoreListResponse:
    """
    Get risk scores for all vendors in the organization.

    Returns a list of vendors with their calculated risk scores, including:
    - Overall score (0-100)
    - Risk level (low, medium, high, critical)
    - Factor breakdown
    - Summary statistics

    Risk levels:
    - 0-25: Low Risk (Green)
    - 26-50: Medium Risk (Yellow)
    - 51-75: High Risk (Orange)
    - 76-100: Critical Risk (Red)
    """
    skip = (page - 1) * limit
    return await risk_scoring.get_all_vendor_risk_scores(
        db=db,
        org_id=current_user.organization_id,
        skip=skip,
        limit=limit,
    )


@router.get("/vendors/{vendor_id}", response_model=RiskScore)
async def get_vendor_risk_score(
    vendor_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RiskScore:
    """
    Get detailed risk breakdown for a specific vendor.

    Returns comprehensive risk analysis including:
    - Overall risk score (0-100)
    - Risk level classification
    - Detailed factor breakdown:
      - Findings Risk (severity-weighted open findings)
      - Compliance Coverage (document coverage and remediation)
      - Data Sensitivity (classification and tier impact)
      - Document Freshness (age of compliance docs)
    - Finding counts by severity
    - Vendor metadata affecting score
    """
    score = await risk_scoring.get_vendor_risk_score(
        db=db,
        vendor_id=vendor_id,
        org_id=current_user.organization_id,
    )

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )

    return score


@router.post("/calculate", response_model=RiskCalculationResponse)
async def recalculate_risk_scores(
    request: RiskCalculationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RiskCalculationResponse:
    """
    Trigger risk recalculation for vendors.

    By default, recalculates scores for all vendors in the organization.
    Optionally specify vendor_ids to only recalculate specific vendors.

    The recalculation:
    - Fetches latest findings and documents
    - Applies the risk scoring algorithm
    - Updates cached risk_score on vendor records
    - Records calculation timestamp

    Use force=true to recalculate even if recently calculated (within 1 hour).
    """
    return await risk_scoring.recalculate_risk_scores(
        db=db,
        org_id=current_user.organization_id,
        vendor_ids=request.vendor_ids,
        force=request.force,
    )


@router.get("/trends", response_model=RiskTrendsResponse)
async def get_risk_trends(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
) -> RiskTrendsResponse:
    """
    Get risk score trends over time for all vendors.

    Returns trend analysis including:
    - Current score for each vendor
    - Trend direction (improving, stable, worsening)
    - Score change over the specified period
    - Historical data points for charting

    Note: Full historical tracking requires periodic snapshots.
    Current implementation shows current state with trend indicators.
    """
    return await risk_scoring.get_risk_trends(
        db=db,
        org_id=current_user.organization_id,
        days=days,
    )
