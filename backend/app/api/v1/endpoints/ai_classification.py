"""API endpoints for AI Tool Classification."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.schemas.ai_classification import (
    AIClassificationCreate,
    AIClassificationUpdate,
    AIClassificationResponse,
    AIClassificationDetailResponse,
    AIClassificationListResponse,
    AIToolCapabilityCreate,
    AIToolCapabilityResponse,
    RiskMatrixResponse,
    RiskMatrixEntry,
    StackTypeListResponse,
    ClassifyVendorRequest,
)
from app.services import ai_classification as classification_service

router = APIRouter()


@router.get("/stack-types", response_model=StackTypeListResponse)
async def get_stack_types():
    """Get all AI stack type definitions.

    Returns the 8 stack types used for classifying AI tools,
    along with their typical risk factors and examples.
    """
    stack_types = classification_service.get_stack_type_definitions()
    return StackTypeListResponse(stack_types=stack_types)


@router.get("/", response_model=AIClassificationListResponse)
async def list_classifications(
    stack_type: str | None = Query(None, description="Filter by stack type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all AI classifications for the organization.

    Supports filtering by stack type and pagination.
    """
    classifications, total = await classification_service.get_classifications(
        db=db,
        org_id=current_user.organization_id,
        stack_type=stack_type,
        skip=skip,
        limit=limit,
    )

    # Build response with vendor names
    data = []
    for classification in classifications:
        response_dict = {
            "id": classification.id,
            "vendor_id": classification.vendor_id,
            "organization_id": classification.organization_id,
            "stack_type": classification.stack_type,
            "has_credential_access": classification.has_credential_access,
            "has_autonomous_actions": classification.has_autonomous_actions,
            "has_data_training": classification.has_data_training,
            "has_external_integrations": classification.has_external_integrations,
            "has_code_execution": classification.has_code_execution,
            "credential_types": classification.credential_types,
            "credential_scope": classification.credential_scope,
            "action_types": classification.action_types,
            "requires_human_approval": classification.requires_human_approval,
            "data_access_types": classification.data_access_types,
            "data_retention_policy": classification.data_retention_policy,
            "trains_on_customer_data": classification.trains_on_customer_data,
            "data_sharing_third_parties": classification.data_sharing_third_parties,
            "autonomy_level": classification.autonomy_level,
            "blast_radius": classification.blast_radius,
            "ai_risk_score": classification.ai_risk_score,
            "classification_method": classification.classification_method,
            "classification_confidence": float(classification.classification_confidence) if classification.classification_confidence else None,
            "classified_by_id": classification.classified_by_id,
            "classified_at": classification.classified_at,
            "notes": classification.notes,
            "created_at": classification.created_at,
            "updated_at": classification.updated_at,
            "capabilities": [
                {
                    "id": cap.id,
                    "classification_id": cap.classification_id,
                    "capability_category": cap.capability_category,
                    "capability_name": cap.capability_name,
                    "description": cap.description,
                    "risk_level": cap.risk_level,
                    "is_enabled": cap.is_enabled,
                    "evidence": cap.evidence,
                    "documentation_url": cap.documentation_url,
                    "created_at": cap.created_at,
                    "updated_at": cap.updated_at,
                }
                for cap in classification.capabilities
            ],
            "vendor_name": classification.vendor.name if classification.vendor else None,
            "vendor_category": classification.vendor.category if classification.vendor else None,
        }
        data.append(AIClassificationDetailResponse(**response_dict))

    return AIClassificationListResponse(data=data, total=total)


@router.get("/vendor/{vendor_id}", response_model=AIClassificationResponse | None)
async def get_vendor_classification(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get AI classification for a specific vendor.

    Returns the classification details including capabilities,
    or null if vendor has not been classified.
    """
    classification = await classification_service.get_classification_by_vendor_id(
        db=db,
        vendor_id=vendor_id,
        org_id=current_user.organization_id,
    )
    return classification


@router.get("/risk-matrix", response_model=RiskMatrixResponse)
async def get_risk_matrix(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get risk matrix view of all classified vendors.

    Returns a matrix view with vendor names, stack types,
    autonomy levels, blast radius, and risk scores for visualization.
    """
    entries, summary = await classification_service.get_risk_matrix(
        db=db,
        org_id=current_user.organization_id,
    )

    return RiskMatrixResponse(
        entries=[RiskMatrixEntry(**e) for e in entries],
        total=len(entries),
        summary=summary,
    )


@router.post("/", response_model=AIClassificationResponse, status_code=201)
async def create_classification(
    classification_data: AIClassificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new AI classification for a vendor.

    Classifies a vendor by AI stack type, capability flags,
    and risk factors. Automatically calculates AI risk score.
    """
    try:
        classification = await classification_service.create_classification(
            db=db,
            user_id=current_user.id,
            org_id=current_user.organization_id,
            classification_data=classification_data,
        )
        return classification
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{classification_id}", response_model=AIClassificationResponse)
async def update_classification(
    classification_id: str,
    update_data: AIClassificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing AI classification.

    Updates the classification fields and recalculates the risk score.
    """
    classification = await classification_service.update_classification(
        db=db,
        classification_id=classification_id,
        org_id=current_user.organization_id,
        user_id=current_user.id,
        update_data=update_data,
    )
    if not classification:
        raise HTTPException(status_code=404, detail="Classification not found")
    return classification


@router.delete("/{classification_id}", status_code=204)
async def delete_classification(
    classification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an AI classification.

    Removes the classification from a vendor. This does not
    delete the vendor itself.
    """
    deleted = await classification_service.delete_classification(
        db=db,
        classification_id=classification_id,
        org_id=current_user.organization_id,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Classification not found")
    return None


@router.post("/{classification_id}/capabilities", response_model=AIToolCapabilityResponse, status_code=201)
async def add_capability(
    classification_id: str,
    capability_data: AIToolCapabilityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a capability to an existing classification.

    Allows adding granular capability tracking to a classified vendor.
    """
    capability = await classification_service.add_capability(
        db=db,
        classification_id=classification_id,
        org_id=current_user.organization_id,
        capability_data=capability_data.model_dump(),
    )
    if not capability:
        raise HTTPException(status_code=404, detail="Classification not found")
    return capability


@router.post("/classify", response_model=AIClassificationResponse, status_code=201)
async def classify_vendor_assisted(
    request: ClassifyVendorRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AI-assisted classification of a vendor.

    Uses vendor description and context to suggest a classification.
    For now, this creates a manual classification - AI assistance
    can be added as an enhancement.
    """
    # For now, create a basic classification that needs manual review
    # In future: integrate with LLM for auto-classification
    classification_data = AIClassificationCreate(
        vendor_id=request.vendor_id,
        stack_type="not_ai_tool",  # Default, user should update
        notes=f"AI-assisted classification requested. Context: {request.additional_context or 'None provided'}",
    )

    try:
        classification = await classification_service.create_classification(
            db=db,
            user_id=current_user.id,
            org_id=current_user.organization_id,
            classification_data=classification_data,
        )
        return classification
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
