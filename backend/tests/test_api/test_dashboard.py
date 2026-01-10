"""Tests for dashboard API endpoints."""

import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AnalysisRun,
    Document,
    DocumentStatus,
    Finding,
    FindingSeverity,
    Organization,
    User,
    Vendor,
)


class TestDashboardEndpoints:
    """Tests for dashboard statistics endpoints."""

    def test_dashboard_stats_requires_authentication(self, client: TestClient):
        """Test that /api/v1/dashboard/stats requires authentication."""
        response = client.get("/api/v1/dashboard/stats")

        assert response.status_code == 401

    def test_dashboard_stats_returns_200_with_auth(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test that /api/v1/dashboard/stats returns 200 with valid auth."""
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)

        assert response.status_code == 200

    def test_dashboard_stats_response_structure(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test that dashboard stats returns the expected response structure."""
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
        data = response.json()

        # Check all expected fields are present
        expected_fields = [
            "totalVendors",
            "totalDocuments",
            "pendingAnalysis",
            "completedAnalysis",
            "criticalFindings",
            "highFindings",
            "mediumFindings",
            "lowFindings",
        ]

        for field in expected_fields:
            assert field in data, f"Expected field '{field}' not found in response"

    def test_dashboard_stats_returns_zero_counts_for_new_org(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test that dashboard stats returns zero counts for a new organization."""
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
        data = response.json()

        # New organization should have zero counts
        assert data["totalVendors"] == 0
        assert data["totalDocuments"] == 0
        assert data["pendingAnalysis"] == 0
        assert data["completedAnalysis"] == 0
        assert data["criticalFindings"] == 0
        assert data["highFindings"] == 0
        assert data["mediumFindings"] == 0
        assert data["lowFindings"] == 0

    def test_dashboard_stats_counts_are_integers(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test that all dashboard stat counts are integers."""
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
        data = response.json()

        for key, value in data.items():
            assert isinstance(value, int), f"Expected '{key}' to be an integer"

    def test_dashboard_stats_with_invalid_token(self, client: TestClient):
        """Test that dashboard stats rejects invalid tokens."""
        response = client.get(
            "/api/v1/dashboard/stats",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401


@pytest_asyncio.fixture
async def org_with_data(
    db_session: AsyncSession, test_organization: Organization, test_user: User
) -> Organization:
    """Create an organization with vendors, documents, and findings for testing."""
    org_id = test_organization.id

    # Create some vendors
    vendor_ids = []
    for i in range(3):
        vendor_id = str(uuid.uuid4())
        vendor = Vendor(
            id=vendor_id,
            organization_id=org_id,
            name=f"Test Vendor {i}",
            description=f"Test vendor {i} description",
            status="active",
            tier="medium",
        )
        db_session.add(vendor)
        vendor_ids.append(vendor_id)

    await db_session.flush()

    first_vendor_id = vendor_ids[0]

    # Create documents with different statuses
    doc_statuses = [
        DocumentStatus.PENDING.value,
        DocumentStatus.PROCESSING.value,
        DocumentStatus.PROCESSED.value,
        DocumentStatus.PROCESSED.value,
    ]
    doc_ids = []
    for i, status in enumerate(doc_statuses):
        doc_id = str(uuid.uuid4())
        doc = Document(
            id=doc_id,
            organization_id=org_id,
            vendor_id=first_vendor_id,
            filename=f"test_document_{i}.pdf",
            storage_path=f"/test/path/{i}.pdf",
            file_size=1024 * (i + 1),
            mime_type="application/pdf",
            document_type="soc2",
            status=status,
        )
        db_session.add(doc)
        doc_ids.append(doc_id)

    await db_session.flush()

    # Create an analysis run (required for findings)
    analysis_run_id = str(uuid.uuid4())
    analysis_run = AnalysisRun(
        id=analysis_run_id,
        organization_id=org_id,
        document_id=doc_ids[0],
        framework="soc2",
        model_used="test-model",
        status="completed",
    )
    db_session.add(analysis_run)
    await db_session.flush()

    # Create findings with different severities
    finding_severities = [
        FindingSeverity.CRITICAL.value,
        FindingSeverity.HIGH.value,
        FindingSeverity.HIGH.value,
        FindingSeverity.MEDIUM.value,
        FindingSeverity.LOW.value,
    ]
    for i, severity in enumerate(finding_severities):
        finding = Finding(
            id=str(uuid.uuid4()),
            organization_id=org_id,
            document_id=doc_ids[0],
            analysis_run_id=analysis_run_id,
            title=f"Test Finding {i}",
            description=f"Test finding {i} description",
            framework="soc2",
            severity=severity,
            status="open",
        )
        db_session.add(finding)

    await db_session.commit()
    return test_organization


class TestDashboardStatsWithData:
    """Tests for dashboard statistics with actual data."""

    @pytest.mark.asyncio
    async def test_dashboard_counts_vendors(
        self,
        async_client: AsyncClient,
        org_with_data: Organization,
        auth_headers: dict[str, str],
    ):
        """Test that dashboard correctly counts vendors."""
        response = await async_client.get(
            "/api/v1/dashboard/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["totalVendors"] == 3

    @pytest.mark.asyncio
    async def test_dashboard_counts_documents(
        self,
        async_client: AsyncClient,
        org_with_data: Organization,
        auth_headers: dict[str, str],
    ):
        """Test that dashboard correctly counts documents."""
        response = await async_client.get(
            "/api/v1/dashboard/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["totalDocuments"] == 4

    @pytest.mark.asyncio
    async def test_dashboard_counts_pending_analysis(
        self,
        async_client: AsyncClient,
        org_with_data: Organization,
        auth_headers: dict[str, str],
    ):
        """Test that dashboard correctly counts pending analysis."""
        response = await async_client.get(
            "/api/v1/dashboard/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # 1 pending + 1 processing = 2 pending analysis
        assert data["pendingAnalysis"] == 2

    @pytest.mark.asyncio
    async def test_dashboard_counts_completed_analysis(
        self,
        async_client: AsyncClient,
        org_with_data: Organization,
        auth_headers: dict[str, str],
    ):
        """Test that dashboard correctly counts completed analysis."""
        response = await async_client.get(
            "/api/v1/dashboard/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completedAnalysis"] == 2

    @pytest.mark.asyncio
    async def test_dashboard_counts_findings_by_severity(
        self,
        async_client: AsyncClient,
        org_with_data: Organization,
        auth_headers: dict[str, str],
    ):
        """Test that dashboard correctly counts findings by severity."""
        response = await async_client.get(
            "/api/v1/dashboard/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["criticalFindings"] == 1
        assert data["highFindings"] == 2
        assert data["mediumFindings"] == 1
        assert data["lowFindings"] == 1
