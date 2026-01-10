"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests for health and root endpoints."""

    def test_health_check_returns_200(self, client: TestClient):
        """Test that the /health endpoint returns a 200 status code."""
        response = client.get("/health")

        assert response.status_code == 200

    def test_health_check_response_structure(self, client: TestClient):
        """Test that the /health endpoint returns the expected structure."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "environment" in data

    def test_health_check_status_is_healthy(self, client: TestClient):
        """Test that the /health endpoint reports healthy status."""
        response = client.get("/health")
        data = response.json()

        assert data["status"] == "healthy"

    def test_health_check_environment_is_present(self, client: TestClient):
        """Test that the /health endpoint shows environment."""
        response = client.get("/health")
        data = response.json()

        # Environment should be present (may vary based on config loading order)
        assert data["environment"] in ["testing", "development"]

    def test_root_endpoint_returns_200(self, client: TestClient):
        """Test that the root endpoint returns a 200 status code."""
        response = client.get("/")

        assert response.status_code == 200

    def test_root_endpoint_response_structure(self, client: TestClient):
        """Test that the root endpoint returns expected fields."""
        response = client.get("/")
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "health" in data

    def test_root_endpoint_shows_app_name(self, client: TestClient):
        """Test that the root endpoint shows the correct app name."""
        response = client.get("/")
        data = response.json()

        assert data["name"] == "VendorAuditAI"

    def test_api_v1_status_endpoint(self, client: TestClient):
        """Test the API v1 status endpoint."""
        response = client.get("/api/v1/status")

        assert response.status_code == 200
        data = response.json()
        assert data["api_version"] == "v1"
        assert data["status"] == "operational"
        assert "endpoints" in data
