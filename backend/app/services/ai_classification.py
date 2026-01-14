"""Service layer for AI Tool Classification."""

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ai_classification import (
    AIToolClassification,
    AIToolCapability,
    AIStackType,
    AutonomyLevel,
    BlastRadius,
    ClassificationMethod,
)
from app.models.vendor import Vendor
from app.schemas.ai_classification import (
    AIClassificationCreate,
    AIClassificationUpdate,
    StackTypeDefinition,
)


# Stack Type Definitions - based on Yunus's DoorDash requirements
STACK_TYPE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "foundation_model": {
        "name": "Foundation Model",
        "description": "Pure LLM provider (GPT, Claude, Gemini, Llama)",
        "examples": ["OpenAI", "Anthropic", "Google AI", "Meta AI"],
        "typical_risks": ["data_training", "prompt_injection", "output_manipulation"],
        "base_risk_score": 40,
        "typical_credential_access": False,
        "typical_autonomous_actions": False,
    },
    "genai_application": {
        "name": "GenAI Application Layer",
        "description": "Application built on top of foundation models",
        "examples": ["Jasper", "Copy.ai", "Notion AI", "Grammarly"],
        "typical_risks": ["data_exposure", "third_party_llm", "prompt_leakage"],
        "base_risk_score": 50,
        "typical_credential_access": False,
        "typical_autonomous_actions": False,
    },
    "autonomous_agent": {
        "name": "Autonomous Agent",
        "description": "AI agents that can take actions with credentials",
        "examples": ["Zapier AI", "Make.com AI", "Microsoft Copilot", "Claude Computer Use"],
        "typical_risks": ["credential_access", "autonomous_actions", "blast_radius"],
        "base_risk_score": 75,
        "typical_credential_access": True,
        "typical_autonomous_actions": True,
    },
    "fine_tuning_platform": {
        "name": "Fine-tuning/Training Platform",
        "description": "Platforms for training or fine-tuning models on your data",
        "examples": ["Weights & Biases", "Hugging Face", "Scale AI"],
        "typical_risks": ["data_training", "model_extraction", "dataset_exposure"],
        "base_risk_score": 60,
        "typical_credential_access": False,
        "typical_autonomous_actions": False,
    },
    "inference_optimization": {
        "name": "Inference Optimization",
        "description": "Tools that optimize LLM inference and deployment",
        "examples": ["Anyscale", "Modal", "Replicate", "Together AI"],
        "typical_risks": ["model_access", "data_caching", "performance_logging"],
        "base_risk_score": 35,
        "typical_credential_access": False,
        "typical_autonomous_actions": False,
    },
    "horizontal_layer": {
        "name": "Horizontal AI Layer",
        "description": "Cross-cutting AI infrastructure and orchestration",
        "examples": ["LangChain", "LlamaIndex", "Semantic Kernel"],
        "typical_risks": ["integration_points", "data_flow", "prompt_storage"],
        "base_risk_score": 45,
        "typical_credential_access": False,
        "typical_autonomous_actions": False,
    },
    "embedding_service": {
        "name": "Embedding/Vector Service",
        "description": "Vector database and embedding generation services",
        "examples": ["Pinecone", "Weaviate", "Chroma", "Milvus"],
        "typical_risks": ["data_storage", "embedding_exposure", "search_leakage"],
        "base_risk_score": 40,
        "typical_credential_access": False,
        "typical_autonomous_actions": False,
    },
    "mlops_platform": {
        "name": "MLOps Platform",
        "description": "ML operations, deployment, and monitoring",
        "examples": ["MLflow", "Kubeflow", "SageMaker", "Vertex AI"],
        "typical_risks": ["model_access", "deployment_control", "data_pipelines"],
        "base_risk_score": 55,
        "typical_credential_access": True,
        "typical_autonomous_actions": False,
    },
    "not_ai_tool": {
        "name": "Not an AI Tool",
        "description": "Vendor is not an AI tool or has no AI capabilities",
        "examples": [],
        "typical_risks": [],
        "base_risk_score": 0,
        "typical_credential_access": False,
        "typical_autonomous_actions": False,
    },
}


def calculate_ai_risk_score(classification: AIToolClassification) -> int:
    """Calculate AI-specific risk score based on classification factors.

    This is DIFFERENT from the generic vendor risk score.
    It considers AI-specific factors like autonomous actions, credential access, etc.
    """
    # Start with base score for stack type
    stack_def = STACK_TYPE_DEFINITIONS.get(classification.stack_type, {})
    base_score = stack_def.get("base_risk_score", 30)

    # Add modifiers for capability flags
    if classification.has_credential_access:
        base_score += 15  # Credentials = higher risk

    if classification.has_autonomous_actions:
        base_score += 20  # Autonomous actions = much higher risk

    if classification.trains_on_customer_data:
        base_score += 10  # Training on data = data exposure risk

    if classification.has_code_execution:
        base_score += 15  # Code execution = high risk

    if classification.has_external_integrations:
        base_score += 5  # External integrations = data flow risk

    if classification.data_sharing_third_parties:
        base_score += 10  # Third party sharing = privacy risk

    # Autonomy level modifier
    autonomy_modifiers = {
        AutonomyLevel.NONE.value: 0,
        AutonomyLevel.LOW.value: 5,
        AutonomyLevel.MEDIUM.value: 10,
        AutonomyLevel.HIGH.value: 15,
        AutonomyLevel.CRITICAL.value: 25,
    }
    base_score += autonomy_modifiers.get(classification.autonomy_level or AutonomyLevel.NONE.value, 0)

    # Blast radius modifier
    blast_modifiers = {
        BlastRadius.MINIMAL.value: 0,
        BlastRadius.LIMITED.value: 5,
        BlastRadius.SIGNIFICANT.value: 10,
        BlastRadius.SEVERE.value: 20,
        BlastRadius.CATASTROPHIC.value: 30,
    }
    base_score += blast_modifiers.get(classification.blast_radius or BlastRadius.MINIMAL.value, 0)

    # Human approval reduces risk slightly
    if classification.requires_human_approval and classification.has_autonomous_actions:
        base_score -= 5

    return min(100, max(0, base_score))


def get_stack_type_definitions() -> list[StackTypeDefinition]:
    """Get all stack type definitions for the frontend."""
    return [
        StackTypeDefinition(
            id=stack_id,
            name=stack_def["name"],
            description=stack_def["description"],
            examples=stack_def["examples"],
            typical_risks=stack_def["typical_risks"],
            base_risk_score=stack_def["base_risk_score"],
            typical_credential_access=stack_def["typical_credential_access"],
            typical_autonomous_actions=stack_def["typical_autonomous_actions"],
        )
        for stack_id, stack_def in STACK_TYPE_DEFINITIONS.items()
    ]


async def get_classification_by_vendor_id(
    db: AsyncSession,
    vendor_id: str,
    org_id: str,
) -> AIToolClassification | None:
    """Get AI classification for a vendor."""
    stmt = (
        select(AIToolClassification)
        .options(selectinload(AIToolClassification.capabilities))
        .where(
            AIToolClassification.vendor_id == vendor_id,
            AIToolClassification.organization_id == org_id,
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_classification_by_id(
    db: AsyncSession,
    classification_id: str,
    org_id: str,
) -> AIToolClassification | None:
    """Get AI classification by ID."""
    stmt = (
        select(AIToolClassification)
        .options(selectinload(AIToolClassification.capabilities))
        .where(
            AIToolClassification.id == classification_id,
            AIToolClassification.organization_id == org_id,
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_classifications(
    db: AsyncSession,
    org_id: str,
    stack_type: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[AIToolClassification], int]:
    """Get all AI classifications for an organization."""
    # Build base query
    base_query = select(AIToolClassification).where(
        AIToolClassification.organization_id == org_id
    )

    if stack_type:
        base_query = base_query.where(AIToolClassification.stack_type == stack_type)

    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results with capabilities
    stmt = (
        base_query
        .options(selectinload(AIToolClassification.capabilities))
        .offset(skip)
        .limit(limit)
        .order_by(AIToolClassification.created_at.desc())
    )
    result = await db.execute(stmt)
    classifications = list(result.scalars().all())

    return classifications, total


async def create_classification(
    db: AsyncSession,
    user_id: str,
    org_id: str,
    classification_data: AIClassificationCreate,
) -> AIToolClassification:
    """Create a new AI classification for a vendor."""
    # Verify vendor exists and belongs to org
    vendor_stmt = select(Vendor).where(
        Vendor.id == classification_data.vendor_id,
        Vendor.organization_id == org_id,
    )
    vendor_result = await db.execute(vendor_stmt)
    vendor = vendor_result.scalar_one_or_none()
    if not vendor:
        raise ValueError("Vendor not found or does not belong to organization")

    # Check if classification already exists
    existing = await get_classification_by_vendor_id(db, classification_data.vendor_id, org_id)
    if existing:
        raise ValueError("Classification already exists for this vendor")

    # Create classification
    classification = AIToolClassification(
        id=str(uuid4()),
        vendor_id=classification_data.vendor_id,
        organization_id=org_id,
        stack_type=classification_data.stack_type,
        has_credential_access=classification_data.has_credential_access,
        has_autonomous_actions=classification_data.has_autonomous_actions,
        has_data_training=classification_data.has_data_training,
        has_external_integrations=classification_data.has_external_integrations,
        has_code_execution=classification_data.has_code_execution,
        credential_types=json.dumps(classification_data.credential_types) if classification_data.credential_types else None,
        credential_scope=json.dumps(classification_data.credential_scope) if classification_data.credential_scope else None,
        action_types=json.dumps(classification_data.action_types) if classification_data.action_types else None,
        requires_human_approval=classification_data.requires_human_approval,
        data_access_types=json.dumps(classification_data.data_access_types) if classification_data.data_access_types else None,
        data_retention_policy=classification_data.data_retention_policy,
        trains_on_customer_data=classification_data.trains_on_customer_data,
        data_sharing_third_parties=classification_data.data_sharing_third_parties,
        autonomy_level=classification_data.autonomy_level,
        blast_radius=classification_data.blast_radius,
        notes=classification_data.notes,
        classification_method=ClassificationMethod.MANUAL.value,
        classified_by_id=user_id,
        classified_at=datetime.now(timezone.utc),
    )

    # Calculate risk score
    classification.ai_risk_score = calculate_ai_risk_score(classification)

    db.add(classification)

    # Add capabilities if provided
    if classification_data.capabilities:
        for cap_data in classification_data.capabilities:
            capability = AIToolCapability(
                id=str(uuid4()),
                classification_id=classification.id,
                capability_category=cap_data.capability_category,
                capability_name=cap_data.capability_name,
                description=cap_data.description,
                risk_level=cap_data.risk_level,
                is_enabled=cap_data.is_enabled,
                evidence=cap_data.evidence,
                documentation_url=cap_data.documentation_url,
            )
            db.add(capability)

    await db.commit()
    await db.refresh(classification)

    # Reload with relationships
    return await get_classification_by_id(db, classification.id, org_id)  # type: ignore


async def update_classification(
    db: AsyncSession,
    classification_id: str,
    org_id: str,
    user_id: str,
    update_data: AIClassificationUpdate,
) -> AIToolClassification | None:
    """Update an existing AI classification."""
    classification = await get_classification_by_id(db, classification_id, org_id)
    if not classification:
        return None

    # Update fields that are provided
    update_dict = update_data.model_dump(exclude_unset=True)

    # Handle JSON fields
    json_fields = ["credential_types", "credential_scope", "action_types", "data_access_types"]
    for field in json_fields:
        if field in update_dict and update_dict[field] is not None:
            update_dict[field] = json.dumps(update_dict[field])

    for key, value in update_dict.items():
        setattr(classification, key, value)

    # Update metadata
    classification.classified_by_id = user_id
    classification.classified_at = datetime.now(timezone.utc)

    # Recalculate risk score
    classification.ai_risk_score = calculate_ai_risk_score(classification)

    await db.commit()
    await db.refresh(classification)

    return classification


async def delete_classification(
    db: AsyncSession,
    classification_id: str,
    org_id: str,
) -> bool:
    """Delete an AI classification."""
    classification = await get_classification_by_id(db, classification_id, org_id)
    if not classification:
        return False

    await db.delete(classification)
    await db.commit()
    return True


async def get_risk_matrix(
    db: AsyncSession,
    org_id: str,
) -> tuple[list[dict], dict[str, int]]:
    """Get risk matrix data for visualization."""
    # Get all classifications with vendor info
    stmt = (
        select(
            AIToolClassification,
            Vendor.name.label("vendor_name"),
        )
        .join(Vendor, AIToolClassification.vendor_id == Vendor.id)
        .where(AIToolClassification.organization_id == org_id)
        .order_by(AIToolClassification.ai_risk_score.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    entries = []
    summary: dict[str, int] = {}

    for row in rows:
        classification = row[0]
        vendor_name = row[1]

        entries.append({
            "vendor_id": classification.vendor_id,
            "vendor_name": vendor_name,
            "stack_type": classification.stack_type,
            "autonomy_level": classification.autonomy_level,
            "blast_radius": classification.blast_radius,
            "ai_risk_score": classification.ai_risk_score,
            "has_credential_access": classification.has_credential_access,
            "has_autonomous_actions": classification.has_autonomous_actions,
        })

        # Count by stack type
        stack = classification.stack_type
        summary[stack] = summary.get(stack, 0) + 1

    return entries, summary


async def add_capability(
    db: AsyncSession,
    classification_id: str,
    org_id: str,
    capability_data: dict,
) -> AIToolCapability | None:
    """Add a capability to a classification."""
    classification = await get_classification_by_id(db, classification_id, org_id)
    if not classification:
        return None

    capability = AIToolCapability(
        id=str(uuid4()),
        classification_id=classification_id,
        capability_category=capability_data["capability_category"],
        capability_name=capability_data["capability_name"],
        description=capability_data.get("description"),
        risk_level=capability_data.get("risk_level", "medium"),
        is_enabled=capability_data.get("is_enabled", True),
        evidence=capability_data.get("evidence"),
        documentation_url=capability_data.get("documentation_url"),
    )

    db.add(capability)
    await db.commit()
    await db.refresh(capability)

    return capability
