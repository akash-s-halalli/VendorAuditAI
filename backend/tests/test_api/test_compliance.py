"""Tests for compliance framework API endpoints."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class TestComplianceFrameworkEndpoints:
    """Tests for compliance framework listing and retrieval."""

    def test_list_frameworks_returns_200(self, client: TestClient):
        """Test that listing frameworks returns 200 status."""
        response = client.get("/api/v1/frameworks")

        assert response.status_code == 200

    def test_list_frameworks_response_structure(self, client: TestClient):
        """Test that list frameworks returns expected structure."""
        response = client.get("/api/v1/frameworks")
        data = response.json()

        assert "data" in data
        assert "total" in data
        assert isinstance(data["data"], list)
        assert isinstance(data["total"], int)

    def test_list_frameworks_total_matches_data_length(self, client: TestClient):
        """Test that total count matches data array length."""
        response = client.get("/api/v1/frameworks")
        data = response.json()

        assert data["total"] == len(data["data"])

    def test_get_nonexistent_framework_returns_404(self, client: TestClient):
        """Test that getting a non-existent framework returns 404."""
        response = client.get("/api/v1/frameworks/nonexistent_framework")

        assert response.status_code == 404

    def test_get_framework_summary_nonexistent_returns_404(self, client: TestClient):
        """Test that getting summary for non-existent framework returns 404."""
        response = client.get("/api/v1/frameworks/nonexistent_framework/summary")

        assert response.status_code == 404

    def test_get_framework_controls_nonexistent_returns_404(self, client: TestClient):
        """Test that getting controls for non-existent framework returns 404."""
        response = client.get("/api/v1/frameworks/nonexistent_framework/controls")

        assert response.status_code == 404

    def test_get_control_nonexistent_framework_returns_404(self, client: TestClient):
        """Test that getting a control from non-existent framework returns 404."""
        response = client.get("/api/v1/frameworks/nonexistent/controls/ctrl1")

        assert response.status_code == 404


class TestComplianceFrameworkSearch:
    """Tests for compliance framework search functionality."""

    def test_search_controls_returns_200(self, client: TestClient):
        """Test that search endpoint returns 200 for valid query."""
        response = client.get("/api/v1/frameworks/search", params={"query": "access"})

        assert response.status_code == 200

    def test_search_controls_requires_query(self, client: TestClient):
        """Test that search endpoint requires a query parameter."""
        response = client.get("/api/v1/frameworks/search")

        assert response.status_code == 422  # Validation error

    def test_search_controls_query_min_length(self, client: TestClient):
        """Test that search query requires minimum 2 characters."""
        response = client.get("/api/v1/frameworks/search", params={"query": "a"})

        assert response.status_code == 422  # Validation error

    def test_search_controls_response_structure(self, client: TestClient):
        """Test that search returns expected response structure."""
        response = client.get("/api/v1/frameworks/search", params={"query": "access"})
        data = response.json()

        assert "query" in data
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)

    def test_search_controls_with_limit(self, client: TestClient):
        """Test that search respects limit parameter."""
        response = client.get(
            "/api/v1/frameworks/search", params={"query": "access", "limit": 5}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 5

    def test_search_controls_with_framework_filter(self, client: TestClient):
        """Test that search accepts framework_ids filter."""
        response = client.get(
            "/api/v1/frameworks/search",
            params={"query": "access", "framework_ids": "soc2,iso27001"},
        )

        assert response.status_code == 200


class TestComplianceFrameworkWithTestData:
    """Tests using mock framework data."""

    @pytest.fixture
    def mock_framework_dir(self, sample_framework_data, tmp_path):
        """Create a temporary directory with mock framework data."""
        frameworks_dir = tmp_path / "frameworks"
        frameworks_dir.mkdir()

        # Write the sample framework data
        framework_file = frameworks_dir / "test_framework.json"
        framework_file.write_text(json.dumps(sample_framework_data))

        return frameworks_dir

    def test_list_frameworks_with_mock_data(
        self, client: TestClient, mock_framework_dir, sample_framework_data
    ):
        """Test listing frameworks with mock data."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            # Clear the cache to force reload
            from app.services.compliance import reload_frameworks
            reload_frameworks()

            response = client.get("/api/v1/frameworks")
            data = response.json()

            assert response.status_code == 200
            assert data["total"] >= 1

            # Find our test framework
            test_frameworks = [f for f in data["data"] if f["id"] == "test_framework"]
            assert len(test_frameworks) == 1

            framework = test_frameworks[0]
            assert framework["name"] == sample_framework_data["name"]
            assert framework["version"] == sample_framework_data["version"]

    def test_get_framework_by_id_with_mock_data(
        self, client: TestClient, mock_framework_dir, sample_framework_data
    ):
        """Test getting a specific framework by ID."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            from app.services.compliance import reload_frameworks
            reload_frameworks()

            response = client.get("/api/v1/frameworks/test_framework")
            data = response.json()

            assert response.status_code == 200
            assert data["id"] == "test_framework"
            assert data["name"] == sample_framework_data["name"]
            assert "categories" in data
            assert len(data["categories"]) == 1

    def test_get_framework_summary_with_mock_data(
        self, client: TestClient, mock_framework_dir, sample_framework_data
    ):
        """Test getting framework summary."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            from app.services.compliance import reload_frameworks
            reload_frameworks()

            response = client.get("/api/v1/frameworks/test_framework/summary")
            data = response.json()

            assert response.status_code == 200
            assert data["id"] == "test_framework"
            assert data["category_count"] == 1
            assert data["control_count"] == 1

    def test_get_framework_controls_with_mock_data(
        self, client: TestClient, mock_framework_dir
    ):
        """Test getting all controls for a framework."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            from app.services.compliance import reload_frameworks
            reload_frameworks()

            response = client.get("/api/v1/frameworks/test_framework/controls")
            data = response.json()

            assert response.status_code == 200
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["id"] == "CAT1.1"

    def test_get_control_by_id_with_mock_data(
        self, client: TestClient, mock_framework_dir
    ):
        """Test getting a specific control by ID."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            from app.services.compliance import reload_frameworks
            reload_frameworks()

            response = client.get("/api/v1/frameworks/test_framework/controls/CAT1.1")
            data = response.json()

            assert response.status_code == 200
            assert data["id"] == "CAT1.1"
            assert data["name"] == "Test Control 1.1"
            assert data["framework_id"] == "test_framework"
            assert data["category_id"] == "CAT1"

    def test_search_controls_with_mock_data(
        self, client: TestClient, mock_framework_dir
    ):
        """Test searching controls with mock data."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            from app.services.compliance import reload_frameworks
            reload_frameworks()

            response = client.get(
                "/api/v1/frameworks/search", params={"query": "test control"}
            )
            data = response.json()

            assert response.status_code == 200
            assert data["total"] >= 1
            # Verify our test control is in results
            control_ids = [r["control"]["id"] for r in data["results"]]
            assert "CAT1.1" in control_ids
