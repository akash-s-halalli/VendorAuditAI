"""Pydantic schemas for vendor risk scoring."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RiskFactor(BaseModel):
    """Individual risk factor contribution to overall score."""

    name: str = Field(..., description="Name of the risk factor")
    description: str = Field(..., description="Description of what this factor measures")
    raw_value: float = Field(..., description="Raw value before weighting")
    weighted_value: float = Field(..., description="Value after applying weight")
    weight: float = Field(..., description="Weight applied to this factor (0.0-1.0)")
    max_possible: float = Field(..., description="Maximum possible contribution")


class RiskScore(BaseModel):
    """Overall risk score for a vendor."""

    vendor_id: str = Field(..., description="Vendor ID")
    vendor_name: str = Field(..., description="Vendor name")
    overall_score: float = Field(
        ..., ge=0, le=100, description="Overall risk score (0-100)"
    )
    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Risk level category"
    )
    risk_color: Literal["green", "yellow", "orange", "red"] = Field(
        ..., description="Risk level color indicator"
    )
    factors: list[RiskFactor] = Field(
        default_factory=list, description="Breakdown of risk factors"
    )
    calculated_at: datetime = Field(..., description="When the score was calculated")

    # Summary statistics
    findings_critical: int = Field(default=0, description="Count of critical findings")
    findings_high: int = Field(default=0, description="Count of high findings")
    findings_medium: int = Field(default=0, description="Count of medium findings")
    findings_low: int = Field(default=0, description="Count of low findings")
    total_findings: int = Field(default=0, description="Total number of findings")
    compliance_coverage: float = Field(
        default=0, ge=0, le=100, description="Compliance coverage percentage"
    )
    vendor_tier: str = Field(default="medium", description="Vendor tier classification")
    data_classification: str | None = Field(
        default=None, description="Data classification sensitivity"
    )
    document_age_days: int | None = Field(
        default=None, description="Age of oldest document in days"
    )

    model_config = {"from_attributes": True}


class RiskScoreListResponse(BaseModel):
    """Response containing list of vendor risk scores."""

    data: list[RiskScore] = Field(..., description="List of risk scores")
    total: int = Field(..., description="Total number of vendors")
    average_score: float = Field(..., description="Average risk score across all vendors")
    high_risk_count: int = Field(
        ..., description="Number of vendors with high/critical risk"
    )


class RiskTrendPoint(BaseModel):
    """Single point in a risk trend."""

    date: datetime = Field(..., description="Date of the measurement")
    score: float = Field(..., ge=0, le=100, description="Risk score at this point")
    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Risk level at this point"
    )


class RiskTrend(BaseModel):
    """Historical risk scores over time for a vendor."""

    vendor_id: str = Field(..., description="Vendor ID")
    vendor_name: str = Field(..., description="Vendor name")
    current_score: float = Field(..., ge=0, le=100, description="Current risk score")
    trend_direction: Literal["improving", "stable", "worsening"] = Field(
        ..., description="Direction of risk trend"
    )
    score_change_30d: float = Field(
        ..., description="Score change over last 30 days (negative = improving)"
    )
    history: list[RiskTrendPoint] = Field(
        default_factory=list, description="Historical score data points"
    )

    model_config = {"from_attributes": True}


class RiskTrendsResponse(BaseModel):
    """Response containing risk trends for all vendors."""

    data: list[RiskTrend] = Field(..., description="List of vendor risk trends")
    total: int = Field(..., description="Total number of vendors")
    overall_trend: Literal["improving", "stable", "worsening"] = Field(
        ..., description="Overall trend across all vendors"
    )
    average_change_30d: float = Field(
        ..., description="Average score change over 30 days"
    )


class RiskCalculationRequest(BaseModel):
    """Request to trigger risk recalculation."""

    vendor_ids: list[str] | None = Field(
        default=None,
        description="Optional list of vendor IDs to recalculate. If None, recalculates all.",
    )
    force: bool = Field(
        default=False,
        description="Force recalculation even if recently calculated",
    )


class RiskCalculationResponse(BaseModel):
    """Response from risk recalculation."""

    vendors_processed: int = Field(..., description="Number of vendors processed")
    calculation_time_ms: float = Field(..., description="Time taken in milliseconds")
    errors: list[str] = Field(
        default_factory=list, description="Any errors encountered"
    )
    message: str = Field(..., description="Summary message")
