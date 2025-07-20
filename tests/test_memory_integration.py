"""Real integration tests for SkogCLI memory commands against live basic-memory."""

import pytest
import subprocess
import tempfile
import shutil
import json
import os
from pathlib import Path
from typer.testing import CliRunner
from skogcli import app


class TestMemoryIntegrationLive:
    """Test SkogCLI memory commands against real basic-memory instance."""

    def setup_method(self):
        """Set up isolated test environment for each test."""
        # Create temporary directory for test project
        self.test_dir = Path(tempfile.mkdtemp(prefix="skogcli_test_"))
        self.test_project_name = f"test_project_{os.getpid()}"

        # Create test project in basic-memory
        result = subprocess.run(
            [
                "basic-memory",
                "project",
                "add",
                self.test_project_name,
                str(self.test_dir),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(f"Could not create test project: {result.stderr}")

        # Set as default project for this test
        subprocess.run(
            ["basic-memory", "project", "default", self.test_project_name],
            capture_output=True,
            text=True,
        )

        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up test environment."""
        try:
            # Remove test project
            subprocess.run(
                ["basic-memory", "project", "remove", self.test_project_name],
                capture_output=True,
                text=True,
            )

            # Clean up test directory
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
        except Exception:
            pass  # Best effort cleanup

    def test_write_note_integration(self):
        """Test writing a note through SkogCLI to real basic-memory."""
        # Write note using SkogCLI
        result = self.runner.invoke(
            app,
            [
                "memory",
                "write",
                "Test Integration Note",
                "test-folder",
                "--content",
                "This is integration test content",
                "--tags",
                "integration,test",
                "--project",
                self.test_project_name,
            ],
        )

        # Verify SkogCLI succeeded
        assert result.exit_code == 0
        assert "✓ Note saved: Test Integration Note in test-folder" in result.stdout

        # Verify note actually exists in basic-memory
        verify_result = subprocess.run(
            [
                "basic-memory",
                "--project",
                self.test_project_name,
                "tool",
                "read-note",
                "test-folder/Test Integration Note",
            ],
            capture_output=True,
            text=True,
        )

        assert verify_result.returncode == 0
        # basic-memory CLI returns markdown with YAML frontmatter, not JSON
        output = verify_result.stdout
        assert "This is integration test content" in output
        assert "title: Test Integration Note" in output
        assert "tags:" in output and "integration,test" in output

    def test_read_note_integration(self):
        """Test reading a note through SkogCLI from real basic-memory."""
        # First create a note directly with basic-memory
        create_result = subprocess.run(
            [
                "basic-memory",
                "--project",
                self.test_project_name,
                "tool",
                "write-note",
                "--title",
                "Direct Created Note",
                "--folder",
                "direct",
                "--content",
                "# Direct Note\n\nThis was created directly.",
            ],
            capture_output=True,
            text=True,
        )

        assert create_result.returncode == 0

        # Now read it through SkogCLI
        result = self.runner.invoke(
            app,
            [
                "memory",
                "read",
                "direct/Direct Created Note",
                "--project",
                self.test_project_name,
            ],
        )

        assert result.exit_code == 0
        # Should contain the markdown content
        assert "Direct Note" in result.stdout
        assert "This was created directly" in result.stdout
        # Should show metadata (SkogCLI formats it as "title: Title Name")
        assert "title:" in result.stdout
        assert "Direct Created Note" in result.stdout

    def test_search_integration(self):
        """Test searching notes through SkogCLI in real basic-memory."""
        # Create multiple test notes
        notes = [
            ("Search Test One", "search-test", "Content about Python programming"),
            ("Search Test Two", "search-test", "Content about JavaScript development"),
            ("Other Note", "other", "Unrelated content about cooking"),
        ]

        for title, folder, content in notes:
            subprocess.run(
                [
                    "basic-memory",
                    "--project",
                    self.test_project_name,
                    "tool",
                    "write-note",
                    "--title",
                    title,
                    "--folder",
                    folder,
                    "--content",
                    content,
                ],
                capture_output=True,
                text=True,
            )

        # Search through SkogCLI
        result = self.runner.invoke(
            app,
            ["memory", "search", "programming", "--project", self.test_project_name],
        )

        assert result.exit_code == 0
        # Should find the Python note but not JavaScript or cooking notes
        assert "Search Test One" in result.stdout
        assert (
            "Python programming" not in result.stdout
        )  # Content shouldn't be in summary
        # Should show search results formatting
        assert "Search Results: 'programming'" in result.stdout

    def test_list_activity_integration(self):
        """Test listing recent activity through SkogCLI from real basic-memory."""
        # Create a note to ensure we have recent activity
        subprocess.run(
            [
                "basic-memory",
                "--project",
                self.test_project_name,
                "tool",
                "write-note",
                "--title",
                "Recent Activity Note",
                "--folder",
                "activity",
                "--content",
                "This note should appear in recent activity",
            ],
            capture_output=True,
            text=True,
        )

        # List recent activity through SkogCLI
        result = self.runner.invoke(
            app,
            [
                "memory",
                "list",
                "--project",
                self.test_project_name,
                "--timeframe",
                "1d",
            ],
        )

        assert result.exit_code == 0
        assert "Recent Activity" in result.stdout
        assert "Recent Activity Note" in result.stdout

    def test_sync_integration(self):
        """Test syncing through SkogCLI with real basic-memory."""
        result = self.runner.invoke(
            app, ["memory", "sync", "--project", self.test_project_name]
        )

        # Sync should succeed (even if no changes)
        assert result.exit_code == 0
        # Should contain some sync output
        assert len(result.stdout.strip()) > 0

    def test_status_integration(self):
        """Test status command through SkogCLI with real basic-memory."""
        result = self.runner.invoke(
            app, ["memory", "status", "--project", self.test_project_name]
        )

        assert result.exit_code == 0
        # Should show project information
        assert "Project:" in result.stdout
        assert self.test_project_name in result.stdout
        # Should show statistics
        assert "Statistics" in result.stdout

    def test_write_read_search_workflow(self):
        """Test complete workflow: write → read → search integration."""
        # Step 1: Write a note
        write_result = self.runner.invoke(
            app,
            [
                "memory",
                "write",
                "Workflow Test Note",
                "workflow",
                "--content",
                "# Workflow Test\n\nThis tests the complete workflow with unique_marker_12345",
                "--project",
                self.test_project_name,
            ],
        )
        assert write_result.exit_code == 0

        # Step 2: Read the note back
        read_result = self.runner.invoke(
            app,
            [
                "memory",
                "read",
                "workflow/Workflow Test Note",
                "--project",
                self.test_project_name,
            ],
        )
        assert read_result.exit_code == 0
        assert "Workflow Test" in read_result.stdout
        assert "unique_marker_12345" in read_result.stdout

        # Step 3: Search for the note
        search_result = self.runner.invoke(
            app,
            [
                "memory",
                "search",
                "unique_marker_12345",
                "--project",
                self.test_project_name,
            ],
        )
        assert search_result.exit_code == 0
        assert "Workflow Test Note" in search_result.stdout

    def test_error_handling_integration(self):
        """Test error handling with real basic-memory."""
        # Try to read non-existent note
        result = self.runner.invoke(
            app,
            ["memory", "read", "nonexistent/note", "--project", self.test_project_name],
        )

        # Should handle error gracefully
        assert result.exit_code == 1
        assert "Error:" in result.stdout

    def test_bm_passthrough_integration(self):
        """Test basic-memory passthrough command with real integration."""
        # Use passthrough to call basic-memory directly
        result = self.runner.invoke(
            app, ["memory", "bm", "--project", self.test_project_name, "status"]
        )

        assert result.exit_code == 0
        # Should contain basic-memory status output
        assert len(result.stdout.strip()) > 0

    def test_json_output_format_integration(self):
        """Test JSON output format with real data."""
        # Create a note first
        subprocess.run(
            [
                "basic-memory",
                "--project",
                self.test_project_name,
                "tool",
                "write-note",
                "--title",
                "JSON Test Note",
                "--folder",
                "json-test",
                "--content",
                "Content for JSON testing",
            ],
            capture_output=True,
            text=True,
        )

        # Search with JSON format
        result = self.runner.invoke(
            app,
            [
                "memory",
                "search",
                "JSON",
                "--project",
                self.test_project_name,
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0
        # SkogCLI should pass through JSON format from basic-memory
        # The exact format depends on what basic-memory returns
        assert len(result.stdout.strip()) > 0


class TestMemoryRequiresBasicMemory:
    """Test that memory commands fail appropriately when basic-memory is not available."""

    def test_missing_basic_memory_detection(self):
        """Test that SkogCLI detects when basic-memory is missing."""
        # This test would need to temporarily hide basic-memory
        # For now, we'll skip it since we know basic-memory is available
        pytest.skip("basic-memory is available - cannot test missing binary scenario")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
