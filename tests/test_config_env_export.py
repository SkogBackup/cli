"""Tests for environment variable export functionality in config system."""

import os
import subprocess
import tempfile
from pathlib import Path


class TestConfigEnvExport:
    """Test environment variable export functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Store original environment variables that might affect config
        self.original_home = os.environ.get("HOME")
        self.original_skogai_vars = {}
        for key in list(os.environ.keys()):
            if key.startswith("SKOGAI_TEST_"):
                self.original_skogai_vars[key] = os.environ[key]
                del os.environ[key]  # Remove to ensure clean test environment

        # Create a temporary config directory for testing
        self.test_home = Path(tempfile.mkdtemp())
        os.environ["HOME"] = str(self.test_home)

    def teardown_method(self):
        """Clean up after each test."""
        # Restore original environment
        if self.original_home:
            os.environ["HOME"] = self.original_home
        else:
            del os.environ["HOME"]

        # Restore original SKOGAI environment variables
        for key, value in self.original_skogai_vars.items():
            os.environ[key] = value

        # Clean up the test directory
        import shutil

        shutil.rmtree(self.test_home, ignore_errors=True)

    def test_config_set_env_variable(self):
        """Test that we can set environment variables via config."""
        # Set an environment variable via config
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "claude.env.MYENV", "test"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # Verify it was stored
        get_result = subprocess.run(
            ["uv", "run", "skogcli", "config", "get", "claude.env.MYENV"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert get_result.returncode == 0
        assert "test" in get_result.stdout

    def test_config_export_env_command_exists(self):
        """Test that export-env command exists and shows help."""
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "export-env", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed and show help
        assert result.returncode == 0
        assert "export" in result.stdout.lower()

    def test_config_export_env_generates_export_statements(self):
        """Test that export-env generates bash export statements."""
        # First set some environment variables
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "claude.env.TEST_VAR1", "value1"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "claude.env.TEST_VAR2", "value2"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Export them
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "export-env"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # Should contain export statements
        assert "export TEST_VAR1=" in result.stdout
        assert "export TEST_VAR2=" in result.stdout
        assert "value1" in result.stdout
        assert "value2" in result.stdout

    def test_config_export_env_with_namespace_filter(self):
        """Test that export-env can filter by namespace."""
        # Set vars in different namespaces
        subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "set",
                "claude.env.CLAUDE_VAR",
                "claude_value",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "set",
                "agent.env.AGENT_VAR",
                "agent_value",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Export only claude namespace
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "export-env", "--namespace", "claude"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # Should contain only claude vars
        assert "CLAUDE_VAR" in result.stdout
        assert "claude_value" in result.stdout
        assert "AGENT_VAR" not in result.stdout

    def test_config_export_env_to_file(self):
        """Test that export-env can write to a file."""
        # Set an environment variable
        subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "set",
                "claude.env.FILE_VAR",
                "file_value",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Export to a file
        env_file = self.test_home / "test.env"
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "export-env", "--output", str(env_file)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # File should exist and contain export statement
        assert env_file.exists()
        content = env_file.read_text()
        assert "export FILE_VAR=" in content
        assert "file_value" in content

    def test_config_list_env_variables(self):
        """Test that we can list only environment variables."""
        # Set some regular config and env vars
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "ui.theme", "dark"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "set",
                "claude.env.LIST_VAR",
                "list_value",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # List only env vars
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "list", "--env-only"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # Should contain env vars but not regular config
        assert "LIST_VAR" in result.stdout or "claude.env.LIST_VAR" in result.stdout
        assert "ui.theme" not in result.stdout

    def test_config_unset_env_variable(self):
        """Test that we can unset environment variables."""
        # Set an environment variable
        subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "set",
                "claude.env.UNSET_VAR",
                "unset_value",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Verify it exists
        get_result = subprocess.run(
            ["uv", "run", "skogcli", "config", "get", "claude.env.UNSET_VAR"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        assert get_result.returncode == 0

        # Unset it
        unset_result = subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "claude.env.UNSET_VAR", "null"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        assert unset_result.returncode == 0

        # Verify it's gone from export output
        export_result = subprocess.run(
            ["uv", "run", "skogcli", "config", "export-env"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        assert "UNSET_VAR" not in export_result.stdout
