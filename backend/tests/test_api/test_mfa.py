"""Tests for MFA (Multi-Factor Authentication) endpoints."""

import pyotp
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from tests.conftest import get_auth_token


class TestMFAEnable:
    """Tests for the MFA enable endpoint."""

    @pytest.mark.asyncio
    async def test_mfa_enable_generates_valid_secret(
        self,
        async_client: AsyncClient,
        test_user: User,
    ):
        """Test that MFA enable generates a valid TOTP secret."""
        token = get_auth_token(test_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post("/api/v1/auth/mfa/enable", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "secret" in data
        assert "provisioning_uri" in data
        assert "backup_codes" in data

        # Verify secret is valid base32
        secret = data["secret"]
        assert len(secret) == 32  # Standard pyotp secret length

        # Verify provisioning URI format
        uri = data["provisioning_uri"]
        assert uri.startswith("otpauth://totp/")
        assert "VendorAuditAI" in uri
        # Email is URL-encoded in the URI (@ becomes %40)
        assert test_user.email.replace("@", "%40") in uri

        # Verify backup codes
        assert len(data["backup_codes"]) == 10
        for code in data["backup_codes"]:
            assert len(code) == 8

    @pytest.mark.asyncio
    async def test_mfa_enable_already_enabled_fails(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that enabling MFA fails if already enabled."""
        # Enable MFA for the user
        test_user.mfa_enabled = True
        test_user.mfa_secret = pyotp.random_base32()
        await db_session.commit()

        token = get_auth_token(test_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post("/api/v1/auth/mfa/enable", headers=headers)

        assert response.status_code == 400
        assert "already enabled" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_mfa_enable_requires_auth(self, async_client: AsyncClient):
        """Test that MFA enable requires authentication."""
        response = await async_client.post("/api/v1/auth/mfa/enable")
        assert response.status_code == 401


class TestMFAVerify:
    """Tests for the MFA verify endpoint."""

    @pytest.mark.asyncio
    async def test_mfa_verify_with_correct_code(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that MFA verify works with correct TOTP code."""
        token = get_auth_token(test_user)
        headers = {"Authorization": f"Bearer {token}"}

        # First, enable MFA to get the secret
        enable_response = await async_client.post(
            "/api/v1/auth/mfa/enable", headers=headers
        )
        assert enable_response.status_code == 200
        secret = enable_response.json()["secret"]

        # Generate a valid TOTP code
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        # Verify with the correct code
        response = await async_client.post(
            "/api/v1/auth/mfa/verify",
            headers=headers,
            json={"code": valid_code},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mfa_enabled"] is True
        assert "successfully enabled" in data["message"].lower()

        # Refresh the user from DB
        await db_session.refresh(test_user)
        assert test_user.mfa_enabled is True
        assert test_user.mfa_secret == secret

    @pytest.mark.asyncio
    async def test_mfa_verify_with_incorrect_code(
        self,
        async_client: AsyncClient,
        test_user: User,
    ):
        """Test that MFA verify fails with incorrect TOTP code."""
        token = get_auth_token(test_user)
        headers = {"Authorization": f"Bearer {token}"}

        # First, enable MFA to get the secret
        enable_response = await async_client.post(
            "/api/v1/auth/mfa/enable", headers=headers
        )
        assert enable_response.status_code == 200

        # Try to verify with an incorrect code
        response = await async_client.post(
            "/api/v1/auth/mfa/verify",
            headers=headers,
            json={"code": "000000"},
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_mfa_verify_without_enable_fails(
        self,
        async_client: AsyncClient,
        test_user: User,
    ):
        """Test that MFA verify fails if enable was not called first."""
        token = get_auth_token(test_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/auth/mfa/verify",
            headers=headers,
            json={"code": "123456"},
        )

        assert response.status_code == 400
        assert "not initiated" in response.json()["detail"].lower()


class TestMFADisable:
    """Tests for the MFA disable endpoint."""

    @pytest.mark.asyncio
    async def test_mfa_disable_works(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that MFA can be disabled with valid code."""
        # Enable MFA for the user
        secret = pyotp.random_base32()
        test_user.mfa_enabled = True
        test_user.mfa_secret = secret
        await db_session.commit()

        token = get_auth_token(test_user)
        headers = {"Authorization": f"Bearer {token}"}

        # Generate a valid TOTP code
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        response = await async_client.post(
            "/api/v1/auth/mfa/disable",
            headers=headers,
            json={"code": valid_code},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mfa_enabled"] is False
        assert "disabled" in data["message"].lower()

        # Refresh the user from DB
        await db_session.refresh(test_user)
        assert test_user.mfa_enabled is False
        assert test_user.mfa_secret is None

    @pytest.mark.asyncio
    async def test_mfa_disable_with_incorrect_code_fails(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that MFA disable fails with incorrect code."""
        # Enable MFA for the user
        secret = pyotp.random_base32()
        test_user.mfa_enabled = True
        test_user.mfa_secret = secret
        await db_session.commit()

        token = get_auth_token(test_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/auth/mfa/disable",
            headers=headers,
            json={"code": "000000"},
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_mfa_disable_when_not_enabled_fails(
        self,
        async_client: AsyncClient,
        test_user: User,
    ):
        """Test that MFA disable fails if MFA is not enabled."""
        token = get_auth_token(test_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/auth/mfa/disable",
            headers=headers,
            json={"code": "123456"},
        )

        assert response.status_code == 400
        assert "not enabled" in response.json()["detail"].lower()


class TestMFALoginFlow:
    """Tests for the MFA login flow."""

    @pytest.mark.asyncio
    async def test_login_with_mfa_enabled_returns_mfa_required(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that login with MFA enabled returns mfa_required flag."""
        # Enable MFA for the user
        secret = pyotp.random_base32()
        test_user.mfa_enabled = True
        test_user.mfa_secret = secret
        await db_session.commit()

        response = await async_client.post(
            "/api/v1/auth/login-mfa",
            data={
                "username": test_user.email,
                "password": "testpassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mfa_required"] is True
        assert data["mfa_token"] is not None
        assert data["access_token"] is None
        assert data["refresh_token"] is None

    @pytest.mark.asyncio
    async def test_login_without_mfa_returns_tokens(
        self,
        async_client: AsyncClient,
        test_user: User,
    ):
        """Test that login without MFA returns full tokens."""
        response = await async_client.post(
            "/api/v1/auth/login-mfa",
            data={
                "username": test_user.email,
                "password": "testpassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mfa_required"] is False
        assert data["access_token"] is not None
        assert data["refresh_token"] is not None

    @pytest.mark.asyncio
    async def test_mfa_validate_with_correct_code(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that MFA validation works with correct code."""
        # Enable MFA for the user
        secret = pyotp.random_base32()
        test_user.mfa_enabled = True
        test_user.mfa_secret = secret
        await db_session.commit()

        # Login to get MFA token
        login_response = await async_client.post(
            "/api/v1/auth/login-mfa",
            data={
                "username": test_user.email,
                "password": "testpassword123",
            },
        )
        mfa_token = login_response.json()["mfa_token"]

        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        # Validate MFA
        response = await async_client.post(
            "/api/v1/auth/mfa/validate",
            headers={"X-MFA-Token": mfa_token},
            json={"code": valid_code},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] is not None
        assert data["refresh_token"] is not None
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_mfa_validate_with_incorrect_code_fails(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that MFA validation fails with incorrect code."""
        # Enable MFA for the user
        secret = pyotp.random_base32()
        test_user.mfa_enabled = True
        test_user.mfa_secret = secret
        await db_session.commit()

        # Login to get MFA token
        login_response = await async_client.post(
            "/api/v1/auth/login-mfa",
            data={
                "username": test_user.email,
                "password": "testpassword123",
            },
        )
        mfa_token = login_response.json()["mfa_token"]

        # Try to validate with incorrect code
        response = await async_client.post(
            "/api/v1/auth/mfa/validate",
            headers={"X-MFA-Token": mfa_token},
            json={"code": "000000"},
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_mfa_validate_with_invalid_token_fails(
        self,
        async_client: AsyncClient,
    ):
        """Test that MFA validation fails with invalid MFA token."""
        response = await async_client.post(
            "/api/v1/auth/mfa/validate",
            headers={"X-MFA-Token": "invalid-token"},
            json={"code": "123456"},
        )

        assert response.status_code == 401


class TestMFACodeValidation:
    """Tests for TOTP code format validation."""

    @pytest.mark.asyncio
    async def test_mfa_code_must_be_6_digits(
        self,
        async_client: AsyncClient,
        test_user: User,
    ):
        """Test that MFA code must be exactly 6 digits."""
        token = get_auth_token(test_user)
        headers = {"Authorization": f"Bearer {token}"}

        # First enable MFA
        await async_client.post("/api/v1/auth/mfa/enable", headers=headers)

        # Test with 5 digits
        response = await async_client.post(
            "/api/v1/auth/mfa/verify",
            headers=headers,
            json={"code": "12345"},
        )
        assert response.status_code == 422  # Validation error

        # Test with 7 digits
        response = await async_client.post(
            "/api/v1/auth/mfa/verify",
            headers=headers,
            json={"code": "1234567"},
        )
        assert response.status_code == 422

        # Test with non-numeric
        response = await async_client.post(
            "/api/v1/auth/mfa/verify",
            headers=headers,
            json={"code": "abcdef"},
        )
        assert response.status_code == 422
