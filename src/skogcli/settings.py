import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_SETTINGS = {
    "api_url": "https://api.example.com",
    "timeout": 30,
    "debug": False,
    "theme": "dark",
    "output_format": "text"
}

# Path for settings file
def get_settings_dir() -> Path:
    """Get the directory for settings file."""
    # Use XDG_CONFIG_HOME if available, otherwise ~/.config
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        base_dir = Path(config_home)
    else:
        base_dir = Path.home() / ".config"
    
    # Ensure the directory exists
    settings_dir = base_dir / "skogcli"
    settings_dir.mkdir(parents=True, exist_ok=True)
    
    return settings_dir

def get_settings_path() -> Path:
    """Get the full path to the settings file."""
    return get_settings_dir() / "config.json"  # Using config.json as per context.md

def load_settings() -> Dict[str, Any]:
    """Load settings from file or return defaults if file doesn't exist."""
    settings_path = get_settings_path()
    
    # If file doesn't exist, return defaults
    if not settings_path.exists():
        logger.info("Settings file not found, using defaults")
        return DEFAULT_SETTINGS.copy()
    
    # Read and parse the file
    try:
        with open(settings_path, "r") as f:
            settings = json.load(f)
            logger.debug("Settings loaded successfully")
            return settings
    except json.JSONDecodeError:
        logger.error("Invalid settings file format, using defaults")
        return DEFAULT_SETTINGS.copy()
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: Dict[str, Any]) -> bool:
    """Save settings to file."""
    settings_path = get_settings_path()
    
    try:
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
        logger.debug("Settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return False

def get_setting(key: str) -> Optional[Any]:
    """Get a specific setting value."""
    settings = load_settings()
    return settings.get(key)

def set_setting(key: str, value: Any) -> bool:
    """Set a specific setting value."""
    settings = load_settings()
    
    # Convert string representations to appropriate types if needed
    if key in DEFAULT_SETTINGS:
        default_type = type(DEFAULT_SETTINGS[key])
        if default_type == bool and isinstance(value, str):
            value = value.lower() in ("true", "yes", "1", "y")
        elif default_type == int and isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                logger.error(f"Invalid value for {key}: {value} (expected integer)")
                return False
    
    settings[key] = value
    return save_settings(settings)

def reset_settings() -> bool:
    """Reset all settings to defaults."""
    return save_settings(DEFAULT_SETTINGS.copy())

def list_settings() -> Dict[str, Any]:
    """Return all current settings."""
    return load_settings()