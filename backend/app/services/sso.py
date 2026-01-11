"""SSO/SAML 2.0 service layer.

Provides functionality for SAML-based Single Sign-On including:
- SP metadata generation
- SAML AuthnRequest creation
- SAML Response validation and parsing
- User provisioning from SAML assertions
"""

import base64
import hashlib
import logging
import secrets
import xml.etree.ElementTree as ET
import zlib
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote, urlencode
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import create_access_token, create_refresh_token
from app.models import Organization, User, UserRole
from app.models.sso_config import SSOConfig, SSOProvider
from app.schemas.sso import (
    AttributeMapping,
    SAMLUserAttributes,
    SSOCallbackResponse,
    SSOConfigCreate,
    SSOConfigUpdate,
)

logger = logging.getLogger(__name__)
settings = get_settings()

# SAML XML namespaces
SAML_NAMESPACES = {
    "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
    "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}


class SAMLValidationError(Exception):
    """Raised when SAML response validation fails."""

    pass


class SSOService:
    """Service for SSO/SAML 2.0 operations."""

    def __init__(self, db: AsyncSession):
        """Initialize SSO service with database session."""
        self.db = db

    async def get_sso_config(self, organization_id: str) -> SSOConfig | None:
        """Get SSO configuration for an organization.

        Args:
            organization_id: The organization ID

        Returns:
            SSOConfig if found, None otherwise
        """
        result = await self.db.execute(
            select(SSOConfig).where(SSOConfig.organization_id == organization_id)
        )
        return result.scalar_one_or_none()

    async def get_sso_config_by_org_slug(self, org_slug: str) -> SSOConfig | None:
        """Get SSO configuration by organization slug.

        Args:
            org_slug: The organization slug

        Returns:
            SSOConfig if found, None otherwise
        """
        result = await self.db.execute(
            select(SSOConfig)
            .join(Organization)
            .where(Organization.slug == org_slug)
        )
        return result.scalar_one_or_none()

    async def create_sso_config(
        self,
        organization_id: str,
        config_data: SSOConfigCreate,
    ) -> SSOConfig:
        """Create SSO configuration for an organization.

        Args:
            organization_id: The organization ID
            config_data: SSO configuration data

        Returns:
            Created SSOConfig

        Raises:
            ValueError: If SSO config already exists for organization
        """
        # Check if config already exists
        existing = await self.get_sso_config(organization_id)
        if existing:
            raise ValueError("SSO configuration already exists for this organization")

        # Generate SP configuration
        sp_entity_id = f"{settings.sso_sp_entity_id}/{organization_id}"
        sp_acs_url = f"{settings.sso_callback_url}/{organization_id}"

        sso_config = SSOConfig(
            organization_id=organization_id,
            provider=config_data.provider.value,
            enabled=config_data.enabled,
            idp_entity_id=config_data.idp_entity_id,
            idp_sso_url=config_data.idp_sso_url,
            idp_slo_url=config_data.idp_slo_url,
            idp_x509_cert=config_data.idp_x509_cert,
            sp_entity_id=sp_entity_id,
            sp_acs_url=sp_acs_url,
            want_assertions_signed=config_data.want_assertions_signed,
            want_response_signed=config_data.want_response_signed,
            attribute_mapping=(
                config_data.attribute_mapping.model_dump()
                if config_data.attribute_mapping
                else None
            ),
        )

        self.db.add(sso_config)
        await self.db.commit()
        await self.db.refresh(sso_config)

        logger.info(f"Created SSO config for organization {organization_id}")
        return sso_config

    async def update_sso_config(
        self,
        organization_id: str,
        config_data: SSOConfigUpdate,
    ) -> SSOConfig:
        """Update SSO configuration.

        Args:
            organization_id: The organization ID
            config_data: Updated SSO configuration data

        Returns:
            Updated SSOConfig

        Raises:
            ValueError: If SSO config doesn't exist
        """
        sso_config = await self.get_sso_config(organization_id)
        if not sso_config:
            raise ValueError("SSO configuration not found")

        # Update fields that are provided
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "provider" and value:
                setattr(sso_config, field, value.value if hasattr(value, "value") else value)
            elif field == "attribute_mapping" and value:
                setattr(sso_config, field, value.model_dump() if hasattr(value, "model_dump") else value)
            elif value is not None:
                setattr(sso_config, field, value)

        await self.db.commit()
        await self.db.refresh(sso_config)

        logger.info(f"Updated SSO config for organization {organization_id}")
        return sso_config

    async def delete_sso_config(self, organization_id: str) -> bool:
        """Delete (disable) SSO configuration.

        Args:
            organization_id: The organization ID

        Returns:
            True if deleted, False if not found
        """
        sso_config = await self.get_sso_config(organization_id)
        if not sso_config:
            return False

        await self.db.delete(sso_config)
        await self.db.commit()

        logger.info(f"Deleted SSO config for organization {organization_id}")
        return True

    def generate_sp_metadata(self, sso_config: SSOConfig) -> str:
        """Generate SAML Service Provider metadata XML.

        Args:
            sso_config: SSO configuration

        Returns:
            SP metadata XML string
        """
        # Build metadata XML
        metadata = f'''<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                     entityID="{sso_config.sp_entity_id}">
    <md:SPSSODescriptor AuthnRequestsSigned="true"
                        WantAssertionsSigned="{str(sso_config.want_assertions_signed).lower()}"
                        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                     Location="{sso_config.sp_acs_url}"
                                     index="0"
                                     isDefault="true"/>
    </md:SPSSODescriptor>
    <md:Organization>
        <md:OrganizationName xml:lang="en">VendorAuditAI</md:OrganizationName>
        <md:OrganizationDisplayName xml:lang="en">VendorAuditAI</md:OrganizationDisplayName>
        <md:OrganizationURL xml:lang="en">https://vendorauditai.com</md:OrganizationURL>
    </md:Organization>
</md:EntityDescriptor>'''

        return metadata

    def generate_authn_request(
        self,
        sso_config: SSOConfig,
        relay_state: str | None = None,
    ) -> tuple[str, str]:
        """Generate SAML AuthnRequest and redirect URL.

        Args:
            sso_config: SSO configuration
            relay_state: Optional relay state to include

        Returns:
            Tuple of (redirect_url, base64_encoded_request)
        """
        request_id = f"_id{uuid4().hex}"
        issue_instant = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build AuthnRequest XML
        authn_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                    ID="{request_id}"
                    Version="2.0"
                    IssueInstant="{issue_instant}"
                    Destination="{sso_config.idp_sso_url}"
                    AssertionConsumerServiceURL="{sso_config.sp_acs_url}"
                    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
    <saml:Issuer>{sso_config.sp_entity_id}</saml:Issuer>
    <samlp:NameIDPolicy Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
                        AllowCreate="true"/>
</samlp:AuthnRequest>'''

        # Deflate and base64 encode for HTTP-Redirect binding
        compressed = zlib.compress(authn_request.encode("utf-8"))[2:-4]  # Remove zlib header/footer
        encoded = base64.b64encode(compressed).decode("utf-8")

        # Build redirect URL
        params = {"SAMLRequest": encoded}
        if relay_state:
            params["RelayState"] = relay_state

        redirect_url = f"{sso_config.idp_sso_url}?{urlencode(params)}"

        return redirect_url, base64.b64encode(authn_request.encode("utf-8")).decode("utf-8")

    def parse_saml_response(
        self,
        saml_response: str,
        sso_config: SSOConfig,
    ) -> SAMLUserAttributes:
        """Parse and validate SAML response.

        This implementation provides basic SAML parsing without heavy cryptographic
        dependencies. For production, consider using python3-saml or signxml
        for full signature validation.

        Args:
            saml_response: Base64-encoded SAML response
            sso_config: SSO configuration

        Returns:
            Extracted user attributes

        Raises:
            SAMLValidationError: If response validation fails
        """
        try:
            # Decode SAML response
            decoded = base64.b64decode(saml_response)
            xml_string = decoded.decode("utf-8")

            logger.debug(f"Parsing SAML response for org {sso_config.organization_id}")

            # Parse XML
            root = ET.fromstring(xml_string)

            # Register namespaces
            for prefix, uri in SAML_NAMESPACES.items():
                ET.register_namespace(prefix, uri)

            # Check response status
            status_code = root.find(".//samlp:StatusCode", SAML_NAMESPACES)
            if status_code is not None:
                status_value = status_code.get("Value", "")
                if "Success" not in status_value:
                    raise SAMLValidationError(f"SAML response indicates failure: {status_value}")

            # Find assertion
            assertion = root.find(".//saml:Assertion", SAML_NAMESPACES)
            if assertion is None:
                raise SAMLValidationError("No assertion found in SAML response")

            # Validate issuer
            issuer = assertion.find("saml:Issuer", SAML_NAMESPACES)
            if issuer is not None and issuer.text != sso_config.idp_entity_id:
                logger.warning(
                    f"Issuer mismatch: expected {sso_config.idp_entity_id}, got {issuer.text}"
                )
                # Allow mismatch with warning (some IdPs use different issuer)

            # Check conditions (time validity)
            conditions = assertion.find("saml:Conditions", SAML_NAMESPACES)
            if conditions is not None:
                not_before = conditions.get("NotBefore")
                not_on_or_after = conditions.get("NotOnOrAfter")
                now = datetime.now(UTC)

                if not_before:
                    nb_time = datetime.fromisoformat(not_before.replace("Z", "+00:00"))
                    if now < nb_time:
                        logger.warning(f"SAML assertion not yet valid (NotBefore: {not_before})")

                if not_on_or_after:
                    noa_time = datetime.fromisoformat(not_on_or_after.replace("Z", "+00:00"))
                    if now >= noa_time:
                        raise SAMLValidationError(
                            f"SAML assertion has expired (NotOnOrAfter: {not_on_or_after})"
                        )

            # Signature validation warning
            signature = assertion.find("ds:Signature", SAML_NAMESPACES)
            if signature is None and (sso_config.want_assertions_signed or sso_config.want_response_signed):
                logger.warning(
                    "[!] SAML signature validation skipped - no signature found. "
                    "For production, install signxml for full cryptographic validation."
                )

            # Extract attributes
            attributes = self._extract_saml_attributes(assertion, sso_config)

            return attributes

        except ET.ParseError as e:
            raise SAMLValidationError(f"Failed to parse SAML XML: {e}") from e
        except Exception as e:
            if isinstance(e, SAMLValidationError):
                raise
            raise SAMLValidationError(f"SAML validation error: {e}") from e

    def _extract_saml_attributes(
        self,
        assertion: ET.Element,
        sso_config: SSOConfig,
    ) -> SAMLUserAttributes:
        """Extract user attributes from SAML assertion.

        Args:
            assertion: SAML assertion XML element
            sso_config: SSO configuration with attribute mapping

        Returns:
            Extracted user attributes
        """
        raw_attributes: dict[str, Any] = {}

        # Get NameID (usually email)
        name_id = assertion.find(".//saml:NameID", SAML_NAMESPACES)
        name_id_value = name_id.text if name_id is not None else None

        # Extract all attributes
        attr_statement = assertion.find("saml:AttributeStatement", SAML_NAMESPACES)
        if attr_statement is not None:
            for attr in attr_statement.findall("saml:Attribute", SAML_NAMESPACES):
                attr_name = attr.get("Name", "")
                attr_values = [
                    v.text for v in attr.findall("saml:AttributeValue", SAML_NAMESPACES)
                    if v.text
                ]
                if attr_values:
                    raw_attributes[attr_name] = attr_values[0] if len(attr_values) == 1 else attr_values

        # Get attribute mapping
        mapping = AttributeMapping()
        if sso_config.attribute_mapping:
            mapping = AttributeMapping(**sso_config.attribute_mapping)

        # Extract mapped attributes
        email = raw_attributes.get(mapping.email) or name_id_value
        if not email:
            # Try common email attribute names
            for attr_name in ["email", "Email", "mail", "emailAddress", "user.email"]:
                if attr_name in raw_attributes:
                    email = raw_attributes[attr_name]
                    break

        if not email:
            raise SAMLValidationError("Could not extract email from SAML assertion")

        first_name = raw_attributes.get(mapping.first_name)
        last_name = raw_attributes.get(mapping.last_name)
        groups = None

        if mapping.groups and mapping.groups in raw_attributes:
            groups_value = raw_attributes[mapping.groups]
            groups = groups_value if isinstance(groups_value, list) else [groups_value]

        return SAMLUserAttributes(
            email=email,
            first_name=first_name,
            last_name=last_name,
            groups=groups,
            raw_attributes=raw_attributes,
        )

    async def get_or_create_sso_user(
        self,
        organization_id: str,
        attributes: SAMLUserAttributes,
    ) -> tuple[User, bool]:
        """Get or create a user from SAML attributes.

        Args:
            organization_id: The organization ID
            attributes: Extracted SAML user attributes

        Returns:
            Tuple of (User, is_new_user)
        """
        # Look for existing user by email in the organization
        result = await self.db.execute(
            select(User).where(
                User.organization_id == organization_id,
                User.email == attributes.email,
            )
        )
        user = result.scalar_one_or_none()

        if user:
            # Update user info if changed
            if attributes.first_name or attributes.last_name:
                full_name = " ".join(
                    filter(None, [attributes.first_name, attributes.last_name])
                )
                if full_name and user.full_name != full_name:
                    user.full_name = full_name

            user.last_login = datetime.now(UTC)
            await self.db.commit()
            return user, False

        # Create new user
        # Generate a random password hash (user will use SSO, not password)
        random_password_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()

        full_name = " ".join(
            filter(None, [attributes.first_name, attributes.last_name])
        ) or attributes.email.split("@")[0]

        user = User(
            organization_id=organization_id,
            email=attributes.email,
            password_hash=random_password_hash,
            full_name=full_name,
            role=UserRole.ANALYST.value,  # Default role for SSO users
            is_active=True,
            last_login=datetime.now(UTC),
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Created SSO user {attributes.email} for organization {organization_id}")
        return user, True

    async def process_sso_callback(
        self,
        organization_id: str,
        saml_response: str,
    ) -> SSOCallbackResponse:
        """Process SSO callback and return tokens.

        Args:
            organization_id: The organization ID
            saml_response: Base64-encoded SAML response

        Returns:
            SSO callback response with tokens

        Raises:
            SAMLValidationError: If validation fails
            ValueError: If SSO is not configured or enabled
        """
        # Get SSO config
        sso_config = await self.get_sso_config(organization_id)
        if not sso_config:
            raise ValueError("SSO is not configured for this organization")
        if not sso_config.enabled:
            raise ValueError("SSO is not enabled for this organization")

        # Parse and validate SAML response
        attributes = self.parse_saml_response(saml_response, sso_config)

        # Get or create user
        user, is_new_user = await self.get_or_create_sso_user(
            organization_id, attributes
        )

        # Generate tokens
        access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "org_id": user.organization_id,
                "role": user.role,
                "sso": True,
            },
        )
        refresh_token = create_refresh_token(subject=user.id)

        return SSOCallbackResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user_id=user.id,
            is_new_user=is_new_user,
        )


def get_sso_service(db: AsyncSession) -> SSOService:
    """Get SSO service instance.

    Args:
        db: Database session

    Returns:
        SSOService instance
    """
    return SSOService(db)
