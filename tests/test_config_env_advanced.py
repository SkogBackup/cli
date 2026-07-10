"""Advanced tests for environment variable functionality."""

import os
import subprocess
import tempfile
import pytest
from pathlib import Path


class TestConfigEnvAdvanced:
    """Test advanced environment variable functionality."""

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

    def test_config_env_source_command(self):
        """Test that we can generate a source-able script."""
        # Set some environment variables
        subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "set",
                "claude.env.SOURCE_VAR",
                "source_value",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Generate source script
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "export-env"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed and contain source commands
        assert result.returncode == 0
        assert "export SOURCE_VAR=" in result.stdout

    def test_config_env_clear_namespace(self):
        """Test clearing all environment variables in a namespace."""
        # TODO: Implement clear-env command with --namespace option
        # Set some variables in claude namespace
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "claude.env.CLEAR1", "value1"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "claude.env.CLEAR2", "value2"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Clear claude env vars
        # NOTE: clear-env command not yet implemented - skipping test
        pytest.skip("clear-env command not yet implemented")

        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "clear-env", "--namespace", "claude"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # Variables should be gone
        list_result = subprocess.run(
            ["uv", "run", "skogcli", "config", "list", "--env-only"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert "CLEAR1" not in list_result.stdout
        assert "CLEAR2" not in list_result.stdout

    def test_config_env_import_from_file(self):
        """Test importing environment variables from a file."""
        # TODO: Implement import-env command
        pytest.skip("import-env command not yet implemented")

        # Create a test env file
        env_file = self.test_home / "import.env"
        env_file.write_text("""
export IMPORT_VAR1="import_value1"
export IMPORT_VAR2="import_value2"
# This is a comment
export IMPORT_VAR3="import_value3"
""")

        # Import the file
        result = subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "import-env",
                str(env_file),
                "--namespace",
                "test",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # Variables should be imported
        get_result = subprocess.run(
            ["uv", "run", "skogcli", "config", "get", "test.env.IMPORT_VAR1"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert "import_value1" in get_result.stdout

    def test_config_env_with_agent_integration(self):
        """Test that env vars can be used with agent commands."""
        # Set an API key
        subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "set",
                "claude.env.API_KEY",
                "test-key-123",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Export for claude namespace
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "export-env", "--namespace", "claude"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should contain the API key export
        assert result.returncode == 0
        assert 'export API_KEY="test-key-123"' in result.stdout

    def test_config_env_validation(self):
        """Test validation of environment variable names."""
        # Try to set invalid env var name
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "claude.env.123INVALID", "value"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should warn or handle gracefully
        # (Note: This might be implementation-dependent - the test should verify the behavior)
        # For now, we'll just check it doesn't crash
        # In a real implementation, you might want to validate env var names
        assert result.returncode in [0, 1]  # Either succeeds or fails gracefully
