"""Tests for config functionality without .config directory references.

These tests define the desired behavior after removing .config directory usage.
All tests should FAIL with current implementation and PASS after changes.
"""

import json
import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from src.skogcli.settings import (
    get_config_dir,
    load_settings,
    get_setting,
    set_setting,
)


class TestConfigNoDotConfig:
    """Test config functionality without .config directory references."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Store and clean SKOGAI environment variables that might affect config
        self.original_skogai_vars = {}
        for key in list(os.environ.keys()):
            if key.startswith("SKOGAI_") and ("UI" in key or "THEME" in key):
                self.original_skogai_vars[key] = os.environ[key]
                del os.environ[key]  # Remove to ensure clean test environment

        # Create temporary directories for testing
        self.test_temp_dir = Path(tempfile.mkdtemp())
        self.test_src_data_dir = self.test_temp_dir / "src" / "skogcli" / "data"
        self.test_src_data_dir.mkdir(parents=True, exist_ok=True)

        # Create test default_settings.json
        self.test_default_settings = {
            "credentials": {},
            "settings": {
                "memory": {"page_size": 10, "default_project": None},
                "ui": {"theme": "default", "verbose": False},
                "cli": {"storage_dir": str(self.test_temp_dir / "skogai_config")},
            },
        }

        self.test_default_settings_file = (
            self.test_src_data_dir / "default_settings.json"
        )
        with open(self.test_default_settings_file, "w") as f:
            json.dump(self.test_default_settings, f, indent=2)

    def teardown_method(self):
        """Clean up after each test."""
        # Restore original SKOGAI environment variables
        for key, value in self.original_skogai_vars.items():
            os.environ[key] = value

        shutil.rmtree(self.test_temp_dir, ignore_errors=True)

    def test_config_dir_should_not_use_dotconfig_fallback(self):
        """Test that get_config_dir never falls back to .config directory."""
        # Clear environment variables that might affect config dir
        with patch.dict(os.environ, {}, clear=True):
            # Mock get_setting to return None (no cli.storage_dir setting)
            with patch("src.skogcli.settings.get_setting", return_value=None):
                # This should raise an error instead of falling back to .config
                with pytest.raises((FileNotFoundError, ValueError)):
                    get_config_dir()

    def test_config_dir_uses_environment_variable(self):
        """Test that get_config_dir prioritizes SKOGAI_CONFIG_DIR environment variable."""
        test_config_dir = self.test_temp_dir / "custom_config"

        with patch.dict(os.environ, {"SKOGAI_CONFIG_DIR": str(test_config_dir)}):
            config_dir = get_config_dir()
            assert config_dir == test_config_dir
            assert config_dir.exists()  # Should be created

    def test_config_dir_uses_storage_dir_setting(self):
        """Test that get_config_dir uses cli.storage_dir setting."""
        test_storage_dir = self.test_temp_dir / "storage_config"

        with patch.dict(os.environ, {}, clear=True):
            with patch("src.skogcli.settings.get_setting") as mock_get_setting:
                mock_get_setting.return_value = str(test_storage_dir)

                config_dir = get_config_dir()
                assert config_dir == test_storage_dir
                assert config_dir.exists()  # Should be created

    def test_load_settings_requires_default_settings_file(self):
        """Test that load_settings throws error if default_settings.json is missing."""
        # Remove the default settings file
        self.test_default_settings_file.unlink()

        # Mock the default_settings module to point to our missing file
        with patch(
            "src.skogcli.default_settings.get_default_settings_file",
            return_value=self.test_default_settings_file,
        ):
            with pytest.raises(FileNotFoundError):
                load_settings()

    def test_environment_variables_override_file_settings(self):
        """Test that environment variables override file-based settings."""
        # Set environment variable for memory page_size
        with patch.dict(os.environ, {"SKOGAI_MEMORY_PAGE_SIZE": "25"}):
            with patch(
                "src.skogcli.default_settings.get_default_settings_file",
                return_value=self.test_default_settings_file,
            ):
                # The environment variable should override the file setting (10)
                page_size = get_setting("memory.page_size")
                assert page_size == 25

    def test_environment_variables_ui_theme_override(self):
        """Test that UI theme can be overridden by environment variable."""
        with patch.dict(os.environ, {"SKOGAI_UI_THEME": "dark"}):
            with patch(
                "src.skogcli.default_settings.get_default_settings_file",
                return_value=self.test_default_settings_file,
            ):
                theme = get_setting("ui.theme")
                assert theme == "dark"

    def test_no_config_directory_created_in_home(self):
        """Test that no .config directory is created in user's home."""
        # Mock Path.home() to return our test directory
        fake_home = self.test_temp_dir / "fake_home"
        fake_home.mkdir()

        with patch("pathlib.Path.home", return_value=fake_home):
            with patch.dict(os.environ, {}, clear=True):
                with patch(
                    "src.skogcli.settings.get_setting",
                    return_value=str(self.test_temp_dir / "custom"),
                ):
                    # Call get_config_dir which should not create .config in home
                    get_config_dir()

                    # Verify .config directory was NOT created in fake home
                    config_in_home = fake_home / ".config"
                    assert not config_in_home.exists()

    def test_setting_operations_work_without_dotconfig(self):
        """Test that set_setting and get_setting work without .config dependency."""
        test_config_dir = self.test_temp_dir / "test_config"

        with patch.dict(os.environ, {"SKOGAI_CONFIG_DIR": str(test_config_dir)}):
            with patch(
                "src.skogcli.default_settings.get_default_settings_file",
                return_value=self.test_default_settings_file,
            ):
                # Set a value
                success = set_setting("ui.theme", "custom")
                assert success is True

                # Get the value back
                theme = get_setting("ui.theme")
                assert theme == "custom"

                # Verify no .config directory was involved
                assert not any(".config" in str(p) for p in test_config_dir.rglob("*"))
