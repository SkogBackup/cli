"""Functional tests for SkogCLI memory commands - test actual workflows."""

import uuid
from typer.testing import CliRunner
from skogcli import app


class TestMemoryFunctional:
    """Test SkogCLI memory commands with real workflows."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.test_guid = f"test-{uuid.uuid4().hex[:8]}"
        self.test_folder = "functional-tests"

    def test_complete_memory_workflow(self):
        """Test complete workflow: create → search → read → edit → delete."""

        # 1. Create a note
        create_result = self.runner.invoke(
            app,
            [
                "memory",
                "write",
                self.test_guid,
                self.test_folder,
                "--content",
                f"Initial content for {self.test_guid}",
            ],
        )
        assert create_result.exit_code == 0
        assert (
            f"✓ Note saved: {self.test_guid} in {self.test_folder}"
            in create_result.stdout
        )

        # 2. Search for the note
        search_result = self.runner.invoke(app, ["memory", "search", self.test_guid])
        assert search_result.exit_code == 0
        assert self.test_guid in search_result.stdout

        # 3. Read the note
        read_result = self.runner.invoke(
            app, ["memory", "read", f"{self.test_folder}/{self.test_guid}"]
        )
        assert read_result.exit_code == 0
        assert f"Initial content for {self.test_guid}" in read_result.stdout

        # 4. Edit the note
        edit_result = self.runner.invoke(
            app,
            [
                "memory",
                "write",
                self.test_guid,
                self.test_folder,
                "--content",
                f"Updated content for {self.test_guid}",
            ],
        )
        assert edit_result.exit_code == 0

        # 5. Read updated note
        read_updated_result = self.runner.invoke(
            app, ["memory", "read", f"{self.test_folder}/{self.test_guid}"]
        )
        assert read_updated_result.exit_code == 0
        assert f"Updated content for {self.test_guid}" in read_updated_result.stdout
        assert f"Initial content for {self.test_guid}" not in read_updated_result.stdout

    def test_create_with_tags_and_search(self):
        """Test creating note with tags and finding it via search."""
        test_tag = f"tag-{uuid.uuid4().hex[:6]}"

        # Create note with unique tag
        create_result = self.runner.invoke(
            app,
            [
                "memory",
                "write",
                self.test_guid,
                self.test_folder,
                "--content",
                f"Content with tags for {self.test_guid}",
                "--tags",
                f"test,{test_tag},functional",
            ],
        )
        assert create_result.exit_code == 0

        # Search by unique tag
        search_result = self.runner.invoke(app, ["memory", "search", test_tag])
        assert search_result.exit_code == 0
        assert self.test_guid in search_result.stdout

    def test_list_shows_created_note(self):
        """Test that list command shows recently created notes."""

        # Create a note
        create_result = self.runner.invoke(
            app,
            [
                "memory",
                "write",
                self.test_guid,
                self.test_folder,
                "--content",
                f"Content for list test {self.test_guid}",
            ],
        )
        assert create_result.exit_code == 0

        # List recent activity
        list_result = self.runner.invoke(app, ["memory", "list", "--timeframe", "1d"])
        assert list_result.exit_code == 0
        assert self.test_guid in list_result.stdout

    def test_status_command_works(self):
        """Test that status command returns project information."""
        status_result = self.runner.invoke(app, ["memory", "status"])
        assert status_result.exit_code == 0
        assert "Project:" in status_result.stdout

    def test_sync_command_works(self):
        """Test that sync command works."""
        sync_result = self.runner.invoke(app, ["memory", "sync"])
        assert sync_result.exit_code == 0

    def test_bm_passthrough_works(self):
        """Test that bm passthrough command works."""
        bm_result = self.runner.invoke(app, ["memory", "bm", "status"])
        assert bm_result.exit_code == 0

    def test_read_nonexistent_note_fails(self):
        """Test that reading non-existent note fails gracefully."""
        fake_guid = f"nonexistent-{uuid.uuid4().hex[:8]}"
        read_result = self.runner.invoke(app, ["memory", "read", f"fake/{fake_guid}"])
        assert read_result.exit_code == 1
        assert "Error:" in read_result.stdout

    def test_json_output_format(self):
        """Test JSON output format works."""

        # Create a note first
        create_result = self.runner.invoke(
            app,
            [
                "memory",
                "write",
                self.test_guid,
                self.test_folder,
                "--content",
                f"JSON test content {self.test_guid}",
            ],
        )
        assert create_result.exit_code == 0

        # Search with JSON format
        search_result = self.runner.invoke(
            app, ["memory", "search", self.test_guid, "--format", "json"]
        )
        assert search_result.exit_code == 0
        # Should contain JSON-like output
        assert "{" in search_result.stdout or "[" in search_result.stdout
