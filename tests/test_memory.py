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


class TestMemoryCommands:
    """Test memory CLI commands with mocked basic-memory interactions."""

    @patch("skogcli.memory.run_basic_memory")
    def test_bm_passthrough(self, mock_run):
        """Test basic-memory passthrough command with various arguments."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "basic-memory output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(app, ["memory", "bm", "tool", "list-projects"])

        # Verify the command was passed through correctly
        mock_run.assert_called_once_with(["tool", "list-projects"])
        assert result.exit_code == 0
        assert "basic-memory output" in result.stdout

    @patch("skogcli.memory.run_basic_memory")
    def test_write_command_success(self, mock_run):
        """Test memory write command with valid inputs."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Note created successfully"
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "memory",
                "write",
                "Test Note",
                "notes",
                "--content",
                "This is test content",
            ],
        )

        # Verify the command was called correctly
        expected_cmd = [
            "tool",
            "write-note",
            "--title",
            "Test Note",
            "--folder",
            "notes",
            "--content",
            "This is test content",
        ]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0
        assert "✓ Note saved: Test Note in notes" in result.stdout

    @patch("skogcli.memory.run_basic_memory")
    def test_write_command_with_tags(self, mock_run):
        """Test memory write with comma-separated tags."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "memory",
                "write",
                "Tagged Note",
                "projects",
                "--content",
                "Content with tags",
                "--tags",
                "work,important,2025",
            ],
        )

        # Verify tags were passed correctly
        expected_cmd = [
            "tool",
            "write-note",
            "--title",
            "Tagged Note",
            "--folder",
            "projects",
            "--tags",
            "work,important,2025",
            "--content",
            "Content with tags",
        ]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0

    @patch("skogcli.memory.run_basic_memory")
    def test_write_command_with_project(self, mock_run):
        """Test memory write with specific project."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "memory",
                "write",
                "Project Note",
                "meetings",
                "--content",
                "Meeting notes",
                "--project",
                "work-project",
            ],
        )

        # Verify project parameter was handled correctly
        expected_cmd = [
            "--project",
            "work-project",
            "tool",
            "write-note",
            "--title",
            "Project Note",
            "--folder",
            "meetings",
            "--content",
            "Meeting notes",
        ]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0

    @patch("skogcli.memory.run_basic_memory")
    def test_write_command_failure(self, mock_run):
        """Test memory write when basic-memory fails."""
        # Setup mock to fail
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Failed to create note"
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["memory", "write", "Failed Note", "notes", "--content", "This will fail"],
        )

        # Verify error handling
        assert result.exit_code == 1
        assert "Error: Failed to create note" in result.stdout

    @patch("skogcli.memory.run_basic_memory")
    def test_read_command_success(self, mock_run):
        """Test memory read with valid identifier."""
        # Setup mock with JSON response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "content": "# Test Note\n\nThis is test content",
                "title": "Test Note",
                "file_path": "/path/to/note.md",
                "created_at": "2025-01-01T10:00:00.000Z",
                "updated_at": "2025-01-01T11:00:00.000Z",
            }
        )
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(app, ["memory", "read", "test-note"])

        # Verify the command was called correctly
        expected_cmd = [
            "tool",
            "read-note",
            "test-note",
            "--page",
            "1",
            "--page-size",
            "10",
        ]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0

    @patch("skogcli.memory.run_basic_memory")
    def test_read_command_with_pagination(self, mock_run):
        """Test memory read with pagination options."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"content": "Test content"})
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(
            app, ["memory", "read", "test-note", "--page", "2", "--page-size", "20"]
        )

        # Verify pagination parameters
        expected_cmd = [
            "tool",
            "read-note",
            "test-note",
            "--page",
            "2",
            "--page-size",
            "20",
        ]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0

    @patch("skogcli.memory.run_basic_memory")
    def test_read_command_failure(self, mock_run):
        """Test memory read when note not found."""
        # Setup mock to fail
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Note not found"
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(app, ["memory", "read", "nonexistent"])

        # Verify error handling
        assert result.exit_code == 1
        assert "Error: Note not found" in result.stdout

    @patch("skogcli.memory.run_basic_memory")
    def test_search_command_basic(self, mock_run):
        """Test memory search with simple query."""
        # Setup mock with search results
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "results": [
                    {
                        "type": "note",
                        "title": "Test Note",
                        "created_at": "2025-01-01T10:00:00.000Z",
                        "file_path": "/path/to/note.md",
                    }
                ]
            }
        )
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(app, ["memory", "search", "test query"])

        # Verify search command
        expected_cmd = [
            "tool",
            "search-notes",
            "test query",
            "--page",
            "1",
            "--page-size",
            "10",
        ]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0

    @patch("skogcli.memory.run_basic_memory")
    def test_search_command_with_filters(self, mock_run):
        """Test memory search with permalink/title filters."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"results": []})
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(
            app, ["memory", "search", "test", "--permalink", "--title"]
        )

        # Verify filters were applied
        expected_cmd = [
            "tool",
            "search-notes",
            "test",
            "--page",
            "1",
            "--page-size",
            "10",
            "--permalink",
            "--title",
        ]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0

    @patch("skogcli.memory.run_basic_memory")
    def test_search_command_json_format(self, mock_run):
        """Test memory search with JSON output format."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"results": []}'
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(app, ["memory", "search", "test", "--format", "json"])

        # Verify JSON output is passed through
        assert result.exit_code == 0
        assert '{"results": []}' in result.stdout

    @patch("skogcli.memory.run_basic_memory")
    def test_list_command_default(self, mock_run):
        """Test memory list with default parameters."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "results": [
                    {
                        "primary_result": {
                            "type": "note",
                            "title": "Recent Note",
                            "created_at": "2025-01-01T10:00:00.000Z",
                            "file_path": "/path/to/note.md",
                        }
                    }
                ]
            }
        )
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(app, ["memory", "list"])

        # Verify default parameters
        expected_cmd = [
            "tool",
            "recent-activity",
            "--depth",
            "1",
            "--timeframe",
            "7d",
            "--page",
            "1",
            "--page-size",
            "10",
            "--max-related",
            "5",
        ]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0

    @patch("skogcli.memory.run_basic_memory")
    def test_sync_command_basic(self, mock_run):
        """Test memory sync with default options."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Sync completed successfully"
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(app, ["memory", "sync"])

        # Verify sync command
        expected_cmd = ["sync"]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0
        assert "Sync completed successfully" in result.stdout

    @patch("skogcli.memory.run_basic_memory")
    def test_status_command_default(self, mock_run):
        """Test memory status with default settings."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "project_name": "test-project",
                "project_path": "/path/to/project",
                "statistics": {
                    "total_entities": 10,
                    "entity_types": {"note": 5},
                    "total_observations": 3,
                    "total_relations": 2,
                },
                "system": {"watch_status": {"last_scan": "2025-01-01T10:00:00Z"}},
            }
        )
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(app, ["memory", "status"])

        # Verify status command
        expected_cmd = ["project", "info"]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0


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


class TestMemoryErrorHandling:
    """Test error handling in memory module."""

    @patch("skogcli.memory.run_basic_memory")
    def test_json_decode_error_handling(self, mock_run):
        """Test when basic-memory returns invalid JSON."""
        # Setup mock with invalid JSON
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json response"
        mock_run.return_value = mock_result

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(app, ["memory", "read", "test"])

        # Should not crash, should handle gracefully
        assert result.exit_code == 0

    @patch("subprocess.run")
    def test_missing_basic_memory_binary(self, mock_run):
        """Test when basic-memory binary not found."""
        # Setup mock to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError("basic-memory not found")

        from typer.testing import CliRunner
        from skogcli import app

        runner = CliRunner()
        result = runner.invoke(
            app, ["memory", "write", "test", "notes", "--content", "test"]
        )

        # Verify error message about installation
        assert result.exit_code == 1
        assert "basic-memory not found" in result.stdout
