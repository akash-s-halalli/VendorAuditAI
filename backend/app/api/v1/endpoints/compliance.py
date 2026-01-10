"""Compliance framework API endpoints."""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.compliance import (
    ControlResponse,
    ControlSearchQuery,
    ControlSearchResponse,
    FrameworkListResponse,
    FrameworkResponse,
    FrameworkSummary,
)
from app.services import compliance as compliance_service

router = APIRouter(tags=["Compliance Frameworks"])


@router.get("", response_model=FrameworkListResponse)
async def list_frameworks() -> FrameworkListResponse:
    """
    List all available compliance frameworks.

    Returns summary information for each framework including name, version,
    and counts of categories and controls.
    """
    return compliance_service.get_all_frameworks()


@router.get("/search", response_model=ControlSearchResponse)
async def search_controls(
    query: str = Query(..., min_length=2, description="Search query text"),
    framework_ids: str | None = Query(
        None, description="Comma-separated list of framework IDs to search"
    ),
    limit: int = Query(50, ge=1, le=200, description="Maximum results to return"),
) -> ControlSearchResponse:
    """
    Search for controls across compliance frameworks.

    Searches control IDs, names, descriptions, and requirements for the given query.
    Results are ranked by relevance.
    """
    # Parse framework IDs if provided
    framework_id_list = None
    if framework_ids:
        framework_id_list = [fid.strip() for fid in framework_ids.split(",") if fid.strip()]

    search_query = ControlSearchQuery(
        query=query,
        framework_ids=framework_id_list,
        limit=limit,
    )
    return compliance_service.search_controls(search_query)


@router.get("/{framework_id}", response_model=FrameworkResponse)
async def get_framework(framework_id: str) -> FrameworkResponse:
    """
    Get detailed information for a specific compliance framework.

    Returns the full framework including all categories, controls, and requirements.
    """
    framework = compliance_service.get_framework_by_id(framework_id)
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework '{framework_id}' not found",
        )
    return framework


@router.get("/{framework_id}/summary", response_model=FrameworkSummary)
async def get_framework_summary(framework_id: str) -> FrameworkSummary:
    """
    Get summary information for a specific compliance framework.

    Returns basic framework information with category and control counts.
    """
    summary = compliance_service.get_framework_summary(framework_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework '{framework_id}' not found",
        )
    return summary


@router.get("/{framework_id}/controls", response_model=list[ControlResponse])
async def get_framework_controls(framework_id: str) -> list[ControlResponse]:
    """
    Get all controls for a specific compliance framework.

    Returns a flat list of all controls across all categories in the framework.
    """
    controls = compliance_service.get_framework_controls(framework_id)
    if controls is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework '{framework_id}' not found",
        )
    return controls


@router.get("/{framework_id}/controls/{control_id}", response_model=ControlResponse)
async def get_control(framework_id: str, control_id: str) -> ControlResponse:
    """
    Get a specific control by ID within a framework.

    Returns the control details including all requirements.
    """
    control = compliance_service.get_control_by_id(framework_id, control_id)
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Control '{control_id}' not found in framework '{framework_id}'",
        )
    return control
