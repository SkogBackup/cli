"""Default settings for SkogCLI.

This module provides utilities for loading default settings from the JSON file.
The single source of truth for defaults is src/skogcli/data/default_settings.json.
"""

import json
from pathlib import Path
from typing import Any, Dict

# Configuration version - increment when making breaking changes
CONFIG_VERSION = 1


def get_default_settings_file() -> Path:
    """Get the path to the default settings file."""
    return Path(__file__).parent / "data" / "default_settings.json"


def ensure_data_dir() -> None:
    """Ensure the data directory exists."""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)


def load_default_settings() -> Dict[str, Any]:
    """Load default settings from JSON file.

    Returns:
        Dict containing the default settings from default_settings.json

    Raises:
        FileNotFoundError: If the default settings file doesn't exist
        ValueError: If the JSON file is invalid or empty
    """
    default_file = get_default_settings_file()

    if not default_file.exists():
        raise FileNotFoundError(
            f"Default settings file not found: {default_file}. "
            "The default_settings.json file is required for configuration."
        )

    try:
        with open(default_file, "r") as f:
            settings = json.load(f)

        if not settings:
            raise ValueError(f"Default settings file is empty: {default_file}")

        return settings
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in default settings file {default_file}: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load default settings file {default_file}: {e}")


def save_default_settings(settings: dict[str, Any]) -> bool:
    """Save default settings to file.

    Args:
        settings: Settings dictionary to save as defaults

    Returns:
        bool: True if successful, False otherwise
    """
    ensure_data_dir()
    default_file = get_default_settings_file()

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
