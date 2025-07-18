"""Tests for skogcli memory functionality."""

import pytest
import subprocess
from unittest.mock import patch, MagicMock
import json
import sys
from pathlib import Path
import typer
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
