"""Default settings for SkogCLI.

This module contains the default settings that are used when initializing
a new configuration or when resetting to defaults.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

# Configuration version - increment when making breaking changes
CONFIG_VERSION = 1

DEFAULT_SETTINGS = {
    "settings": {
        "cli": {
            "last-updated": "1970-01-01T00:00:00Z",
            "version": "0",
        },
        "memory": {"page_size": 10, "default_project": "default"},
        "ui": {"theme": "light"},
    }
}


def get_default_settings_file() -> Path:
    """Get the path to the default settings file."""
    return Path(__file__).parent / "data" / "default_settings.json"


def ensure_data_dir() -> None:
    """Ensure the data directory exists."""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)


def load_default_settings() -> Dict[str, Any]:
    """Load default settings from file or return the built-in defaults."""
    default_file = get_default_settings_file()

    if default_file.exists():
        try:
            with open(default_file, "r") as f:
                settings = json.load(f)

            # Ensure all required sections exist by merging with built-in defaults
            result = DEFAULT_SETTINGS.copy()

            # Deep merge the loaded settings with built-in defaults
            def deep_merge(source, destination):
                for key, value in source.items():
                    if (
                        isinstance(value, dict)
                        and key in destination
                        and isinstance(destination[key], dict)
                    ):
                        deep_merge(value, destination[key])
                    else:
                        destination[key] = value
                return destination

            deep_merge(settings, result)
            return result
        except Exception:
            # If there's any error loading the file, fall back to built-in defaults
            return DEFAULT_SETTINGS.copy()
    else:
        return DEFAULT_SETTINGS.copy()


def save_default_settings(settings: Dict[str, Any]) -> bool:
    """Save default settings to file.

    Returns:
        bool: True if successful, False otherwise
    """
    ensure_data_dir()
    default_file = get_default_settings_file()

    # Update metadata
    settings["settings"]["cli"] = {"version": CONFIG_VERSION}
    settings["settings"]["cli"]["last-updated"] = time.time()

    try:
        with open(default_file, "w") as f:
            # Create a copy without sensitive data for the defaults file
            main_settings = settings.copy()
            if "credentials" in main_settings:
                main_settings["credentials"] = {}  # Empty the credentials section
            json.dump(main_settings, f, indent=2)
        return True
    except Exception:
        return False
