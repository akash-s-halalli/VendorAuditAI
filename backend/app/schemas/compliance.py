"""Pydantic schemas for compliance framework management."""

from typing import Literal

from pydantic import BaseModel, Field


class RequirementBase(BaseModel):
    """Base schema for a compliance requirement within a control."""

    id: str = Field(..., description="Unique requirement identifier")
    description: str = Field(..., description="Full description of the requirement")
    guidance: str = Field(default="", description="Implementation guidance for the requirement")


class RequirementResponse(RequirementBase):
    """Schema for requirement response with additional metadata."""

    control_id: str = Field(..., description="ID of the parent control")
    framework_id: str = Field(..., description="ID of the parent framework")

    model_config = {"from_attributes": True}


class ControlBase(BaseModel):
    """Base schema for a compliance control."""

    id: str = Field(..., description="Unique control identifier (e.g., 'ID.AM-1')")
    name: str = Field(..., description="Short name or title of the control")
    description: str = Field(..., description="Full description of the control requirement")
    requirements: list[RequirementBase] = Field(
        default_factory=list, description="Specific requirements within this control"
    )


class ControlResponse(ControlBase):
    """Schema for control response with additional metadata."""

    category_id: str = Field(..., description="ID of the parent category")
    framework_id: str = Field(..., description="ID of the parent framework")

    model_config = {"from_attributes": True}


class ControlMappingResponse(BaseModel):
    """Schema for control mapping between frameworks."""

    source_framework_id: str = Field(..., description="Source framework identifier")
    source_control_id: str = Field(..., description="Source control identifier")
    target_framework_id: str = Field(..., description="Target framework identifier")
    target_control_id: str = Field(..., description="Target control identifier")
    mapping_type: Literal["equivalent", "partial", "related"] = Field(
        ..., description="Type of mapping relationship"
    )
    notes: str | None = Field(default=None, description="Additional notes about the mapping")

    model_config = {"from_attributes": True}


class CategoryBase(BaseModel):
    """Base schema for a compliance category/domain."""

    id: str = Field(..., description="Unique category identifier (e.g., 'ID' for Identify)")
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")


class CategoryResponse(CategoryBase):
    """Schema for category response with controls."""

    framework_id: str = Field(..., description="ID of the parent framework")
    controls: list[ControlBase] = Field(default_factory=list, description="Controls in this category")

    model_config = {"from_attributes": True}


class FrameworkBase(BaseModel):
    """Base schema for a compliance framework."""

    id: str = Field(..., description="Unique framework identifier (e.g., 'nist_csf')")
    name: str = Field(..., description="Full framework name")
    version: str = Field(..., description="Framework version")
    description: str = Field(..., description="Framework description")
    organization: str = Field(..., description="Organization that publishes the framework")


class FrameworkSummary(FrameworkBase):
    """Schema for framework summary (list view)."""

    category_count: int = Field(..., description="Number of categories/domains")
    control_count: int = Field(..., description="Total number of controls")

    model_config = {"from_attributes": True}


class FrameworkResponse(FrameworkBase):
    """Schema for full framework response with categories and controls."""

    categories: list[CategoryResponse] = Field(
        default_factory=list, description="Categories/domains in the framework"
    )

    model_config = {"from_attributes": True}


class FrameworkListResponse(BaseModel):
    """Schema for paginated framework list response."""

    data: list[FrameworkSummary]
    total: int


class ControlSearchQuery(BaseModel):
    """Schema for control search request."""

    query: str = Field(..., min_length=2, description="Search query text")
    framework_ids: list[str] | None = Field(
        default=None, description="Filter by specific framework IDs"
    )
    limit: int = Field(default=50, ge=1, le=200, description="Maximum results to return")


class ControlSearchResult(BaseModel):
    """Schema for a single control search result."""

    framework_id: str
    framework_name: str
    category_id: str
    category_name: str
    control: ControlBase
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Search relevance score")


class ControlSearchResponse(BaseModel):
    """Schema for control search response."""

    query: str
    results: list[ControlSearchResult]
    total: int
