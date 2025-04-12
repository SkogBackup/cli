import pytest
from skogcli.settings import (
    DEFAULT_SETTINGS,
    load_settings,
    save_settings,
    get_setting,
    set_setting,
    reset_settings,
)
import tempfile
import os
from pathlib import Path
import json

@pytest.fixture
def temp_settings_dir():
    """Create a temporary directory for settings and set environment variable."""
    with tempfile.TemporaryDirectory() as temp_dir:
        old_xdg_config = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = temp_dir
        yield Path(temp_dir)
        # Restore original environment
        if old_xdg_config:
            os.environ["XDG_CONFIG_HOME"] = old_xdg_config
        else:
            os.environ.pop("XDG_CONFIG_HOME", None)

def test_load_default_settings(temp_settings_dir):
    """Test that default settings are loaded when no file exists."""
    settings = load_settings()
    assert settings == DEFAULT_SETTINGS
    
def test_save_and_load_settings(temp_settings_dir):
    """Test saving and loading settings."""
    test_settings = DEFAULT_SETTINGS.copy()
    test_settings["api_url"] = "https://test.example.com"
    test_settings["timeout"] = 60
    
    # Save settings
    result = save_settings(test_settings)
    assert result is True
    
    # Load settings
    loaded_settings = load_settings()
    assert loaded_settings == test_settings
    
def test_get_setting(temp_settings_dir):
    """Test getting a specific setting."""
    # Default setting
    assert get_setting("api_url") == DEFAULT_SETTINGS["api_url"]
    
    # Changed setting
    set_setting("api_url", "https://new.example.com")
    assert get_setting("api_url") == "https://new.example.com"
    
def test_set_setting(temp_settings_dir):
    """Test setting a specific setting."""
    # Set string
    assert set_setting("api_url", "https://changed.example.com") is True
    assert get_setting("api_url") == "https://changed.example.com"
    
    # Set int as string (should be converted)
    assert set_setting("timeout", "120") is True
    assert get_setting("timeout") == 120
    assert isinstance(get_setting("timeout"), int)
    
    # Set bool as string (should be converted)
    assert set_setting("debug", "true") is True
    assert get_setting("debug") is True
    
def test_reset_settings(temp_settings_dir):
    """Test resetting settings to defaults."""
    # Change settings
    set_setting("api_url", "https://changed.example.com")
    set_setting("timeout", 120)
    
    # Reset
    assert reset_settings() is True
    
    # Check settings are reset
    settings = load_settings()
    assert settings == DEFAULT_SETTINGS