"""Pytest fixtures for VendorAuditAI tests."""

import asyncio
import sys
import uuid
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

# Mock tiktoken before any app imports to avoid network calls
mock_encoding = MagicMock()
mock_encoding.encode.return_value = [1, 2, 3]  # Return dummy token ids
mock_encoding.decode.return_value = "decoded text"

mock_tiktoken = MagicMock()
mock_tiktoken.get_encoding.return_value = mock_encoding
mock_tiktoken.encoding_for_model.return_value = mock_encoding

sys.modules["tiktoken"] = mock_tiktoken

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.db import get_db
from app.main import create_app
from app.models import Base, Organization, User, UserRole


# Test settings that override production settings
def get_test_settings() -> Settings:
    """Create test settings with in-memory SQLite database."""
    return Settings(
        app_env="testing",
        debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        database_echo=False,
        secret_key="test-secret-key",
        jwt_secret_key="test-jwt-secret-key",
        cors_origins=["http://localhost:3000"],
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create an async engine for testing with in-memory SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async_session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_organization(db_session: AsyncSession) -> Organization:
    """Create a test organization."""
    org = Organization(
        id=str(uuid.uuid4()),
        name="Test Organization",
        slug="test-org",
        description="A test organization for unit tests",
        subscription_tier="free",
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create a test user."""
    from app.core.security import hash_password

    user = User(
        id=str(uuid.uuid4()),
        organization_id=test_organization.id,
        email="testuser@example.com",
        password_hash=hash_password("testpassword123"),
        full_name="Test User",
        role=UserRole.ANALYST.value,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_admin_user(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create a test admin user."""
    from app.core.security import hash_password

    user = User(
        id=str(uuid.uuid4()),
        organization_id=test_organization.id,
        email="admin@example.com",
        password_hash=hash_password("adminpassword123"),
        full_name="Admin User",
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def get_auth_token(user: User) -> str:
    """Generate a JWT token for a test user."""
    from app.core.security import create_access_token
    return create_access_token(subject=user.id)


@pytest.fixture(scope="function")
def app(async_engine, db_session):
    """Create a FastAPI app instance for testing."""
    # Override settings
    with patch("app.config.get_settings", get_test_settings):
        test_app = create_app()

        # Override the database dependency
        async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
            yield db_session

        test_app.dependency_overrides[get_db] = override_get_db

        yield test_app

        test_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(app) -> Generator[TestClient, None, None]:
    """Create a synchronous test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture(scope="function")
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create an asynchronous test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest.fixture(scope="function")
def auth_headers(test_user: User) -> dict[str, str]:
    """Get authorization headers for authenticated requests."""
    token = get_auth_token(test_user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_auth_headers(test_admin_user: User) -> dict[str, str]:
    """Get authorization headers for admin requests."""
    token = get_auth_token(test_admin_user)
    return {"Authorization": f"Bearer {token}"}


# Sample test data fixtures
@pytest.fixture
def sample_vendor_data() -> dict[str, Any]:
    """Sample vendor data for testing."""
    return {
        "name": "Test Vendor Inc.",
        "description": "A test vendor for unit tests",
        "website": "https://testvendor.example.com",
        "contact_email": "contact@testvendor.example.com",
        "tier": "tier_1",
    }


@pytest.fixture
def sample_document_data() -> dict[str, Any]:
    """Sample document data for testing."""
    return {
        "title": "Test SOC 2 Report",
        "description": "A test SOC 2 report document",
        "document_type": "soc2",
    }


@pytest.fixture
def sample_framework_data() -> dict[str, Any]:
    """Sample compliance framework data for testing."""
    return {
        "id": "test_framework",
        "name": "Test Compliance Framework",
        "version": "1.0",
        "description": "A test compliance framework",
        "organization": "Test Standards Organization",
        "categories": [
            {
                "id": "CAT1",
                "name": "Test Category 1",
                "description": "First test category",
                "controls": [
                    {
                        "id": "CAT1.1",
                        "name": "Test Control 1.1",
                        "description": "First test control",
                        "requirements": [
                            {
                                "id": "CAT1.1.a",
                                "description": "First requirement",
                                "guidance": "Implementation guidance for first requirement",
                            }
                        ],
                    }
                ],
            }
        ],
    }
