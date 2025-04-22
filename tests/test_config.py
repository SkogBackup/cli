"""Tests for skogcli config functionality."""

import json
import subprocess
import pytest
from pathlib import Path
import os
import shutil


class TestConfig:
    """Tests for the config functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary config directory for testing
        self.original_home = os.environ.get("HOME")
        self.test_home = Path("/tmp/skogcli_test_home")
        self.test_home.mkdir(parents=True, exist_ok=True)
        self.test_config_dir = self.test_home / ".config" / "skogcli"
        self.test_config_dir.mkdir(parents=True, exist_ok=True)
        self.test_config_file = self.test_config_dir / "config.json"
        
        # Point HOME to our test directory
        os.environ["HOME"] = str(self.test_home)

    def teardown_method(self):
        """Clean up after each test."""
        # Restore the original HOME environment variable
        if self.original_home:
            os.environ["HOME"] = self.original_home
        
        # Clean up the test directory
        shutil.rmtree(self.test_home, ignore_errors=True)

    def test_config_show(self):
        """Test that config --show displays the configuration."""
        # Run the command
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "show"],
            capture_output=True,
            text=True,
        )
        
        # Check that the command succeeded
        assert result.returncode == 0
        
        # Check that the output contains expected configuration sections
        assert "memory" in result.stdout
        assert "ui" in result.stdout

    def test_config_list(self):
        """Test that config list displays the configuration keys."""
        # Run the command
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "list"],
            capture_output=True,
            text=True,
        )
        
        # Check that the command succeeded
        assert result.returncode == 0
        
        # Check that the output contains expected keys
        assert "Available configuration keys" in result.stdout
        assert "memory.page_size" in result.stdout
        assert "ui.theme" in result.stdout

    def test_config_get(self):
        """Test that config get retrieves a specific setting."""
        # Run the command to get memory.page_size
        result = subprocess.run(
            ["uv", "run", "skogcli", "config", "get", "memory.page_size"],
            capture_output=True,
            text=True,
        )
        
        # Check that the command succeeded
        assert result.returncode == 0
        
        # Check that the output contains the key and a value
        assert "memory.page_size" in result.stdout
        assert "10" in result.stdout  # Default value from settings.py

    def test_config_set_and_get(self):
        """Test setting and then getting a configuration value."""
        # Set a config value
        set_result = subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "ui.theme", "dark"],
            capture_output=True,
            text=True,
        )
        
        # Check that the set command succeeded
        assert set_result.returncode == 0
        assert "Set ui.theme" in set_result.stdout
        
        # Now get the value to verify it was set
        get_result = subprocess.run(
            ["uv", "run", "skogcli", "config", "get", "ui.theme"],
            capture_output=True,
            text=True,
        )
        
        # Check that the get command succeeded and returns the set value
        assert get_result.returncode == 0
        assert "ui.theme = dark" in get_result.stdout

    def test_config_reset(self):
        """Test resetting the configuration to defaults."""
        # First, set a non-default value
        subprocess.run(
            ["uv", "run", "skogcli", "config", "set", "ui.theme", "dark"],
            capture_output=True,
            text=True,
        )
        
        # Now reset the config (with --yes to skip confirmation)
        reset_result = subprocess.run(
            ["uv", "run", "skogcli", "config", "reset", "--yes"],
            capture_output=True,
            text=True,
        )
        
        # Check that the reset command succeeded
        assert reset_result.returncode == 0
        assert "reset to defaults" in reset_result.stdout.lower()
        
        # Verify that the value was reset by getting it
        get_result = subprocess.run(
            ["uv", "run", "skogcli", "config", "get", "ui.theme"],
            capture_output=True,
            text=True,
        )
        
        # Should be back to the default value
        assert get_result.returncode == 0
        assert "ui.theme = default" in get_result.stdout