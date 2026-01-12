"""Vendor categorization API endpoints.

This module provides endpoints for automatic vendor categorization based on
keywords, service types, and data access patterns. It recommends appropriate
risk levels and compliance frameworks based on vendor characteristics.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.categorization import (
    BatchCategorizationRequest,
    BatchCategorizationResponse,
    BatchCategorizationResultItem,
    CategoryDetail,
    CategoryListResponse,
    CategorySummary,
    CategorizationResult,
    FrameworkRecommendation,
    FrameworkRecommendationResponse,
    VendorCategorizationRequest,
)
from app.services.vendor_categorization import (
    CATEGORY_DEFINITIONS,
    EXAMPLE_VENDOR_TAXONOMY,
    VendorCategory,
    categorize_vendor,
    get_all_categories,
    get_category_info,
    get_framework_recommendations,
)

router = APIRouter(tags=["Vendor Categorization"])


@router.post("/analyze", response_model=CategorizationResult)
async def analyze_vendor(request: VendorCategorizationRequest) -> CategorizationResult:
    """
    Analyze a vendor and return categorization results.

    This endpoint uses keyword matching and analysis to automatically categorize
    a vendor based on the provided information. It returns:
    - Primary category for the vendor
    - Confidence score for the categorization
    - Risk level associated with the category
    - Recommended compliance frameworks
    - Keywords that matched during analysis
    - Secondary categories that also matched
    - Typical data types handled by this vendor category
    - Assessment priority recommendation

    Args:
        request: Vendor information including name and optional description/context

    Returns:
        CategorizationResult with full categorization analysis
    """
    result = categorize_vendor(
        vendor_name=request.vendor_name,
        vendor_description=request.vendor_description,
        service_type=request.service_type,
        additional_context=request.additional_context,
    )

    return CategorizationResult(
        primary_category=result.primary_category.value,
        confidence=result.confidence,
        risk_level=result.risk_level.value,
        recommended_frameworks=result.recommended_frameworks,
        matched_keywords=result.matched_keywords,
        secondary_categories=[cat.value for cat in result.secondary_categories],
        data_types=result.data_types,
        assessment_priority=result.assessment_priority,
    )


@router.get("/categories", response_model=CategoryListResponse)
async def list_categories() -> CategoryListResponse:
    """
    List all available vendor categories.

    Returns summary information for each of the 25 vendor categories including:
    - Category ID and display name
    - Description of the category
    - Default risk level
    - Default compliance frameworks

    This endpoint is useful for understanding the categorization taxonomy
    and presenting category options to users.

    Returns:
        CategoryListResponse with list of all categories
    """
    categories = get_all_categories()

    category_summaries = [
        CategorySummary(
            id=cat["id"],
            display_name=cat["display_name"],
            description=cat["description"],
            risk_level=cat["risk_level"],
            default_frameworks=cat["default_frameworks"],
        )
        for cat in categories
    ]

    return CategoryListResponse(
        data=category_summaries,
        total=len(category_summaries),
    )


@router.get("/categories/{category_id}", response_model=CategoryDetail)
async def get_category(category_id: str) -> CategoryDetail:
    """
    Get detailed information for a specific vendor category.

    Returns full category details including:
    - Category ID and display name
    - Description and risk level
    - Default compliance frameworks
    - Keywords used for matching
    - Typical data types processed
    - Example vendors in this category

    Args:
        category_id: The category identifier (e.g., 'cloud_infrastructure')

    Returns:
        CategoryDetail with full category information

    Raises:
        HTTPException: 404 if category is not found
    """
    # Validate category_id exists
    try:
        category_enum = VendorCategory(category_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_id}' not found",
        )

    if category_enum not in CATEGORY_DEFINITIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_id}' not found",
        )

    definition = CATEGORY_DEFINITIONS[category_enum]

    # Get example vendors from the taxonomy
    example_vendors = [
        vendor_data["name"]
        for vendor_key, vendor_data in EXAMPLE_VENDOR_TAXONOMY.items()
        if vendor_data.get("category") == category_enum
    ]

    return CategoryDetail(
        id=definition.category.value,
        display_name=definition.display_name,
        description=definition.description,
        risk_level=definition.risk_level.value,
        default_frameworks=definition.default_frameworks,
        keywords=definition.keywords,
        data_types=definition.data_types,
        example_vendors=example_vendors,
    )


@router.post("/batch", response_model=BatchCategorizationResponse)
async def batch_categorize(request: BatchCategorizationRequest) -> BatchCategorizationResponse:
    """
    Batch categorize multiple vendors at once.

    This endpoint processes multiple vendors in a single request, returning
    categorization results for each vendor. Useful for:
    - Initial vendor portfolio categorization
    - Bulk import of vendor lists
    - Periodic recategorization of existing vendors

    Maximum 100 vendors per request.

    Args:
        request: List of vendors with name and optional description

    Returns:
        BatchCategorizationResponse with results for each vendor
    """
    results: list[BatchCategorizationResultItem] = []

    for vendor in request.vendors:
        categorization = categorize_vendor(
            vendor_name=vendor.name,
            vendor_description=vendor.description,
        )

        result_item = BatchCategorizationResultItem(
            vendor_name=vendor.name,
            result=CategorizationResult(
                primary_category=categorization.primary_category.value,
                confidence=categorization.confidence,
                risk_level=categorization.risk_level.value,
                recommended_frameworks=categorization.recommended_frameworks,
                matched_keywords=categorization.matched_keywords,
                secondary_categories=[cat.value for cat in categorization.secondary_categories],
                data_types=categorization.data_types,
                assessment_priority=categorization.assessment_priority,
            ),
        )
        results.append(result_item)

    return BatchCategorizationResponse(
        results=results,
        total=len(results),
    )


@router.get("/frameworks/{category_id}", response_model=FrameworkRecommendationResponse)
async def get_framework_recommendations_for_category(
    category_id: str,
    is_eu_vendor: bool = Query(
        default=False,
        description="Whether the vendor operates in the EU (triggers DORA consideration)",
    ),
    is_financial_entity: bool = Query(
        default=False,
        description="Whether the vendor is a financial entity (triggers DORA consideration)",
    ),
    handles_student_data: bool = Query(
        default=False,
        description="Whether the vendor handles student data (triggers HECVAT consideration)",
    ),
    handles_health_data: bool = Query(
        default=False,
        description="Whether the vendor handles health data (triggers HIPAA consideration)",
    ),
) -> FrameworkRecommendationResponse:
    """
    Get framework recommendations for a specific category.

    Returns a prioritized list of compliance frameworks recommended for vendors
    in the specified category. The recommendations consider:
    - Default frameworks for the category
    - EU vendor status (adds DORA)
    - Financial entity status (adds DORA)
    - Student data handling (adds HECVAT)
    - Health data handling (adds HIPAA considerations)

    Args:
        category_id: The category identifier (e.g., 'cloud_infrastructure')
        is_eu_vendor: Whether the vendor operates in the EU
        is_financial_entity: Whether the vendor is a financial entity
        handles_student_data: Whether the vendor handles student data
        handles_health_data: Whether the vendor handles health data

    Returns:
        FrameworkRecommendationResponse with prioritized framework list

    Raises:
        HTTPException: 404 if category is not found
    """
    # Validate category_id exists
    try:
        category_enum = VendorCategory(category_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_id}' not found",
        )

    if category_enum not in CATEGORY_DEFINITIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_id}' not found",
        )

    # Get framework recommendations
    frameworks = get_framework_recommendations(
        category=category_enum,
        is_eu_vendor=is_eu_vendor,
        is_financial_entity=is_financial_entity,
        handles_student_data=handles_student_data,
        handles_health_data=handles_health_data,
    )

    # Create prioritized recommendations
    recommendations = [
        FrameworkRecommendation(framework_id=fw, priority=idx + 1)
        for idx, fw in enumerate(frameworks)
    ]

    return FrameworkRecommendationResponse(
        category_id=category_id,
        recommendations=recommendations,
        total=len(recommendations),
    )
