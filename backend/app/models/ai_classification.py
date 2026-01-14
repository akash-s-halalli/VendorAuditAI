"""AI Tool Classification models for categorizing AI vendors by stack type and capabilities."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vendor import Vendor


class AIStackType(str, Enum):
    """Classification of AI tool by its position in the AI stack."""

    FOUNDATION_MODEL = "foundation_model"
    GENAI_APPLICATION = "genai_application"
    INFERENCE_OPTIMIZATION = "inference_optimization"
    FINE_TUNING_PLATFORM = "fine_tuning_platform"
    AUTONOMOUS_AGENT = "autonomous_agent"
    HORIZONTAL_LAYER = "horizontal_layer"
    EMBEDDING_SERVICE = "embedding_service"
    MLOPS_PLATFORM = "mlops_platform"
    NOT_AI_TOOL = "not_ai_tool"


class AutonomyLevel(str, Enum):
    """Level of autonomous capability the AI tool has."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BlastRadius(str, Enum):
    """Potential impact scope if the AI tool is compromised or misbehaves."""

    MINIMAL = "minimal"
    LIMITED = "limited"
    SIGNIFICANT = "significant"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


class ClassificationMethod(str, Enum):
    """How the classification was determined."""

    MANUAL = "manual"
    AI_ASSISTED = "ai_assisted"
    AUTO_DETECTED = "auto_detected"


class AIToolClassification(Base, UUIDMixin, TimestampMixin):
    """Classification of an AI vendor/tool by stack type and capabilities.

    This extends the existing vendor model with AI-specific risk factors
    identified by Yunus at DoorDash:
    - Stack type classification (8 types)
    - Credential access flags
    - Autonomous action capabilities
    - Blast radius scoring
    - Data training flags
    """

    __tablename__ = "ai_tool_classifications"

    # Foreign Keys
    vendor_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # AI Stack Type Classification
    stack_type: Mapped[str] = mapped_column(
        String(50),
        default=AIStackType.NOT_AI_TOOL.value,
        nullable=False,
    )

    # Capability Flags
    has_credential_access: Mapped[bool] = mapped_column(Boolean, default=False)
    has_autonomous_actions: Mapped[bool] = mapped_column(Boolean, default=False)
    has_data_training: Mapped[bool] = mapped_column(Boolean, default=False)
    has_external_integrations: Mapped[bool] = mapped_column(Boolean, default=False)
    has_code_execution: Mapped[bool] = mapped_column(Boolean, default=False)

    # Credential Details (stored as JSON string)
    credential_types: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: ['oauth', 'api_key', 'service_account']
    credential_scope: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: what the credentials can access

    # Autonomous Action Details (stored as JSON string)
    action_types: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: ['send_email', 'modify_data', 'create_resources']
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, default=True)

    # Data Handling
    data_access_types: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: ['read', 'write', 'delete', 'export']
    data_retention_policy: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trains_on_customer_data: Mapped[bool] = mapped_column(Boolean, default=False)
    data_sharing_third_parties: Mapped[bool] = mapped_column(Boolean, default=False)

    # Risk Assessment (AI-specific, different from vendor risk_level)
    autonomy_level: Mapped[str | None] = mapped_column(
        String(20),
        default=AutonomyLevel.NONE.value,
    )
    blast_radius: Mapped[str | None] = mapped_column(
        String(20),
        default=BlastRadius.MINIMAL.value,
    )
    ai_risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100

    # Classification Metadata
    classification_method: Mapped[str] = mapped_column(
        String(20),
        default=ClassificationMethod.MANUAL.value,
    )
    classification_confidence: Mapped[float | None] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )  # 0.00-1.00
    classified_by_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    classified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Additional notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    vendor: Mapped["Vendor"] = relationship(
        "Vendor",
        back_populates="ai_classification",
    )
    classified_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[classified_by_id],
    )
    capabilities: Mapped[list["AIToolCapability"]] = relationship(
        "AIToolCapability",
        back_populates="classification",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<AIToolClassification(vendor_id={self.vendor_id}, stack_type={self.stack_type})>"


class AIToolCapability(Base, UUIDMixin, TimestampMixin):
    """Detailed capability of an AI tool for granular risk assessment."""

    __tablename__ = "ai_tool_capabilities"

    # Foreign Keys
    classification_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_tool_classifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Capability Details
    capability_category: Mapped[str] = mapped_column(String(100), nullable=False)
    capability_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Evidence
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    documentation_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationship
    classification: Mapped["AIToolClassification"] = relationship(
        "AIToolClassification",
        back_populates="capabilities",
    )

    def __repr__(self) -> str:
        return f"<AIToolCapability(name={self.capability_name}, risk={self.risk_level})>"
