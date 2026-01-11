"""Tests for SSO/SAML 2.0 API endpoints."""

import base64
import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from app.models.sso_config import SSOConfig, SSOProvider
from tests.conftest import get_auth_token


# Sample X.509 certificate for testing (self-signed, not for production)
SAMPLE_X509_CERT = """-----BEGIN CERTIFICATE-----
MIICpDCCAYwCCQDU+pQ4L5qE5jANBgkqhkiG9w0BAQsFADAUMRIwEAYDVQQDDAls
b2NhbGhvc3QwHhcNMjQwMTAxMDAwMDAwWhcNMjUwMTAxMDAwMDAwWjAUMRIwEAYD
VQQDDAlsb2NhbGhvc3QwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDJ
a9XYz4z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5
z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5
z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5
z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5
z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5zAgMBAAEw
DQYJKoZIhvcNAQELBQADggEBAKTEST123456789012345678901234567890123456
-----END CERTIFICATE-----"""


@pytest_asyncio.fixture(scope="function")
async def test_sso_config(
    db_session: AsyncSession,
    test_organization: Organization,
) -> SSOConfig:
    """Create a test SSO configuration."""
    sso_config = SSOConfig(
        id=str(uuid.uuid4()),
        organization_id=test_organization.id,
        provider=SSOProvider.OKTA.value,
        enabled=True,
        idp_entity_id="https://idp.example.com/entity",
        idp_sso_url="https://idp.example.com/sso",
        idp_slo_url="https://idp.example.com/slo",
        idp_x509_cert=SAMPLE_X509_CERT,
        sp_entity_id=f"https://vendorauditai.com/sso/{test_organization.id}",
        sp_acs_url=f"https://vendorauditai.com/api/v1/sso/acs/{test_organization.id}",
        want_assertions_signed=True,
        want_response_signed=True,
        attribute_mapping={
            "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
            "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
            "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
        },
    )
    db_session.add(sso_config)
    await db_session.commit()
    await db_session.refresh(sso_config)
    return sso_config


@pytest_asyncio.fixture(scope="function")
async def disabled_sso_config(
    db_session: AsyncSession,
    test_organization: Organization,
) -> SSOConfig:
    """Create a disabled SSO configuration."""
    sso_config = SSOConfig(
        id=str(uuid.uuid4()),
        organization_id=test_organization.id,
        provider=SSOProvider.OKTA.value,
        enabled=False,  # Disabled
        idp_entity_id="https://idp.example.com/entity",
        idp_sso_url="https://idp.example.com/sso",
        idp_x509_cert=SAMPLE_X509_CERT,
        sp_entity_id=f"https://vendorauditai.com/sso/{test_organization.id}",
        sp_acs_url=f"https://vendorauditai.com/api/v1/sso/acs/{test_organization.id}",
    )
    db_session.add(sso_config)
    await db_session.commit()
    await db_session.refresh(sso_config)
    return sso_config


class TestSSOPublicEndpoints:
    """Tests for public SSO endpoints (no authentication required)."""

    @pytest.mark.asyncio
    async def test_get_sso_status_enabled(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
        test_sso_config: SSOConfig,
    ):
        """Test SSO status returns enabled status when configured."""
        response = await async_client.get(f"/api/v1/sso/status/{test_organization.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["sso_enabled"] is True
        assert data["provider"] == "okta"
        assert data["idp_entity_id"] == "https://idp.example.com/entity"
        assert data["login_url"] == f"/api/v1/sso/login/{test_organization.id}"

    @pytest.mark.asyncio
    async def test_get_sso_status_disabled(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
        disabled_sso_config: SSOConfig,
    ):
        """Test SSO status returns disabled when SSO is disabled."""
        response = await async_client.get(f"/api/v1/sso/status/{test_organization.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["sso_enabled"] is False
        assert data["provider"] is None
        assert data["login_url"] is None

    @pytest.mark.asyncio
    async def test_get_sso_status_not_configured(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
    ):
        """Test SSO status returns not enabled when not configured."""
        response = await async_client.get(f"/api/v1/sso/status/{test_organization.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["sso_enabled"] is False

    @pytest.mark.asyncio
    async def test_get_sp_metadata(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
        test_sso_config: SSOConfig,
    ):
        """Test SP metadata endpoint returns valid XML."""
        response = await async_client.get(
            f"/api/v1/sso/metadata/{test_organization.id}"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/xml"

        # Verify XML contains expected elements
        content = response.text
        assert "EntityDescriptor" in content
        assert test_sso_config.sp_entity_id in content
        assert test_sso_config.sp_acs_url in content
        assert "VendorAuditAI" in content

    @pytest.mark.asyncio
    async def test_get_sp_metadata_not_configured(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
    ):
        """Test SP metadata returns 404 when not configured."""
        response = await async_client.get(
            f"/api/v1/sso/metadata/{test_organization.id}"
        )

        assert response.status_code == 404
        assert "not configured" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_initiate_sso_login(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
        test_sso_config: SSOConfig,
    ):
        """Test SSO login initiation returns redirect URL."""
        response = await async_client.get(
            f"/api/v1/sso/login/{test_organization.id}",
            params={"relay_state": "https://app.example.com/dashboard"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "redirect_url" in data
        assert data["redirect_url"].startswith(test_sso_config.idp_sso_url)
        assert "SAMLRequest" in data["redirect_url"]
        assert "RelayState" in data["redirect_url"]
        assert "saml_request" in data

    @pytest.mark.asyncio
    async def test_initiate_sso_login_disabled(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
        disabled_sso_config: SSOConfig,
    ):
        """Test SSO login returns 400 when SSO is disabled."""
        response = await async_client.get(
            f"/api/v1/sso/login/{test_organization.id}"
        )

        assert response.status_code == 400
        assert "not enabled" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_initiate_sso_login_not_configured(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
    ):
        """Test SSO login returns 404 when not configured."""
        response = await async_client.get(
            f"/api/v1/sso/login/{test_organization.id}"
        )

        assert response.status_code == 404
        assert "not configured" in response.json()["detail"].lower()


class TestSSOAdminEndpoints:
    """Tests for SSO admin endpoints (authentication required)."""

    @pytest.mark.asyncio
    async def test_configure_sso_success(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
        test_organization: Organization,
    ):
        """Test SSO configuration creation."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        config_data = {
            "provider": "azure_ad",
            "enabled": True,
            "idp_entity_id": "https://login.microsoftonline.com/tenant-id",
            "idp_sso_url": "https://login.microsoftonline.com/tenant-id/saml2",
            "idp_slo_url": "https://login.microsoftonline.com/tenant-id/saml2/logout",
            "idp_x509_cert": SAMPLE_X509_CERT,
            "want_assertions_signed": True,
            "want_response_signed": True,
            "attribute_mapping": {
                "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
                "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
            },
        }

        response = await async_client.post(
            "/api/v1/sso/configure",
            headers=headers,
            json=config_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["provider"] == "azure_ad"
        assert data["enabled"] is True
        assert data["organization_id"] == test_organization.id
        assert data["idp_entity_id"] == config_data["idp_entity_id"]
        assert "sp_entity_id" in data
        assert "sp_acs_url" in data

    @pytest.mark.asyncio
    async def test_configure_sso_requires_admin(
        self,
        async_client: AsyncClient,
        test_user: User,
    ):
        """Test SSO configuration requires admin privileges."""
        token = get_auth_token(test_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/sso/configure",
            headers=headers,
            json={
                "provider": "okta",
                "idp_entity_id": "https://test.okta.com",
                "idp_sso_url": "https://test.okta.com/sso",
                "idp_x509_cert": SAMPLE_X509_CERT,
            },
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_configure_sso_duplicate_fails(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
        test_sso_config: SSOConfig,
    ):
        """Test SSO configuration fails if already exists."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/sso/configure",
            headers=headers,
            json={
                "provider": "okta",
                "idp_entity_id": "https://test.okta.com",
                "idp_sso_url": "https://test.okta.com/sso",
                "idp_x509_cert": SAMPLE_X509_CERT,
            },
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_sso_config(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
        test_sso_config: SSOConfig,
    ):
        """Test getting SSO configuration."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/api/v1/sso/config", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_sso_config.id
        assert data["provider"] == test_sso_config.provider
        assert data["enabled"] == test_sso_config.enabled

    @pytest.mark.asyncio
    async def test_get_sso_config_not_found(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
    ):
        """Test getting SSO config returns 404 when not configured."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/api/v1/sso/config", headers=headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_sso_config(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
        test_sso_config: SSOConfig,
    ):
        """Test updating SSO configuration."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {
            "enabled": False,
            "idp_sso_url": "https://new-idp.example.com/sso",
        }

        response = await async_client.put(
            "/api/v1/sso/config",
            headers=headers,
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False
        assert data["idp_sso_url"] == "https://new-idp.example.com/sso"
        # Other fields should remain unchanged
        assert data["provider"] == test_sso_config.provider

    @pytest.mark.asyncio
    async def test_delete_sso_config(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
        test_sso_config: SSOConfig,
    ):
        """Test deleting SSO configuration."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.delete("/api/v1/sso/config", headers=headers)

        assert response.status_code == 204

        # Verify deletion
        response = await async_client.get("/api/v1/sso/config", headers=headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_sso_config_not_found(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
    ):
        """Test deleting non-existent SSO config returns 404."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.delete("/api/v1/sso/config", headers=headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_sp_metadata_info(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
        test_sso_config: SSOConfig,
    ):
        """Test getting SP metadata info for admin."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/api/v1/sso/metadata", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "metadata_xml" in data
        assert "entity_id" in data
        assert "acs_url" in data
        assert data["entity_id"] == test_sso_config.sp_entity_id
        assert data["acs_url"] == test_sso_config.sp_acs_url


class TestSSOCallback:
    """Tests for SSO callback (ACS) endpoints."""

    @pytest.mark.asyncio
    async def test_acs_invalid_saml_response(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
        test_sso_config: SSOConfig,
    ):
        """Test ACS rejects invalid SAML response."""
        # Send an invalid base64-encoded SAML response
        invalid_response = base64.b64encode(b"<invalid>not valid xml").decode()

        response = await async_client.post(
            f"/api/v1/sso/acs/{test_organization.id}",
            data={"SAMLResponse": invalid_response},
        )

        assert response.status_code == 400
        assert "saml" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_acs_sso_not_configured(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
    ):
        """Test ACS returns error when SSO not configured."""
        dummy_response = base64.b64encode(b"<Response></Response>").decode()

        response = await async_client.post(
            f"/api/v1/sso/acs/{test_organization.id}",
            data={"SAMLResponse": dummy_response},
        )

        assert response.status_code == 400
        assert "not configured" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_acs_sso_not_enabled(
        self,
        async_client: AsyncClient,
        test_organization: Organization,
        disabled_sso_config: SSOConfig,
    ):
        """Test ACS returns error when SSO not enabled."""
        dummy_response = base64.b64encode(b"<Response></Response>").decode()

        response = await async_client.post(
            f"/api/v1/sso/acs/{test_organization.id}",
            data={"SAMLResponse": dummy_response},
        )

        assert response.status_code == 400
        assert "not enabled" in response.json()["detail"].lower()


class TestSSOCertificateValidation:
    """Tests for SSO certificate validation."""

    @pytest.mark.asyncio
    async def test_configure_sso_invalid_cert_format(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
    ):
        """Test SSO configuration rejects invalid certificate format."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/sso/configure",
            headers=headers,
            json={
                "provider": "okta",
                "idp_entity_id": "https://test.okta.com",
                "idp_sso_url": "https://test.okta.com/sso",
                "idp_x509_cert": "not-a-valid-certificate",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_configure_sso_accepts_base64_der_cert(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
    ):
        """Test SSO configuration accepts base64-encoded DER certificate."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        # A certificate that starts with MII (common for base64 DER)
        base64_der_cert = "MIICpDCCAYwCCQDU+pQ4L5qE5jANBgkqhkiG9w0BAQ=="

        response = await async_client.post(
            "/api/v1/sso/configure",
            headers=headers,
            json={
                "provider": "okta",
                "idp_entity_id": "https://test.okta.com",
                "idp_sso_url": "https://test.okta.com/sso",
                "idp_x509_cert": base64_der_cert,
            },
        )

        assert response.status_code == 201


class TestSSOProviders:
    """Tests for different SSO provider configurations."""

    @pytest.mark.asyncio
    async def test_configure_azure_ad(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
    ):
        """Test configuring Azure AD SSO."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/sso/configure",
            headers=headers,
            json={
                "provider": "azure_ad",
                "idp_entity_id": "https://sts.windows.net/tenant-id/",
                "idp_sso_url": "https://login.microsoftonline.com/tenant-id/saml2",
                "idp_x509_cert": SAMPLE_X509_CERT,
            },
        )

        assert response.status_code == 201
        assert response.json()["provider"] == "azure_ad"

    @pytest.mark.asyncio
    async def test_configure_google(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
    ):
        """Test configuring Google SSO."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/sso/configure",
            headers=headers,
            json={
                "provider": "google",
                "idp_entity_id": "https://accounts.google.com/o/saml2?idpid=xxx",
                "idp_sso_url": "https://accounts.google.com/o/saml2/idp?idpid=xxx",
                "idp_x509_cert": SAMPLE_X509_CERT,
            },
        )

        assert response.status_code == 201
        assert response.json()["provider"] == "google"

    @pytest.mark.asyncio
    async def test_configure_onelogin(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
    ):
        """Test configuring OneLogin SSO."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/sso/configure",
            headers=headers,
            json={
                "provider": "onelogin",
                "idp_entity_id": "https://app.onelogin.com/saml/metadata/xxx",
                "idp_sso_url": "https://xxx.onelogin.com/trust/saml2/http-post/sso/xxx",
                "idp_x509_cert": SAMPLE_X509_CERT,
            },
        )

        assert response.status_code == 201
        assert response.json()["provider"] == "onelogin"

    @pytest.mark.asyncio
    async def test_configure_custom_provider(
        self,
        async_client: AsyncClient,
        test_admin_user: User,
    ):
        """Test configuring custom SSO provider."""
        token = get_auth_token(test_admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/sso/configure",
            headers=headers,
            json={
                "provider": "custom",
                "idp_entity_id": "https://custom-idp.example.com/entity",
                "idp_sso_url": "https://custom-idp.example.com/sso",
                "idp_x509_cert": SAMPLE_X509_CERT,
                "attribute_mapping": {
                    "email": "custom:email",
                    "first_name": "custom:firstName",
                    "last_name": "custom:lastName",
                    "groups": "custom:memberOf",
                },
            },
        )

        assert response.status_code == 201
        assert response.json()["provider"] == "custom"
        assert response.json()["attribute_mapping"]["email"] == "custom:email"
