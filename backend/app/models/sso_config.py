"""SSO Configuration model for SAML 2.0 integration."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class SSOProvider(str, Enum):
    """Supported SSO/SAML identity providers."""

    AZURE_AD = "azure_ad"
    OKTA = "okta"
    GOOGLE = "google"
    ONELOGIN = "onelogin"
    CUSTOM = "custom"


class SSOConfig(Base, UUIDMixin, TimestampMixin):
    """SSO/SAML 2.0 configuration for an organization.

    Each organization can have one SSO configuration that defines
    the SAML identity provider settings and attribute mappings.
    """

    __tablename__ = "sso_configs"

    # Foreign key to organization (one SSO config per org)
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Provider type
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=SSOProvider.CUSTOM.value,
    )

    # SSO enabled status
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Identity Provider (IdP) Configuration
    idp_entity_id: Mapped[str] = mapped_column(String(500), nullable=False)
    idp_sso_url: Mapped[str] = mapped_column(String(500), nullable=False)
    idp_slo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    idp_x509_cert: Mapped[str] = mapped_column(Text, nullable=False)

    # Service Provider (SP) Configuration
    sp_entity_id: Mapped[str] = mapped_column(String(500), nullable=False)
    sp_acs_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Security Options
    want_assertions_signed: Mapped[bool] = mapped_column(Boolean, default=True)
    want_response_signed: Mapped[bool] = mapped_column(Boolean, default=True)

    # Attribute mapping (JSON)
    # Expected format: {"email": "http://...", "first_name": "...", "last_name": "..."}
    attribute_mapping: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationship
    organization: Mapped["Organization"] = relationship(
        "Organization",
        backref="sso_config",
    )

    def __repr__(self) -> str:
        return (
            f"<SSOConfig(id={self.id}, org_id={self.organization_id}, "
            f"provider={self.provider}, enabled={self.enabled})>"
        )
