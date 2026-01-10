"""Tests for compliance framework service functions."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.schemas.compliance import (
    ControlSearchQuery,
    ControlSearchResponse,
    FrameworkListResponse,
    FrameworkResponse,
    FrameworkSummary,
)
from app.services import compliance as compliance_service


class TestComplianceServiceFrameworkDiscovery:
    """Tests for framework discovery functionality."""

    @pytest.fixture
    def mock_frameworks_dir(self, tmp_path):
        """Create a temporary frameworks directory."""
        frameworks_dir = tmp_path / "frameworks"
        frameworks_dir.mkdir()
        return frameworks_dir

    def test_discover_frameworks_empty_directory(self, mock_frameworks_dir):
        """Test framework discovery with empty directory."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_frameworks_dir
        ):
            compliance_service.reload_frameworks()
            framework_ids = compliance_service.get_available_framework_ids()
            assert framework_ids == []

    def test_discover_frameworks_with_files(self, mock_frameworks_dir, sample_framework_data):
        """Test framework discovery with framework files."""
        # Create framework files
        (mock_frameworks_dir / "soc2.json").write_text(json.dumps(sample_framework_data))
        (mock_frameworks_dir / "iso27001.json").write_text(json.dumps(sample_framework_data))

        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_frameworks_dir
        ):
            compliance_service.reload_frameworks()
            framework_ids = compliance_service.get_available_framework_ids()

            assert len(framework_ids) == 2
            assert "soc2" in framework_ids
            assert "iso27001" in framework_ids

    def test_discover_frameworks_sorted(self, mock_frameworks_dir, sample_framework_data):
        """Test that discovered frameworks are sorted alphabetically."""
        # Create framework files
        (mock_frameworks_dir / "zebra.json").write_text(json.dumps(sample_framework_data))
        (mock_frameworks_dir / "alpha.json").write_text(json.dumps(sample_framework_data))
        (mock_frameworks_dir / "beta.json").write_text(json.dumps(sample_framework_data))

        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_frameworks_dir
        ):
            compliance_service.reload_frameworks()
            framework_ids = compliance_service.get_available_framework_ids()

            assert framework_ids == ["alpha", "beta", "zebra"]


class TestComplianceServiceGetAllFrameworks:
    """Tests for get_all_frameworks function."""

    @pytest.fixture
    def mock_frameworks_dir_with_data(self, tmp_path, sample_framework_data):
        """Create frameworks directory with test data."""
        frameworks_dir = tmp_path / "frameworks"
        frameworks_dir.mkdir()

        # Create two frameworks with different data
        framework1 = sample_framework_data.copy()
        framework1["id"] = "framework1"
        framework1["name"] = "Framework One"

        framework2 = sample_framework_data.copy()
        framework2["id"] = "framework2"
        framework2["name"] = "Framework Two"
        framework2["categories"].append({
            "id": "CAT2",
            "name": "Category Two",
            "description": "Second category",
            "controls": [
                {
                    "id": "CAT2.1",
                    "name": "Control 2.1",
                    "description": "Control in category 2",
                    "requirements": [],
                }
            ],
        })

        (frameworks_dir / "framework1.json").write_text(json.dumps(framework1))
        (frameworks_dir / "framework2.json").write_text(json.dumps(framework2))

        return frameworks_dir

    def test_get_all_frameworks_returns_list_response(
        self, mock_frameworks_dir_with_data
    ):
        """Test that get_all_frameworks returns FrameworkListResponse."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_frameworks_dir_with_data
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_all_frameworks()

            assert isinstance(result, FrameworkListResponse)

    def test_get_all_frameworks_total_count(self, mock_frameworks_dir_with_data):
        """Test that total count matches number of frameworks."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_frameworks_dir_with_data
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_all_frameworks()

            assert result.total == 2
            assert len(result.data) == 2

    def test_get_all_frameworks_summary_fields(self, mock_frameworks_dir_with_data):
        """Test that framework summaries have correct fields."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_frameworks_dir_with_data
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_all_frameworks()

            for summary in result.data:
                assert isinstance(summary, FrameworkSummary)
                assert summary.id is not None
                assert summary.name is not None
                assert summary.version is not None
                assert isinstance(summary.category_count, int)
                assert isinstance(summary.control_count, int)

    def test_get_all_frameworks_counts_categories_and_controls(
        self, mock_frameworks_dir_with_data
    ):
        """Test that category and control counts are correct."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_frameworks_dir_with_data
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_all_frameworks()

            # Find framework2 which has 2 categories and 2 controls
            framework2 = next(f for f in result.data if f.id == "framework2")
            assert framework2.category_count == 2
            assert framework2.control_count == 2


class TestComplianceServiceGetFramework:
    """Tests for get_framework_by_id function."""

    @pytest.fixture
    def mock_framework_dir(self, tmp_path, sample_framework_data):
        """Create framework directory with test data."""
        frameworks_dir = tmp_path / "frameworks"
        frameworks_dir.mkdir()
        (frameworks_dir / "test_framework.json").write_text(
            json.dumps(sample_framework_data)
        )
        return frameworks_dir

    def test_get_framework_by_id_returns_framework(
        self, mock_framework_dir, sample_framework_data
    ):
        """Test getting a framework by ID."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_framework_by_id("test_framework")

            assert result is not None
            assert isinstance(result, FrameworkResponse)
            assert result.id == "test_framework"
            assert result.name == sample_framework_data["name"]

    def test_get_framework_by_id_includes_categories(
        self, mock_framework_dir, sample_framework_data
    ):
        """Test that framework includes categories with controls."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_framework_by_id("test_framework")

            assert len(result.categories) == 1
            category = result.categories[0]
            assert category.id == "CAT1"
            assert len(category.controls) == 1

    def test_get_framework_by_id_nonexistent_returns_none(self, mock_framework_dir):
        """Test getting a non-existent framework returns None."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_framework_by_id("nonexistent")

            assert result is None


class TestComplianceServiceGetFrameworkSummary:
    """Tests for get_framework_summary function."""

    @pytest.fixture
    def mock_framework_dir(self, tmp_path, sample_framework_data):
        """Create framework directory with test data."""
        frameworks_dir = tmp_path / "frameworks"
        frameworks_dir.mkdir()
        (frameworks_dir / "test_framework.json").write_text(
            json.dumps(sample_framework_data)
        )
        return frameworks_dir

    def test_get_framework_summary_returns_summary(
        self, mock_framework_dir, sample_framework_data
    ):
        """Test getting framework summary."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_framework_summary("test_framework")

            assert result is not None
            assert isinstance(result, FrameworkSummary)
            assert result.id == "test_framework"
            assert result.category_count == 1
            assert result.control_count == 1

    def test_get_framework_summary_nonexistent_returns_none(self, mock_framework_dir):
        """Test getting summary for non-existent framework."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_framework_summary("nonexistent")

            assert result is None


class TestComplianceServiceGetControls:
    """Tests for get_framework_controls and get_control_by_id functions."""

    @pytest.fixture
    def mock_framework_dir(self, tmp_path, sample_framework_data):
        """Create framework directory with test data."""
        frameworks_dir = tmp_path / "frameworks"
        frameworks_dir.mkdir()
        (frameworks_dir / "test_framework.json").write_text(
            json.dumps(sample_framework_data)
        )
        return frameworks_dir

    def test_get_framework_controls_returns_list(self, mock_framework_dir):
        """Test getting all controls for a framework."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_framework_controls("test_framework")

            assert result is not None
            assert isinstance(result, list)
            assert len(result) == 1

    def test_get_framework_controls_includes_metadata(self, mock_framework_dir):
        """Test that controls include framework and category IDs."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_framework_controls("test_framework")

            control = result[0]
            assert control.framework_id == "test_framework"
            assert control.category_id == "CAT1"

    def test_get_framework_controls_nonexistent_returns_none(self, mock_framework_dir):
        """Test getting controls for non-existent framework."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_framework_controls("nonexistent")

            assert result is None

    def test_get_control_by_id_returns_control(self, mock_framework_dir):
        """Test getting a specific control by ID."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_control_by_id("test_framework", "CAT1.1")

            assert result is not None
            assert result.id == "CAT1.1"
            assert result.name == "Test Control 1.1"

    def test_get_control_by_id_includes_requirements(self, mock_framework_dir):
        """Test that control includes requirements."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_control_by_id("test_framework", "CAT1.1")

            assert len(result.requirements) == 1
            assert result.requirements[0].id == "CAT1.1.a"

    def test_get_control_by_id_nonexistent_control(self, mock_framework_dir):
        """Test getting a non-existent control."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()
            result = compliance_service.get_control_by_id("test_framework", "NONEXISTENT")

            assert result is None


class TestComplianceServiceSearch:
    """Tests for search_controls function."""

    @pytest.fixture
    def mock_framework_dir_with_search_data(self, tmp_path):
        """Create framework directory with data suitable for search testing."""
        frameworks_dir = tmp_path / "frameworks"
        frameworks_dir.mkdir()

        framework = {
            "id": "search_test",
            "name": "Search Test Framework",
            "version": "1.0",
            "description": "Framework for testing search",
            "organization": "Test Org",
            "categories": [
                {
                    "id": "ACCESS",
                    "name": "Access Control",
                    "description": "Access management controls",
                    "controls": [
                        {
                            "id": "AC-1",
                            "name": "Access Policy",
                            "description": "Establish access control policies",
                            "requirements": [
                                {
                                    "id": "AC-1.a",
                                    "description": "Define access requirements",
                                    "guidance": "Document all access policies",
                                }
                            ],
                        },
                        {
                            "id": "AC-2",
                            "name": "Account Management",
                            "description": "Manage user accounts",
                            "requirements": [],
                        },
                    ],
                },
                {
                    "id": "ENCRYPT",
                    "name": "Encryption",
                    "description": "Encryption controls",
                    "controls": [
                        {
                            "id": "EN-1",
                            "name": "Data Encryption",
                            "description": "Encrypt sensitive data",
                            "requirements": [],
                        },
                    ],
                },
            ],
        }

        (frameworks_dir / "search_test.json").write_text(json.dumps(framework))
        return frameworks_dir

    def test_search_controls_returns_response(self, mock_framework_dir_with_search_data):
        """Test that search returns ControlSearchResponse."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR",
            mock_framework_dir_with_search_data,
        ):
            compliance_service.reload_frameworks()
            query = ControlSearchQuery(query="access")
            result = compliance_service.search_controls(query)

            assert isinstance(result, ControlSearchResponse)
            assert result.query == "access"

    def test_search_controls_finds_matching_controls(
        self, mock_framework_dir_with_search_data
    ):
        """Test that search finds controls matching the query."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR",
            mock_framework_dir_with_search_data,
        ):
            compliance_service.reload_frameworks()
            query = ControlSearchQuery(query="access")
            result = compliance_service.search_controls(query)

            # Should find AC-1 and AC-2 (both in Access Control category)
            assert result.total >= 1
            control_ids = [r.control.id for r in result.results]
            assert "AC-1" in control_ids

    def test_search_controls_respects_limit(self, mock_framework_dir_with_search_data):
        """Test that search respects the limit parameter."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR",
            mock_framework_dir_with_search_data,
        ):
            compliance_service.reload_frameworks()
            # Use 'ac' (2+ chars) which matches AC-1 and AC-2 in test data
            query = ControlSearchQuery(query="ac", limit=1)
            result = compliance_service.search_controls(query)

            assert len(result.results) <= 1

    def test_search_controls_filters_by_framework(
        self, mock_framework_dir_with_search_data
    ):
        """Test that search can filter by framework IDs."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR",
            mock_framework_dir_with_search_data,
        ):
            compliance_service.reload_frameworks()
            query = ControlSearchQuery(
                query="access", framework_ids=["search_test"]
            )
            result = compliance_service.search_controls(query)

            # All results should be from the specified framework
            for r in result.results:
                assert r.framework_id == "search_test"

    def test_search_controls_includes_relevance_score(
        self, mock_framework_dir_with_search_data
    ):
        """Test that search results include relevance scores."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR",
            mock_framework_dir_with_search_data,
        ):
            compliance_service.reload_frameworks()
            query = ControlSearchQuery(query="access")
            result = compliance_service.search_controls(query)

            for r in result.results:
                assert 0.0 <= r.relevance_score <= 1.0

    def test_search_controls_sorted_by_relevance(
        self, mock_framework_dir_with_search_data
    ):
        """Test that search results are sorted by relevance score."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR",
            mock_framework_dir_with_search_data,
        ):
            compliance_service.reload_frameworks()
            query = ControlSearchQuery(query="access")
            result = compliance_service.search_controls(query)

            scores = [r.relevance_score for r in result.results]
            assert scores == sorted(scores, reverse=True)

    def test_search_controls_no_results(self, mock_framework_dir_with_search_data):
        """Test search with no matching results."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR",
            mock_framework_dir_with_search_data,
        ):
            compliance_service.reload_frameworks()
            query = ControlSearchQuery(query="xyznonexistent")
            result = compliance_service.search_controls(query)

            assert result.total == 0
            assert len(result.results) == 0


class TestComplianceServiceRelevanceScore:
    """Tests for _calculate_relevance_score function."""

    def test_relevance_score_exact_id_match(self):
        """Test relevance score for exact ID match."""
        ctrl_data = {
            "id": "AC-1",
            "name": "Some Name",
            "description": "Some description",
            "requirements": [],
        }
        score = compliance_service._calculate_relevance_score(ctrl_data, "ac-1")
        assert score > 0

    def test_relevance_score_name_match(self):
        """Test relevance score for name match."""
        ctrl_data = {
            "id": "CTRL-1",
            "name": "Access Control Policy",
            "description": "Some description",
            "requirements": [],
        }
        score = compliance_service._calculate_relevance_score(ctrl_data, "access")
        assert score > 0

    def test_relevance_score_description_match(self):
        """Test relevance score for description match."""
        ctrl_data = {
            "id": "CTRL-1",
            "name": "Some Name",
            "description": "Control for encryption of data",
            "requirements": [],
        }
        score = compliance_service._calculate_relevance_score(ctrl_data, "encryption")
        assert score > 0

    def test_relevance_score_no_match(self):
        """Test relevance score when no match found."""
        ctrl_data = {
            "id": "CTRL-1",
            "name": "Access Control",
            "description": "Access management",
            "requirements": [],
        }
        score = compliance_service._calculate_relevance_score(ctrl_data, "xyznonexistent")
        assert score == 0.0

    def test_relevance_score_max_value(self):
        """Test that relevance score does not exceed 1.0."""
        ctrl_data = {
            "id": "access",
            "name": "access",
            "description": "access access access",
            "requirements": [
                {"description": "access", "guidance": "access"},
            ],
        }
        score = compliance_service._calculate_relevance_score(ctrl_data, "access")
        assert score <= 1.0


class TestComplianceServiceCaching:
    """Tests for framework caching functionality."""

    @pytest.fixture
    def mock_framework_dir(self, tmp_path, sample_framework_data):
        """Create framework directory with test data."""
        frameworks_dir = tmp_path / "frameworks"
        frameworks_dir.mkdir()
        (frameworks_dir / "cached_framework.json").write_text(
            json.dumps(sample_framework_data)
        )
        return frameworks_dir

    def test_reload_frameworks_clears_cache(self, mock_framework_dir):
        """Test that reload_frameworks clears the cache."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            # Load framework
            compliance_service.reload_frameworks()
            result1 = compliance_service.get_framework_by_id("cached_framework")
            assert result1 is not None

            # Clear cache
            compliance_service.reload_frameworks()

            # Should still work after reload
            result2 = compliance_service.get_framework_by_id("cached_framework")
            assert result2 is not None

    def test_framework_loaded_once_and_cached(self, mock_framework_dir):
        """Test that framework is loaded from file only once."""
        with patch(
            "app.services.compliance.FRAMEWORKS_DIR", mock_framework_dir
        ):
            compliance_service.reload_frameworks()

            # First call loads from file
            result1 = compliance_service.get_framework_by_id("cached_framework")

            # Second call should use cache
            result2 = compliance_service.get_framework_by_id("cached_framework")

            assert result1 is not None
            assert result2 is not None
            assert result1.id == result2.id
