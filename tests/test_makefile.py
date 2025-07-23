"""Tests for Makefile functionality."""

import subprocess
from pathlib import Path


class TestMakeCommands:
    """Test suite for make commands."""

    def test_makefile_exists(self):
        """Test that Makefile exists in project root."""
        makefile_path = Path("Makefile")
        assert makefile_path.exists(), "Makefile should exist in project root"

    def test_make_help_command(self):
        """Test that 'make help' command works and shows available commands."""
        result = subprocess.run(
            ["make", "help"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0, f"make help failed: {result.stderr}"
        assert "Available commands:" in result.stdout
        assert "help" in result.stdout
        assert "install" in result.stdout
        assert "test" in result.stdout
        # Verify removed placeholder commands are not present
        assert "team-setup" not in result.stdout
        assert "onboard" not in result.stdout
        assert "docs-serve" not in result.stdout

    def test_make_install_command(self):
        """Test that 'make install' command works."""
        result = subprocess.run(
            ["make", "install"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0, f"make install failed: {result.stderr}"

    def test_make_test_command(self):
        """Test that 'make test' command is available (without running it to avoid recursion)."""
        # Check that the Makefile contains the test target
        with open("Makefile", "r") as f:
            makefile_content = f.read()

        assert "test:" in makefile_content, "Makefile should contain test target"
        assert "uv run pytest" in makefile_content, "test target should use pytest"

    def test_make_format_command(self):
        """Test that 'make format' command works."""
        result = subprocess.run(
            ["make", "format"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0, f"make format failed: {result.stderr}"

    def test_make_lint_command(self):
        """Test that 'make lint' command works."""
        result = subprocess.run(
            ["make", "lint"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0, f"make lint failed: {result.stderr}"

    def test_make_clean_command(self):
        """Test that 'make clean' command works."""
        result = subprocess.run(
            ["make", "clean"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0, f"make clean failed: {result.stderr}"

    def test_make_build_command(self):
        """Test that 'make build' command works."""
        result = subprocess.run(
            ["make", "build"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0, f"make build failed: {result.stderr}"
