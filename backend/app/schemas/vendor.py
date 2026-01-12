"""Pydantic schemas for vendor management."""

from datetime import date, datetime
from typing import Literal

import json

from pydantic import BaseModel, Field, field_validator


class VendorBase(BaseModel):
    """Base vendor schema with common fields."""

    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    website: str | None = Field(default=None, max_length=500)
    tier: Literal["critical", "high", "medium", "low"] | None = None
    status: Literal["active", "inactive", "onboarding", "offboarding"] | None = None
    criticality_score: int | None = Field(default=None, ge=1, le=100)
    data_classification: str | None = None
    tags: list[str] | None = None
    category: str | None = Field(default=None, max_length=50)


class VendorCreate(VendorBase):
    """Schema for creating a new vendor."""

    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    website: str | None = Field(default=None, max_length=500)
    tier: Literal["critical", "high", "medium", "low"] | None = "medium"
    status: Literal["active", "inactive", "onboarding", "offboarding"] | None = "onboarding"
    criticality_score: int | None = Field(default=None, ge=1, le=100)
    data_classification: str | None = None
    tags: list[str] | None = Field(default_factory=list)
    category: str | None = Field(default=None, max_length=50)


class VendorUpdate(BaseModel):
    """Schema for updating a vendor (partial updates)."""

    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    website: str | None = Field(default=None, max_length=500)
    tier: Literal["critical", "high", "medium", "low"] | None = None
    status: Literal["active", "inactive", "onboarding", "offboarding"] | None = None
    criticality_score: int | None = Field(default=None, ge=1, le=100)
    data_classification: str | None = None
    tags: list[str] | None = None
    category: str | None = Field(default=None, max_length=50)


class VendorResponse(VendorBase):
    """Schema for vendor response."""

    id: str
    organization_id: str
    contract_expiry: date | None = None
    last_assessed: datetime | None = None
    next_assessment_due: date | None = None
    created_at: datetime
    updated_at: datetime
    # Auto-categorization fields
    recommended_frameworks: list[str] | None = None
    data_types: list[str] | None = None
    categorization_confidence: float | None = None

    model_config = {"from_attributes": True}

    @field_validator("recommended_frameworks", "data_types", "tags", mode="before")
    @classmethod
    def parse_json_list(cls, v: str | list | None) -> list[str] | None:
        """Parse JSON string to list if needed."""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return None


class VendorListResponse(BaseModel):
    """Schema for paginated vendor list response."""

    data: list[VendorResponse]
    total: int
    page: int
    limit: int
