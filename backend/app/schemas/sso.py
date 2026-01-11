"""Pydantic schemas for SSO/SAML 2.0 integration."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class SSOProvider(str, Enum):
    """Supported SSO/SAML identity providers."""

    AZURE_AD = "azure_ad"
    OKTA = "okta"
    GOOGLE = "google"
    ONELOGIN = "onelogin"
    CUSTOM = "custom"


class AttributeMapping(BaseModel):
    """SAML attribute mapping configuration.

    Maps SAML assertion attributes to user fields.
    """

    email: str = Field(
        default="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
        description="SAML attribute for user email",
    )
    first_name: str = Field(
        default="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
        description="SAML attribute for first name",
    )
    last_name: str = Field(
        default="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
        description="SAML attribute for last name",
    )
    groups: str | None = Field(
        default=None,
        description="SAML attribute for group membership",
    )


class SSOConfigBase(BaseModel):
    """Base schema for SSO configuration."""

    provider: SSOProvider = Field(
        default=SSOProvider.CUSTOM,
        description="SSO identity provider type",
    )
    enabled: bool = Field(
        default=False,
        description="Whether SSO is enabled for the organization",
    )

    # IdP Configuration
    idp_entity_id: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Identity Provider Entity ID",
    )
    idp_sso_url: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Identity Provider SSO URL",
    )
    idp_slo_url: str | None = Field(
        default=None,
        max_length=500,
        description="Identity Provider Single Logout URL (optional)",
    )
    idp_x509_cert: str = Field(
        ...,
        min_length=1,
        description="Identity Provider X.509 certificate (PEM format)",
    )

    # Security Options
    want_assertions_signed: bool = Field(
        default=True,
        description="Require SAML assertions to be signed",
    )
    want_response_signed: bool = Field(
        default=True,
        description="Require SAML response to be signed",
    )

    # Attribute Mapping
    attribute_mapping: AttributeMapping | None = Field(
        default=None,
        description="SAML attribute to user field mapping",
    )

    @field_validator("idp_x509_cert")
    @classmethod
    def validate_certificate(cls, v: str) -> str:
        """Validate that the certificate looks like a PEM certificate."""
        cert = v.strip()
        if not cert.startswith("-----BEGIN CERTIFICATE-----"):
            if not cert.startswith("MII"):
                raise ValueError(
                    "Certificate must be in PEM format or base64-encoded DER"
                )
        return cert


class SSOConfigCreate(SSOConfigBase):
    """Schema for creating SSO configuration."""

    pass


class SSOConfigUpdate(BaseModel):
    """Schema for updating SSO configuration."""

    provider: SSOProvider | None = None
    enabled: bool | None = None
    idp_entity_id: str | None = Field(default=None, max_length=500)
    idp_sso_url: str | None = Field(default=None, max_length=500)
    idp_slo_url: str | None = Field(default=None, max_length=500)
    idp_x509_cert: str | None = None
    want_assertions_signed: bool | None = None
    want_response_signed: bool | None = None
    attribute_mapping: AttributeMapping | None = None


class SSOConfigResponse(BaseModel):
    """Schema for SSO configuration response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    provider: str
    enabled: bool

    # IdP Configuration (certificate redacted for security)
    idp_entity_id: str
    idp_sso_url: str
    idp_slo_url: str | None

    # SP Configuration
    sp_entity_id: str
    sp_acs_url: str

    # Security Options
    want_assertions_signed: bool
    want_response_signed: bool

    # Attribute Mapping
    attribute_mapping: dict | None

    # Timestamps
    created_at: datetime
    updated_at: datetime


class SSOMetadataResponse(BaseModel):
    """Schema for SP metadata XML response."""

    metadata_xml: str = Field(
        ...,
        description="Service Provider SAML metadata XML",
    )
    entity_id: str = Field(
        ...,
        description="Service Provider Entity ID",
    )
    acs_url: str = Field(
        ...,
        description="Assertion Consumer Service URL",
    )


class SSOLoginRequest(BaseModel):
    """Schema for initiating SSO login."""

    relay_state: str | None = Field(
        default=None,
        description="URL to redirect to after successful SSO login",
    )


class SSOLoginResponse(BaseModel):
    """Schema for SSO login initiation response."""

    redirect_url: str = Field(
        ...,
        description="URL to redirect user to IdP for authentication",
    )
    saml_request: str | None = Field(
        default=None,
        description="Base64-encoded SAML AuthnRequest (for debugging)",
    )


class SAMLUserAttributes(BaseModel):
    """Extracted user attributes from SAML assertion."""

    email: str
    first_name: str | None = None
    last_name: str | None = None
    groups: list[str] | None = None
    raw_attributes: dict = Field(
        default_factory=dict,
        description="All raw attributes from SAML assertion",
    )


class SSOCallbackResponse(BaseModel):
    """Schema for SSO callback response after successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    is_new_user: bool = Field(
        default=False,
        description="Whether the user was just created via SSO",
    )


class SSOErrorResponse(BaseModel):
    """Schema for SSO error response."""

    error: str
    error_description: str | None = None
    relay_state: str | None = None


class SSOStatusResponse(BaseModel):
    """Schema for SSO status check response."""

    sso_enabled: bool
    provider: str | None = None
    idp_entity_id: str | None = None
    login_url: str | None = Field(
        default=None,
        description="URL to initiate SSO login",
    )
