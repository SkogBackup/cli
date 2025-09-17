"""Tests for skogcli memory functionality."""

import json
import subprocess
import pytest
import typer
from unittest.mock import patch, MagicMock
from skogcli.memory import get_memory_folders, get_memory_projects, run_basic_memory


def test_memory_help():
    """Test that running memory without args shows help."""
    # Run the command
    no_args_result = subprocess.run(
        ["uv", "run", "skogcli", "memory"],
        capture_output=True,
        text=True,
    )

    help_result = subprocess.run(
        ["uv", "run", "skogcli", "memory", "--help"],
        capture_output=True,
        text=True,
    )

    # Both commands should exit with the same status code
    assert no_args_result.returncode == help_result.returncode

    # Both commands should produce the same stdout
    assert no_args_result.stdout == help_result.stdout


class TestMemoryFunctions:
    """Test memory module functions with mocked subprocess calls."""

    @patch("skogcli.memory.run_basic_memory")
    def test_get_memory_folders_success(self, mock_run):
        """Test get_memory_folders when basic-memory returns data."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {"folders": [{"name": "test1"}, {"name": "test2"}, {"name": "test3"}]}
        )
        mock_run.return_value = mock_result

        # Call the function
        folders = get_memory_folders()

        # Check the result
        assert folders == ["test1", "test2", "test3"]
        mock_run.assert_called_once_with(["tool", "list-folders", "--format", "json"])

    @patch("skogcli.memory.run_basic_memory")
    def test_get_memory_folders_fallback(self, mock_run):
        """Test get_memory_folders fallback when basic-memory fails."""
        # Setup mock to raise exception
        mock_run.side_effect = Exception("Test error")

        # Call the function
        folders = get_memory_folders()

        # Check the fallback result
        assert "notes" in folders
        assert "meetings" in folders
        assert "projects" in folders

    @patch("skogcli.memory.run_basic_memory")
    def test_get_memory_projects_success(self, mock_run):
        """Test get_memory_projects when basic-memory returns data."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {"projects": [{"name": "project1"}, {"name": "project2"}]}
        )
        mock_run.return_value = mock_result

        # Call the function
        projects = get_memory_projects()

        # Check the result
        assert projects == ["project1", "project2"]
        mock_run.assert_called_once_with(["tool", "list-projects", "--format", "json"])

    @patch("skogcli.memory.run_basic_memory")
    @patch("skogcli.memory.get_setting")
    def test_get_memory_projects_fallback(self, mock_get_setting, mock_run):
        """Test get_memory_projects fallback when basic-memory fails."""
        # Setup mocks
        mock_run.side_effect = Exception("Test error")
        mock_get_setting.return_value = "test_project"

        # Call the function
        projects = get_memory_projects()

        # Check the fallback result
        assert "default" in projects
        assert "test_project" in projects
        mock_get_setting.assert_called_once_with("memory.default_project")

    @patch("subprocess.run")
    def test_run_basic_memory_success(self, mock_run):
        """Test run_basic_memory when basic-memory is available."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "test output"
        mock_run.return_value = mock_result

        # Call the function
        result = run_basic_memory(["test", "args"])

        # Check the result
        assert result.returncode == 0
        assert result.stdout == "test output"
        mock_run.assert_called_once_with(
            ["uvx", "basic-memory", "test", "args"],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("subprocess.run")
    def test_run_basic_memory_not_found(self, mock_run):
        """Test run_basic_memory when basic-memory is not found."""
        # Setup mock to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError("No such file")

        # Call the function and check for expected exception
        with pytest.raises(typer.Exit) as excinfo:
            run_basic_memory(["test"])

        # Check exit code is 1
        assert excinfo.value.exit_code == 1


class TestMemoryHelperFunctions:
    """Test additional helper functions for memory module."""

    def test_get_activity_types(self):
        """Test activity type options for autocompletion."""
        from skogcli.memory import get_activity_types

        types = get_activity_types()

        # Verify expected activity types
        assert "entity" in types
        assert "observation" in types
        assert "relation" in types
        assert "note" in types
        assert "file" in types

    def test_get_timeframe_options(self):
        """Test timeframe options for autocompletion."""
        from skogcli.memory import get_timeframe_options

        timeframes = get_timeframe_options()

        # Verify expected timeframe formats
        assert "2d" in timeframes
        assert "1w" in timeframes
        assert "1m" in timeframes
        assert "today" in timeframes
        assert "this-week" in timeframes

    @patch("skogcli.memory.run_basic_memory")
    def test_get_note_identifiers_success(self, mock_run):
        """Test note identifier autocompletion."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "notes": [
                    {"permalink": "notes/test-note", "title": "Test Note"},
                    {"permalink": "ideas/great-idea", "title": "Great Idea"},
                ]
            }
        )
        mock_run.return_value = mock_result

        from skogcli.memory import get_note_identifiers

        identifiers = get_note_identifiers()

        # Verify identifier extraction
        assert "notes/test-note" in identifiers
        assert "Test Note" in identifiers
        assert "latest" in identifiers
        assert "recent" in identifiers

    @patch("skogcli.memory.run_basic_memory")
    def test_get_note_identifiers_fallback(self, mock_run):
        """Test note identifier fallback when basic-memory unavailable."""
        # Setup mock to fail
        mock_run.side_effect = Exception("Connection failed")

        from skogcli.memory import get_note_identifiers

        identifiers = get_note_identifiers()

        # Verify fallback identifiers
        assert "latest" in identifiers
        assert "recent" in identifiers
        assert "todo" in identifiers
