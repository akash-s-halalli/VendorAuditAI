"""Compliance framework service for loading and managing framework definitions."""

import json
import logging
from pathlib import Path
from typing import Any

from app.schemas.compliance import (
    CategoryResponse,
    ControlBase,
    ControlResponse,
    ControlSearchQuery,
    ControlSearchResponse,
    ControlSearchResult,
    FrameworkListResponse,
    FrameworkResponse,
    FrameworkSummary,
    RequirementBase,
)

logger = logging.getLogger(__name__)

# Path to framework data files
FRAMEWORKS_DIR = Path(__file__).parent.parent / "data" / "frameworks"

# Cache for loaded frameworks
_frameworks_cache: dict[str, dict[str, Any]] = {}


def _load_framework_file(framework_id: str) -> dict[str, Any] | None:
    """Load a framework definition from its JSON file.

    Args:
        framework_id: The framework identifier (e.g., 'soc2', 'iso27001')

    Returns:
        The framework data as a dictionary, or None if not found
    """
    file_path = FRAMEWORKS_DIR / f"{framework_id}.json"
    if not file_path.exists():
        logger.warning(f"Framework file not found: {file_path}")
        return None

    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing framework file {file_path}: {e}")
        return None
    except OSError as e:
        logger.error(f"Error reading framework file {file_path}: {e}")
        return None


def _get_cached_framework(framework_id: str) -> dict[str, Any] | None:
    """Get a framework from cache, loading it if necessary.

    Args:
        framework_id: The framework identifier

    Returns:
        The cached framework data, or None if not available
    """
    if framework_id not in _frameworks_cache:
        framework_data = _load_framework_file(framework_id)
        if framework_data:
            _frameworks_cache[framework_id] = framework_data
    return _frameworks_cache.get(framework_id)


def _discover_frameworks() -> list[str]:
    """Discover all available framework IDs by scanning the frameworks directory.

    Returns:
        List of framework IDs
    """
    if not FRAMEWORKS_DIR.exists():
        logger.warning(f"Frameworks directory not found: {FRAMEWORKS_DIR}")
        return []

    framework_ids = []
    for file_path in FRAMEWORKS_DIR.glob("*.json"):
        framework_ids.append(file_path.stem)
    return sorted(framework_ids)


def get_all_frameworks() -> FrameworkListResponse:
    """Get all available compliance frameworks.

    Returns:
        FrameworkListResponse containing summary information for all frameworks
    """
    framework_ids = _discover_frameworks()
    summaries = []

    for framework_id in framework_ids:
        framework_data = _get_cached_framework(framework_id)
        if framework_data:
            # Count categories and controls
            categories = framework_data.get("categories", [])
            category_count = len(categories)
            control_count = sum(len(cat.get("controls", [])) for cat in categories)

            summary = FrameworkSummary(
                id=framework_data["id"],
                name=framework_data["name"],
                version=framework_data["version"],
                description=framework_data["description"],
                organization=framework_data["organization"],
                category_count=category_count,
                control_count=control_count,
            )
            summaries.append(summary)

    return FrameworkListResponse(data=summaries, total=len(summaries))


def get_framework_by_id(framework_id: str) -> FrameworkResponse | None:
    """Get a specific framework by its ID with full details.

    Args:
        framework_id: The framework identifier

    Returns:
        FrameworkResponse with categories and controls, or None if not found
    """
    framework_data = _get_cached_framework(framework_id)
    if not framework_data:
        return None

    # Build category responses with controls
    categories = []
    for cat_data in framework_data.get("categories", []):
        controls = []
        for ctrl_data in cat_data.get("controls", []):
            # Build requirements list
            requirements = [
                RequirementBase(
                    id=req["id"],
                    description=req["description"],
                    guidance=req.get("guidance", ""),
                )
                for req in ctrl_data.get("requirements", [])
            ]

            control = ControlBase(
                id=ctrl_data["id"],
                name=ctrl_data["name"],
                description=ctrl_data["description"],
                requirements=requirements,
            )
            controls.append(control)

        category = CategoryResponse(
            id=cat_data["id"],
            name=cat_data["name"],
            description=cat_data["description"],
            framework_id=framework_data["id"],
            controls=controls,
        )
        categories.append(category)

    return FrameworkResponse(
        id=framework_data["id"],
        name=framework_data["name"],
        version=framework_data["version"],
        description=framework_data["description"],
        organization=framework_data["organization"],
        categories=categories,
    )


def get_framework_controls(framework_id: str) -> list[ControlResponse] | None:
    """Get all controls for a specific framework.

    Args:
        framework_id: The framework identifier

    Returns:
        List of ControlResponse objects, or None if framework not found
    """
    framework_data = _get_cached_framework(framework_id)
    if not framework_data:
        return None

    controls = []
    for cat_data in framework_data.get("categories", []):
        for ctrl_data in cat_data.get("controls", []):
            # Build requirements list
            requirements = [
                RequirementBase(
                    id=req["id"],
                    description=req["description"],
                    guidance=req.get("guidance", ""),
                )
                for req in ctrl_data.get("requirements", [])
            ]

            control = ControlResponse(
                id=ctrl_data["id"],
                name=ctrl_data["name"],
                description=ctrl_data["description"],
                requirements=requirements,
                category_id=cat_data["id"],
                framework_id=framework_data["id"],
            )
            controls.append(control)

    return controls


def get_control_by_id(framework_id: str, control_id: str) -> ControlResponse | None:
    """Get a specific control by framework and control ID.

    Args:
        framework_id: The framework identifier
        control_id: The control identifier within the framework

    Returns:
        ControlResponse, or None if not found
    """
    framework_data = _get_cached_framework(framework_id)
    if not framework_data:
        return None

    for cat_data in framework_data.get("categories", []):
        for ctrl_data in cat_data.get("controls", []):
            if ctrl_data["id"] == control_id:
                # Build requirements list
                requirements = [
                    RequirementBase(
                        id=req["id"],
                        description=req["description"],
                        guidance=req.get("guidance", ""),
                    )
                    for req in ctrl_data.get("requirements", [])
                ]

                return ControlResponse(
                    id=ctrl_data["id"],
                    name=ctrl_data["name"],
                    description=ctrl_data["description"],
                    requirements=requirements,
                    category_id=cat_data["id"],
                    framework_id=framework_data["id"],
                )

    return None


def search_controls(query: ControlSearchQuery) -> ControlSearchResponse:
    """Search for controls across frameworks.

    Args:
        query: The search query parameters

    Returns:
        ControlSearchResponse with matching controls
    """
    search_text = query.query.lower()
    results: list[ControlSearchResult] = []

    # Determine which frameworks to search
    if query.framework_ids:
        framework_ids = query.framework_ids
    else:
        framework_ids = _discover_frameworks()

    for framework_id in framework_ids:
        framework_data = _get_cached_framework(framework_id)
        if not framework_data:
            continue

        for cat_data in framework_data.get("categories", []):
            for ctrl_data in cat_data.get("controls", []):
                # Simple text matching for search
                score = _calculate_relevance_score(ctrl_data, search_text)
                if score > 0:
                    # Build requirements list
                    requirements = [
                        RequirementBase(
                            id=req["id"],
                            description=req["description"],
                            guidance=req.get("guidance", ""),
                        )
                        for req in ctrl_data.get("requirements", [])
                    ]

                    control = ControlBase(
                        id=ctrl_data["id"],
                        name=ctrl_data["name"],
                        description=ctrl_data["description"],
                        requirements=requirements,
                    )

                    result = ControlSearchResult(
                        framework_id=framework_data["id"],
                        framework_name=framework_data["name"],
                        category_id=cat_data["id"],
                        category_name=cat_data["name"],
                        control=control,
                        relevance_score=score,
                    )
                    results.append(result)

    # Sort by relevance score and apply limit
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    results = results[: query.limit]

    return ControlSearchResponse(
        query=query.query,
        results=results,
        total=len(results),
    )


def _calculate_relevance_score(ctrl_data: dict[str, Any], search_text: str) -> float:
    """Calculate a simple relevance score for a control based on search text.

    Args:
        ctrl_data: The control data dictionary
        search_text: The lowercase search text

    Returns:
        Relevance score between 0.0 and 1.0
    """
    score = 0.0
    max_score = 4.0

    # Check control ID
    if search_text in ctrl_data.get("id", "").lower():
        score += 1.0

    # Check control name
    if search_text in ctrl_data.get("name", "").lower():
        score += 1.0

    # Check control description
    if search_text in ctrl_data.get("description", "").lower():
        score += 1.0

    # Check requirements
    for req in ctrl_data.get("requirements", []):
        if search_text in req.get("description", "").lower():
            score += 0.5
            break
        if search_text in req.get("guidance", "").lower():
            score += 0.25
            break

    return min(score / max_score, 1.0)


def get_available_framework_ids() -> list[str]:
    """Get list of all available framework IDs.

    Returns:
        List of framework identifiers
    """
    return _discover_frameworks()


def reload_frameworks() -> None:
    """Reload all frameworks from disk, clearing the cache.

    This is useful for development or when framework files are updated.
    """
    global _frameworks_cache
    _frameworks_cache = {}
    logger.info("Framework cache cleared")


def get_framework_summary(framework_id: str) -> FrameworkSummary | None:
    """Get summary information for a specific framework.

    Args:
        framework_id: The framework identifier

    Returns:
        FrameworkSummary, or None if not found
    """
    framework_data = _get_cached_framework(framework_id)
    if not framework_data:
        return None

    categories = framework_data.get("categories", [])
    category_count = len(categories)
    control_count = sum(len(cat.get("controls", [])) for cat in categories)

    return FrameworkSummary(
        id=framework_data["id"],
        name=framework_data["name"],
        version=framework_data["version"],
        description=framework_data["description"],
        organization=framework_data["organization"],
        category_count=category_count,
        control_count=control_count,
    )
