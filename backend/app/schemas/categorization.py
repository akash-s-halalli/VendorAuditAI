"""Pydantic schemas for vendor categorization API."""

from typing import Literal

from pydantic import BaseModel, Field


# Risk level type definition matching the service
RiskLevelType = Literal["critical", "high", "medium", "low"]

# Assessment priority type definition
AssessmentPriorityType = Literal["immediate", "standard", "deferred"]


class VendorCategorizationRequest(BaseModel):
    """Schema for vendor categorization analysis request."""

    vendor_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the vendor to categorize",
    )
    vendor_description: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional description of the vendor or service",
    )
    service_type: str | None = Field(
        default=None,
        max_length=255,
        description="Optional type of service provided by the vendor",
    )
    additional_context: str | None = Field(
        default=None,
        max_length=1000,
        description="Any additional context about the vendor for better categorization",
    )


class CategorizationResult(BaseModel):
    """Schema for vendor categorization analysis result."""

    primary_category: str = Field(
        ...,
        description="Primary category ID for the vendor (e.g., 'cloud_infrastructure')",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the categorization (0.0 to 1.0)",
    )
    risk_level: RiskLevelType = Field(
        ...,
        description="Inherent risk level for this category",
    )
    recommended_frameworks: list[str] = Field(
        default_factory=list,
        description="List of recommended compliance framework IDs",
    )
    matched_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords that matched during categorization",
    )
    secondary_categories: list[str] = Field(
        default_factory=list,
        description="Secondary category IDs that also matched",
    )
    data_types: list[str] = Field(
        default_factory=list,
        description="Types of data typically processed by this category",
    )
    assessment_priority: AssessmentPriorityType = Field(
        ...,
        description="Recommended assessment priority based on risk level",
    )

    model_config = {"from_attributes": True}


class CategorySummary(BaseModel):
    """Schema for category summary in list view."""

    id: str = Field(..., description="Unique category identifier")
    display_name: str = Field(..., description="Human-readable category name")
    description: str = Field(..., description="Description of the category")
    risk_level: RiskLevelType = Field(..., description="Default risk level for this category")
    default_frameworks: list[str] = Field(
        default_factory=list,
        description="Default compliance frameworks for this category",
    )

    model_config = {"from_attributes": True}


class CategoryDetail(CategorySummary):
    """Schema for full category details including keywords and examples."""

    keywords: list[str] = Field(
        default_factory=list,
        description="Keywords used to identify vendors in this category",
    )
    data_types: list[str] = Field(
        default_factory=list,
        description="Types of data typically processed by vendors in this category",
    )
    example_vendors: list[str] = Field(
        default_factory=list,
        description="Example vendors commonly found in this category",
    )

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    """Schema for category list response."""

    data: list[CategorySummary]
    total: int = Field(..., description="Total number of categories")


class BatchVendorInput(BaseModel):
    """Schema for a single vendor in batch categorization."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the vendor",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional description of the vendor",
    )


class BatchCategorizationRequest(BaseModel):
    """Schema for batch vendor categorization request."""

    vendors: list[BatchVendorInput] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of vendors to categorize (max 100)",
    )


class BatchCategorizationResultItem(BaseModel):
    """Schema for a single result in batch categorization."""

    vendor_name: str = Field(..., description="Name of the vendor that was categorized")
    result: CategorizationResult = Field(..., description="Categorization result for this vendor")


class BatchCategorizationResponse(BaseModel):
    """Schema for batch categorization response."""

    results: list[BatchCategorizationResultItem] = Field(
        ...,
        description="Categorization results for each vendor",
    )
    total: int = Field(..., description="Total number of vendors processed")


class FrameworkRecommendationRequest(BaseModel):
    """Schema for framework recommendation query parameters."""

    is_eu_vendor: bool = Field(
        default=False,
        description="Whether the vendor operates in the EU (triggers DORA consideration)",
    )
    is_financial_entity: bool = Field(
        default=False,
        description="Whether the vendor is a financial entity (triggers DORA consideration)",
    )
    handles_student_data: bool = Field(
        default=False,
        description="Whether the vendor handles student data (triggers HECVAT consideration)",
    )
    handles_health_data: bool = Field(
        default=False,
        description="Whether the vendor handles health data (triggers HIPAA consideration)",
    )


class FrameworkRecommendation(BaseModel):
    """Schema for a framework recommendation with priority."""

    framework_id: str = Field(..., description="Framework identifier")
    priority: int = Field(..., ge=1, description="Priority order (1 = highest priority)")


class FrameworkRecommendationResponse(BaseModel):
    """Schema for framework recommendations response."""

    category_id: str = Field(..., description="Category for which recommendations were generated")
    recommendations: list[FrameworkRecommendation] = Field(
        ...,
        description="Recommended frameworks in priority order",
    )
    total: int = Field(..., description="Total number of recommended frameworks")
