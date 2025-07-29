"""Tests for multiple namespace support in environment variable export."""

import os
import subprocess
import tempfile
from pathlib import Path


class TestMultiNamespaceExport:
    """Test multiple namespace environment variable export functionality."""

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

    def test_multiple_namespaces_comma_separated(self):
        """Test exporting from multiple namespaces using comma separation."""
        # Set up variables in different namespaces
        subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "set",
                "shared.env.BASE_URL",
                "https://api.example.com",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "shared.env.TIMEOUT", "30"],
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
                "claude.env.API_KEY",
                "claude-key-123",
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
                "claude.env.MODEL",
                "claude-3-sonnet",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Export from multiple namespaces
        result = subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "export-env",
                "--namespace",
                "shared,claude",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed and contain variables from both namespaces
        assert result.returncode == 0
        assert "export BASE_URL=" in result.stdout
        assert "export TIMEOUT=" in result.stdout
        assert "export API_KEY=" in result.stdout
        assert "export MODEL=" in result.stdout

    def test_multiple_namespaces_precedence_override(self):
        """Test that later namespaces override earlier ones for same variable names."""
        # Set up conflicting variables
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "shared.env.DEBUG", "false"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "development.env.DEBUG", "true"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Export with shared first, then development (development should win)
        result = subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "export-env",
                "--namespace",
                "shared,development",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed and development should override shared
        assert result.returncode == 0
        assert 'export DEBUG="True"' in result.stdout  # development value wins
        assert 'export DEBUG="False"' not in result.stdout  # shared value is overridden

    def test_multiple_namespaces_with_spaces(self):
        """Test multiple namespaces with spaces around commas."""
        # Set up variables
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "base.env.VAR1", "base_value"],
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
                "override.env.VAR2",
                "override_value",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Export with spaces around commas
        result = subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "export-env",
                "--namespace",
                "base, override",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed and handle spaces gracefully
        assert result.returncode == 0
        assert "export VAR1=" in result.stdout
        assert "export VAR2=" in result.stdout

    def test_multiple_namespaces_empty_namespace(self):
        """Test behavior when one of the namespaces is empty."""
        # Set up variables in only one namespace
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "existing.env.VAR", "value"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Export from existing and non-existing namespace
        result = subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "export-env",
                "--namespace",
                "existing,nonexistent",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed and export variables from existing namespace
        assert result.returncode == 0
        assert "export VAR=" in result.stdout

    def test_multiple_namespaces_to_file(self):
        """Test exporting multiple namespaces to a file."""
        # Set up variables
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "prod.env.DB_HOST", "prod-db"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "app.env.APP_NAME", "myapp"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Export to file
        env_file = self.test_home / "multi.env"
        result = subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "export-env",
                "--namespace",
                "prod,app",
                "--output",
                str(env_file),
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # File should exist and contain both namespaces
        assert env_file.exists()
        content = env_file.read_text()
        assert "export DB_HOST=" in content
        assert "export APP_NAME=" in content

    def test_three_namespaces_layered_config(self):
        """Test a realistic scenario with three layers: base, environment, service."""
        # Base configuration
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "base.env.LOG_LEVEL", "info"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "base.env.TIMEOUT", "30"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Production environment overrides
        subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "set",
                "production.env.LOG_LEVEL",
                "warn",
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
                "production.env.DB_HOST",
                "prod-db",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Service-specific settings
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "api.env.PORT", "8080"],
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
                "api.env.TIMEOUT",
                "60",
            ],  # Override base timeout
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Export all three layers: base -> production -> api
        result = subprocess.run(
            [
                "uv",
                "run",
                "skogcli",
                "config",
                "export-env",
                "--namespace",
                "base,production,api",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed and show proper precedence
        assert result.returncode == 0
        assert 'export LOG_LEVEL="warn"' in result.stdout  # production overrides base
        assert 'export TIMEOUT="60"' in result.stdout  # api overrides base
        assert 'export DB_HOST="prod-db"' in result.stdout  # production adds this
        assert 'export PORT="8080"' in result.stdout  # api adds this
