"""Tests for the SkogCLI memory subcommand's CLI interface."""

from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
import json
import os

from skogcli import app

runner = CliRunner()


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
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

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
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

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
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Failed to create note"
        mock_run.return_value = mock_result

        result = runner.invoke(
            app,
            ["memory", "write", "Failed Note", "notes", "--content", "This will fail"],
        )

        assert result.exit_code == 1
        assert "Error: Failed to create note" in result.stdout

    @patch("skogcli.memory.run_basic_memory")
    def test_read_command_success(self, mock_run):
        """Test memory read with valid identifier."""
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

        result = runner.invoke(app, ["memory", "read", "test-note"])

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
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"content": "Test content"})
        mock_run.return_value = mock_result

        result = runner.invoke(
            app, ["memory", "read", "test-note", "--page", "2", "--page-size", "20"]
        )

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
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Note not found"
        mock_run.return_value = mock_result

        result = runner.invoke(app, ["memory", "read", "nonexistent"])

        assert result.exit_code == 1
        assert "Error: Note not found" in result.stdout

    @patch("skogcli.memory.run_basic_memory")
    def test_search_command_basic(self, mock_run):
        """Test memory search with simple query."""
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

        result = runner.invoke(app, ["memory", "search", "test query"])

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
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"results": []})
        mock_run.return_value = mock_result

        result = runner.invoke(
            app, ["memory", "search", "test", "--permalink", "--title"]
        )

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
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"results": []}'
        mock_run.return_value = mock_result

        result = runner.invoke(app, ["memory", "search", "test", "--format", "json"])

        assert result.exit_code == 0
        assert '{"results": []}' in result.stdout

    @patch("skogcli.memory.run_basic_memory")
    def test_list_command_default(self, mock_run):
        """Test memory list with default parameters."""
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

        result = runner.invoke(app, ["memory", "list"])

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
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Sync completed successfully"
        mock_run.return_value = mock_result

        result = runner.invoke(app, ["memory", "sync"])

        expected_cmd = ["sync"]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0
        assert "Sync completed successfully" in result.stdout

    @patch("skogcli.memory.run_basic_memory")
    def test_status_command_default(self, mock_run):
        """Test memory status with default settings."""
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

        result = runner.invoke(app, ["memory", "status"])

        expected_cmd = ["project", "info"]
        mock_run.assert_called_once_with(expected_cmd)
        assert result.exit_code == 0


class TestMemoryErrorHandling:
    """Test error handling in memory module."""

    @patch("skogcli.memory.run_basic_memory")
    def test_json_decode_error_handling(self, mock_run):
        """Test when basic-memory returns invalid JSON."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json response"
        mock_run.return_value = mock_result

        result = runner.invoke(app, ["memory", "read", "test"])

        assert result.exit_code == 0

    @patch("subprocess.run")
    def test_missing_basic_memory_binary(self, mock_run):
        """Test when basic-memory binary not found."""
        mock_run.side_effect = FileNotFoundError("basic-memory not found")

        result = runner.invoke(
            app, ["memory", "write", "test", "notes", "--content", "test"]
        )

        assert result.exit_code == 1
        assert "basic-memory not found" in result.stdout


class TestMemoryIntegration:
    """Integration tests for memory module."""

    def test_memory_command_without_basic_memory(self):
        """Test memory command when basic-memory is not in PATH."""
        with patch.dict(os.environ, {"PATH": "/tmp/nonexistent"}):
            result = runner.invoke(app, ["memory", "status"])

            assert result.exit_code == 1
            assert "basic-memory not found" in result.stdout
