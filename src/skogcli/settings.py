"""Settings management for SkogCLI."""

import json
import os
import shutil
import time
import typer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from rich.console import Console
from rich.syntax import Syntax
from rich import print as rprint
from .decorators import with_explanation
from .default_settings import (
    load_default_settings,
    save_default_settings,
    get_default_settings_file,
    CONFIG_VERSION,
)

console = Console()

# Create a Typer app for the config commands
config_app = typer.Typer(help="Manage SkogCLI configuration", no_args_is_help=True)

# Ensure the data directory exists
from .default_settings import ensure_data_dir

ensure_data_dir()


def get_config_dir() -> Path:
    """Get the configuration directory, creating it if it doesn't exist."""
    # Check for SKOGAI config directory first
    skogai_config_dir = os.getenv("SKOGAI_CONFIG_DIR")
    if skogai_config_dir:
        config_dir = Path(skogai_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    # Check for XDG_CONFIG_HOME as a better fallback
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        config_dir = Path(xdg_config_home) / "skogcli"
    else:
        config_dir = Path.home() / ".config" / "skogcli"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_backup_dir() -> Path:
    """Get the backup directory for configuration files."""
    backup_dir = get_config_dir() / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_config_file() -> Path:
    """Get the path to the configuration file."""
    return get_config_dir() / "config.json"


def get_sensitive_config_file() -> Path:
    """Get the path to the sensitive configuration file."""
    return get_config_dir() / "credentials.json"


def create_backup(config_file: Path) -> Path:
    """Create a backup of the configuration file."""
    if not config_file.exists():
        return None

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = get_backup_dir() / f"{config_file.name}.{timestamp}.bak"

    try:
        shutil.copy2(config_file, backup_path)
        return backup_path
    except Exception as e:
        console.print(f"[bold yellow]Warning:[/] Failed to create backup: {str(e)}")
        return None


def migrate_config(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate configuration from older versions to the current version."""
    # Ensure settings structure exists
    if "settings" not in settings:
        settings["settings"] = {}
        
    if (
        "meta" not in settings["settings"]
        or "version" not in settings["settings"]["meta"]
    ):
        # This is an old config without versioning
        console.print("[yellow]Migrating configuration to the latest version...[/]")

        # Add metadata section with current version
        settings["settings"]["meta"] = {
            "version": CONFIG_VERSION,
            "last_updated": time.time(),
        }

        # Add new sections that didn't exist in older versions
        if "module" not in settings["settings"]:
            # Initialize empty module settings
            settings["settings"]["module"] = {
                "history": []
            }

        if "credentials" not in settings:
            settings["credentials"] = {}
    
    # Migrate chat history from old location to new location if needed
    if "chat" in settings and "history" in settings["chat"]:
        # Ensure module section exists
        if "module" not in settings["settings"]:
            settings["settings"]["module"] = {}
        
        # Ensure history section exists in module
        if "history" not in settings["settings"]["module"]:
            settings["settings"]["module"]["history"] = []
            
        # Copy history from old location to new location
        settings["settings"]["module"]["history"] = settings["chat"]["history"]

    # Handle future migrations based on version numbers
    version = settings["settings"]["meta"].get("version", 0)

    # Example of future migration:
    # if version < 2:
    #     # Migrate from version 1 to 2
    #     settings["new_section"] = {"new_key": "new_value"}
    #     settings["_meta"]["version"] = 2

    return settings


def load_settings() -> Dict[str, Any]:
    """Load settings from the config file, or create default settings if the file doesn't exist."""
    config_file = get_config_file()

    if not config_file.exists():
        # Create default config
        settings = load_default_settings()
        settings["settings"]["meta"] = {
            "last_updated": time.time(),
            "version": CONFIG_VERSION
        }
        save_settings(settings)
        return settings

    try:
        with open(config_file, "r") as f:
            settings = json.load(f)

        # Migrate configuration if needed
        settings = migrate_config(settings)

        # Ensure all required sections exist
        defaults = load_default_settings()
        for section, section_defaults in defaults.items():
            if section not in settings:
                settings[section] = section_defaults

        return settings
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/] Config file is corrupted.")

        # Try to restore from backup
        backup = restore_from_latest_backup()
        if backup:
            console.print(f"[green]Restored configuration from backup.[/]")
            return backup

        # If no backup, reset to defaults
        console.print("[yellow]Resetting to default configuration.[/]")
        settings = load_default_settings()
        settings["_meta"]["last_updated"] = time.time()
        save_settings(settings)
        return settings
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to load configuration: {str(e)}")
        return load_default_settings()


def load_sensitive_settings() -> Dict[str, Any]:
    """Load sensitive settings like API keys from a separate file."""
    sensitive_file = get_sensitive_config_file()

    if not sensitive_file.exists():
        return {}

    try:
        with open(sensitive_file, "r") as f:
            return json.load(f)
    except Exception:
        console.print(
            "[bold yellow]Warning:[/] Could not load sensitive configuration."
        )
        return {}


def restore_from_latest_backup() -> Optional[Dict[str, Any]]:
    """Attempt to restore configuration from the most recent backup."""
    backup_dir = get_backup_dir()
    if not backup_dir.exists():
        return None

    # Find the most recent backup file
    backup_files = list(backup_dir.glob("config.json.*.bak"))
    if not backup_files:
        return None

    # Sort by modification time (newest first)
    backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    # Try to load from the most recent backup
    try:
        with open(backup_files[0], "r") as f:
            return json.load(f)
    except Exception:
        return None


def get_config_keys() -> List[str]:
    """Get a list of all configuration keys for completion."""
    settings = load_settings()

    def extract_keys(data, prefix=""):
        keys = []
        for key, value in data.items():
            full_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, dict):
                keys.append(full_key)
                keys.extend(extract_keys(value, f"{full_key}."))
            else:
                keys.append(full_key)
        return keys

    return extract_keys(settings)


def save_settings(settings: Dict[str, Any]) -> bool:
    """Save settings to the config file.

    Returns:
        bool: True if successful, False otherwise
    """
    config_file = get_config_file()

    # Update metadata
    if "settings" not in settings:
        settings["settings"] = {}
    
    if "meta" not in settings["settings"]:
        settings["settings"]["meta"] = {"version": CONFIG_VERSION}

    settings["settings"]["meta"]["last_updated"] = time.time()

    # Create a backup before saving
    create_backup(config_file)

    # Extract sensitive data to save separately
    sensitive_data = settings.get("credentials", {})

    try:
        # Save main configuration
        with open(config_file, "w") as f:
            # Create a copy without sensitive data for the main config file
            main_settings = settings.copy()
            main_settings["credentials"] = {}  # Empty the credentials section
            json.dump(main_settings, f, indent=2)

        # Save sensitive data if there is any
        if sensitive_data:
            sensitive_file = get_sensitive_config_file()
            with open(sensitive_file, "w") as f:
                json.dump(sensitive_data, f, indent=2)

        return True
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to save configuration: {str(e)}")
        return False


def get_setting(key: str) -> Any:
    """Get a setting value by its key (supports dot notation for nested settings)."""
    settings = load_settings()

    # Handle credentials separately
    if key.startswith("credentials."):
        sensitive_settings = load_sensitive_settings()
        credential_key = key.split(".", 1)[1]
        return sensitive_settings.get(credential_key)

    if "." in key:
        # Handle nested keys
        parts = key.split(".")
        current = settings
        for part in parts:
            if part not in current:
                return None
            current = current[part]
        return current

    return settings.get(key)


def set_setting(key: str, value: Any) -> bool:
    """Set a setting value by its key (supports dot notation for nested settings).

    Returns:
        bool: True if successful, False otherwise
    """
    settings = load_settings()

    # Special handling for credentials
    is_credential = key.startswith("credentials.")

    if is_credential:
        # Load sensitive settings separately
        sensitive_settings = load_sensitive_settings()
        credential_key = key.split(".", 1)[1]
        sensitive_settings[credential_key] = value

        # Save to the sensitive file
        try:
            sensitive_file = get_sensitive_config_file()
            with open(sensitive_file, "w") as f:
                json.dump(sensitive_settings, f, indent=2)

            # Also update the main settings object for consistency
            if "credentials" not in settings:
                settings["credentials"] = {}
            settings["credentials"][credential_key] = value
        except Exception as e:
            console.print(f"[bold red]Error:[/] Failed to save credential: {str(e)}")
            return False
    elif "." in key:
        # Handle nested keys
        parts = key.split(".")
        current = settings
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set the value at the final level
        current[parts[-1]] = value
    else:
        settings[key] = value

    return save_settings(settings)


def reset_settings() -> bool:
    """Reset settings to default values.

    Returns:
        bool: True if successful, False otherwise
    """
    # Create a backup before resetting
    create_backup(get_config_file())
    create_backup(get_sensitive_config_file())

    # Reset to defaults
    settings = load_default_settings()
    if "settings" not in settings:
        settings["settings"] = {}
    if "meta" not in settings["settings"]:
        settings["settings"]["meta"] = {}
    settings["settings"]["meta"]["last_updated"] = time.time()
    return save_settings(settings)


def add_chat_history_item(item: Dict[str, Any]) -> bool:
    """Add an item to the chat history.

    Args:
        item: A dictionary containing chat history data

    Returns:
        bool: True if successful, False otherwise
    """
    settings = load_settings()

    # Ensure module section exists
    if "settings" not in settings:
        settings["settings"] = {}
    
    if "module" not in settings["settings"]:
        # Import default settings from the module
        from .default_settings import DEFAULT_SETTINGS

        settings["settings"]["module"] = DEFAULT_SETTINGS["settings"]["module"].copy()
    
    # Ensure history section exists
    if "history" not in settings["settings"]["module"]:
        settings["settings"]["module"]["history"] = []

    # Add timestamp if not present
    if "timestamp" not in item:
        item["timestamp"] = time.time()

    # Add to history
    settings["settings"]["module"]["history"].append(item)

    # Trim history if it exceeds the maximum
    max_items = settings["settings"]["module"].get("max_history_items", 100)
    if len(settings["settings"]["module"]["history"]) > max_items:
        settings["settings"]["module"]["history"] = settings["settings"]["module"]["history"][-max_items:]

    return save_settings(settings)


def get_chat_history(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get the chat history.

    Args:
        limit: Maximum number of items to return (most recent first)

    Returns:
        List of chat history items
    """
    settings = load_settings()

    if ("settings" not in settings or 
        "module" not in settings["settings"] or 
        "history" not in settings["settings"]["module"]):
        return []

    history = settings["settings"]["module"]["history"]

    # Sort by timestamp (newest first)
    history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    if limit is not None:
        return history[:limit]

    return history


def clear_chat_history() -> bool:
    """Clear the chat history.

    Returns:
        bool: True if successful, False otherwise
    """
    settings = load_settings()

    if "settings" in settings and "module" in settings["settings"]:
        # Create a backup before clearing
        create_backup(get_config_file())

        # Clear history
        settings["settings"]["module"]["history"] = []
        return save_settings(settings)

    return True


@config_app.callback()
def config_callback():
    """Manage SkogCLI configuration."""
    pass


@config_app.command("show")
@with_explanation("Display the current configuration.")
def show():
    """Display the current configuration."""
    settings = load_settings()
    json_str = json.dumps(settings, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(syntax)
    return 0  # Ensure the command returns 0


@config_app.command("list")
@with_explanation("List all available configuration keys.")
def list_keys():
    """List all available configuration keys."""
    settings = load_settings()

    def extract_keys(data, prefix=""):
        keys = []
        for key, value in data.items():
            full_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, dict):
                keys.extend(extract_keys(value, f"{full_key}."))
            else:
                keys.append(full_key)
        return keys

    all_keys = extract_keys(settings)

    console.print("[bold]Available configuration keys:[/]")
    for key in sorted(all_keys):
        console.print(f"  {key}")
    return 0  # Ensure the command returns 0


@config_app.command("get")
@with_explanation("Get the value of a specific configuration key.")
def get(
    key: str = typer.Argument(
        ...,
        help="Configuration key (e.g., 'memory.page_size')",
        autocompletion=lambda: get_config_keys(),
    ),
    raw: bool = typer.Option(
        False, "--raw", "-r", help="Output raw value without formatting"
    ),
    json_format: bool = typer.Option(
        False, "--json", "-j", help="Output as formatted JSON"
    ),
):
    """Get the value of a specific configuration key."""
    value = get_setting(key)
    if value is None:
        console.print(f"[bold red]Error:[/] Key '{key}' not found in configuration.")
        return

    # Check if this is a leaf node in a nested structure
    is_leaf_node = "." in key and not isinstance(value, dict)

    # Output as JSON when --json flag is used
    if json_format:
        print(json.dumps(value, indent=2))
        return

    # Output raw value for leaf nodes or when --raw flag is used
    if raw:
        print(value)
    elif isinstance(value, dict) or isinstance(value, list):
        json_str = json.dumps(value, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai")
        console.print(syntax)
    else:
        console.print(f"{key} = {value}")


@config_app.command("set")
@with_explanation("Set the value of a specific configuration key.")
def set(
    key: str = typer.Argument(
        ...,
        help="Configuration key (e.g., 'memory.page_size')",
        autocompletion=lambda: get_config_keys(),
    ),
    value: str = typer.Argument(..., help="Value to set"),
):
    """Set the value of a specific configuration key."""
    # Try to parse as JSON first (for objects, arrays, etc.)
    try:
        json_value = json.loads(value)
        set_setting(key, json_value)
        if isinstance(json_value, dict) or isinstance(json_value, list):
            json_str = json.dumps(json_value, indent=2)
            console.print(f"[green]Set[/] {key} = ")
            syntax = Syntax(json_str, "json", theme="monokai")
            console.print(syntax)
        else:
            console.print(f"[green]Set[/] {key} = {json_value}")
        return
    except json.JSONDecodeError:
        # Not valid JSON, continue with other type conversions
        pass

    # Try as int
    try:
        int_value = int(value)
        set_setting(key, int_value)
        console.print(f"[green]Set[/] {key} = {int_value}")
        return 0  # Ensure the command returns 0
    except ValueError:
        pass

    # Try as float
    try:
        float_value = float(value)
        set_setting(key, float_value)
        console.print(f"[green]Set[/] {key} = {float_value}")
        return 0  # Ensure the command returns 0
    except ValueError:
        pass

    # Try as boolean
    if value.lower() in ("true", "yes", "1"):
        set_setting(key, True)
        console.print(f"[green]Set[/] {key} = True")
        return 0  # Ensure the command returns 0
    elif value.lower() in ("false", "no", "0"):
        set_setting(key, False)
        console.print(f"[green]Set[/] {key} = False")
        return 0  # Ensure the command returns 0

    # Try as null/None
    if value.lower() in ("null", "none"):
        set_setting(key, None)
        console.print(f"[green]Set[/] {key} = None")
        return 0  # Ensure the command returns 0

    # Default to string
    set_setting(key, value)
    console.print(f'[green]Set[/] {key} = "{value}"')
    return 0  # Ensure the command returns 0


@config_app.command("reset")
@with_explanation("Reset configuration to default values.")
def reset(
    confirm: bool = typer.Option(
        False, "--yes", "-y", help="Confirm reset without prompting"
    ),
):
    """Reset configuration to default values."""
    if not confirm:
        should_reset = typer.confirm(
            "Are you sure you want to reset all settings to defaults?"
        )
        if not should_reset:
            console.print("Reset cancelled.")
            return 1  # Ensure the command returns 1 if reset is cancelled

    if reset_settings():
        console.print("[green]Configuration reset to defaults.[/]")
    else:
        console.print("[bold red]Error:[/] Failed to reset configuration.")


@config_app.command("show-defaults")
@with_explanation("Display the default configuration.")
def show_defaults():
    """Display the default configuration."""
    settings = load_default_settings()
    json_str = json.dumps(settings, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(syntax)
    return 0  # Ensure the command returns 0


@config_app.command("edit-defaults")
@with_explanation("Edit the default configuration.")
def edit_defaults(
    key: Optional[str] = typer.Argument(
        None,
        help="Configuration key to edit (if not specified, opens the entire file)",
        autocompletion=lambda: get_config_keys(),
    ),
    value: Optional[str] = typer.Argument(
        None, help="Value to set (if not specified with key, opens the file in editor)"
    ),
):
    """Edit the default configuration."""
    # If key and value are provided, set the specific value
    if key and value is not None:
        defaults = load_default_settings()

        # Try to parse as JSON first (for objects, arrays, etc.)
        try:
            json_value = json.loads(value)

            # Update the defaults
            if "." in key:
                # Handle nested keys
                parts = key.split(".")
                current = defaults
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Set the value at the final level
                current[parts[-1]] = json_value
            else:
                defaults[key] = json_value

            # Save the updated defaults
            if save_default_settings(defaults):
                if isinstance(json_value, dict) or isinstance(json_value, list):
                    json_str = json.dumps(json_value, indent=2)
                    console.print(f"[green]Set default[/] {key} = ")
                    syntax = Syntax(json_str, "json", theme="monokai")
                    console.print(syntax)
                else:
                    console.print(f"[green]Set default[/] {key} = {json_value}")
                return 0
            else:
                console.print("[bold red]Error:[/] Failed to save default settings.")
                return 1
        except json.JSONDecodeError:
            # Not valid JSON, continue with other type conversions
            pass

        # Try as int
        try:
            int_value = int(value)

            # Update the defaults
            if "." in key:
                # Handle nested keys
                parts = key.split(".")
                current = defaults
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Set the value at the final level
                current[parts[-1]] = int_value
            else:
                defaults[key] = int_value

            # Save the updated defaults
            if save_default_settings(defaults):
                console.print(f"[green]Set default[/] {key} = {int_value}")
                return 0
            else:
                console.print("[bold red]Error:[/] Failed to save default settings.")
                return 1
        except ValueError:
            pass

        # Try as float
        try:
            float_value = float(value)

            # Update the defaults
            if "." in key:
                # Handle nested keys
                parts = key.split(".")
                current = defaults
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Set the value at the final level
                current[parts[-1]] = float_value
            else:
                defaults[key] = float_value

            # Save the updated defaults
            if save_default_settings(defaults):
                console.print(f"[green]Set default[/] {key} = {float_value}")
                return 0
            else:
                console.print("[bold red]Error:[/] Failed to save default settings.")
                return 1
        except ValueError:
            pass

        # Try as boolean
        if value.lower() in ("true", "yes", "1"):
            # Update the defaults
            if "." in key:
                # Handle nested keys
                parts = key.split(".")
                current = defaults
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Set the value at the final level
                current[parts[-1]] = True
            else:
                defaults[key] = True

            # Save the updated defaults
            if save_default_settings(defaults):
                console.print(f"[green]Set default[/] {key} = True")
                return 0
            else:
                console.print("[bold red]Error:[/] Failed to save default settings.")
                return 1
        elif value.lower() in ("false", "no", "0"):
            # Update the defaults
            if "." in key:
                # Handle nested keys
                parts = key.split(".")
                current = defaults
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Set the value at the final level
                current[parts[-1]] = False
            else:
                defaults[key] = False

            # Save the updated defaults
            if save_default_settings(defaults):
                console.print(f"[green]Set default[/] {key} = False")
                return 0
            else:
                console.print("[bold red]Error:[/] Failed to save default settings.")
                return 1

        # Try as null/None
        if value.lower() in ("null", "none"):
            # Update the defaults
            if "." in key:
                # Handle nested keys
                parts = key.split(".")
                current = defaults
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Set the value at the final level
                current[parts[-1]] = None
            else:
                defaults[key] = None

            # Save the updated defaults
            if save_default_settings(defaults):
                console.print(f"[green]Set default[/] {key} = None")
                return 0
            else:
                console.print("[bold red]Error:[/] Failed to save default settings.")
                return 1

        # Default to string
        # Update the defaults
        if "." in key:
            # Handle nested keys
            parts = key.split(".")
            current = defaults
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set the value at the final level
            current[parts[-1]] = value
        else:
            defaults[key] = value

        # Save the updated defaults
        if save_default_settings(defaults):
            console.print(f'[green]Set default[/] {key} = "{value}"')
            return 0
        else:
            console.print("[bold red]Error:[/] Failed to save default settings.")
            return 1

    # If only key is provided, show the current value
    elif key:
        defaults = load_default_settings()

        # Handle nested keys
        if "." in key:
            parts = key.split(".")
            current = defaults
            for part in parts:
                if part not in current:
                    console.print(
                        f"[bold red]Error:[/] Key '{key}' not found in default configuration."
                    )
                    return 1
                current = current[part]
            value = current
        else:
            if key not in defaults:
                console.print(
                    f"[bold red]Error:[/] Key '{key}' not found in default configuration."
                )
                return 1
            value = defaults[key]

        # Display the value
        if isinstance(value, dict) or isinstance(value, list):
            json_str = json.dumps(value, indent=2)
            console.print(f"Default {key} = ")
            syntax = Syntax(json_str, "json", theme="monokai")
            console.print(syntax)
        else:
            console.print(f"Default {key} = {value}")

        return 0

    # If no key is provided, open the entire file in the editor
    else:
        default_file = get_default_settings_file()

        # Ensure the file exists
        if not default_file.exists():
            defaults = load_default_settings()
            save_default_settings(defaults)

        # Use the EDITOR environment variable, or fall back to common editors
        editor = os.environ.get("EDITOR", "nano")

        try:
            # Use os.system to properly invoke the editor with the file path
            exit_code = os.system(f"{editor} {default_file}")
            if exit_code == 0:
                console.print(
                    "[green]Default configuration file edited successfully.[/]"
                )

                # Validate the edited file
                try:
                    with open(default_file, "r") as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    console.print(
                        f"[bold red]Warning:[/] The edited file contains invalid JSON: {str(e)}"
                    )
                    console.print(
                        "You may want to fix this by running the edit command again."
                    )
            else:
                console.print(
                    f"[bold red]Error:[/] Editor exited with code {exit_code}"
                )
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")


@config_app.command("edit")
@with_explanation("Open the configuration file in your default editor.")
def edit(
    sensitive: bool = typer.Option(
        False, "--sensitive", "-s", help="Edit sensitive configuration"
    ),
):
    """Open the configuration file in your default editor."""
    config_file = get_sensitive_config_file() if sensitive else get_config_file()

    if not config_file.exists():
        # Create default config if it doesn't exist
        if sensitive:
            with open(config_file, "w") as f:
                json.dump({}, f, indent=2)
        else:
            # Load default settings
            settings = load_default_settings()
            settings["_meta"]["last_updated"] = time.time()
            save_settings(settings)

    # Create a backup before editing
    create_backup(config_file)

    # Use the EDITOR environment variable, or fall back to common editors
    editor = os.environ.get("EDITOR", "nano")

    try:
        # Use os.system to properly invoke the editor with the file path
        exit_code = os.system(f"{editor} {config_file}")
        if exit_code == 0:
            console.print("[green]Configuration file edited successfully.[/]")

            # Validate the edited file
            try:
                with open(config_file, "r") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                console.print(
                    f"[bold red]Warning:[/] The edited file contains invalid JSON: {str(e)}"
                )
                console.print(
                    "You may want to fix this by running the edit command again."
                )
        else:
            console.print(f"[bold red]Error:[/] Editor exited with code {exit_code}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")


@config_app.command("backup")
@with_explanation("Create a backup of the configuration files.")
def backup():
    """Create a backup of the configuration files."""
    config_file = get_config_file()
    sensitive_file = get_sensitive_config_file()

    backup_paths = []
    if config_file.exists():
        backup_path = create_backup(config_file)
        if backup_path:
            backup_paths.append(backup_path)

    if sensitive_file.exists():
        backup_path = create_backup(sensitive_file)
        if backup_path:
            backup_paths.append(backup_path)

    if backup_paths:
        console.print("[green]Backups created successfully:[/]")
        for path in backup_paths:
            console.print(f"  - {path}")
    else:
        console.print("[yellow]No configuration files to backup.[/]")


@config_app.command("restore")
@with_explanation("Restore configuration from a backup.")
def restore(
    backup_file: Optional[Path] = typer.Argument(
        None,
        help="Path to the backup file (if not specified, uses the most recent backup)",
    ),
    confirm: bool = typer.Option(
        False, "--yes", "-y", help="Confirm restore without prompting"
    ),
):
    """Restore configuration from a backup."""
    if backup_file is None:
        # Find the most recent backup
        backup_dir = get_backup_dir()
        if not backup_dir.exists():
            console.print("[bold red]Error:[/] No backups found.")
            return

        backup_files = list(backup_dir.glob("*.bak"))
        if not backup_files:
            console.print("[bold red]Error:[/] No backups found.")
            return

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        backup_file = backup_files[0]

    if not backup_file.exists():
        console.print(f"[bold red]Error:[/] Backup file not found: {backup_file}")
        return

    if not confirm:
        should_restore = typer.confirm(
            f"Are you sure you want to restore from {backup_file}?"
        )
        if not should_restore:
            console.print("Restore cancelled.")
            return

    try:
        # Determine target file based on backup filename
        if "credentials" in backup_file.name:
            target_file = get_sensitive_config_file()
        else:
            target_file = get_config_file()

        # Create a backup of the current file before restoring
        create_backup(target_file)

        # Copy the backup to the target file
        shutil.copy2(backup_file, target_file)
        console.print(f"[green]Configuration restored from {backup_file}[/]")

        # Validate the restored file
        try:
            with open(target_file, "r") as f:
                json.load(f)
        except json.JSONDecodeError:
            console.print(
                "[bold red]Warning:[/] The restored file contains invalid JSON."
            )
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to restore: {str(e)}")


@config_app.command("list-backups")
@with_explanation("List available configuration backups.")
def list_backups():
    """List available configuration backups."""
    backup_dir = get_backup_dir()
    if not backup_dir.exists():
        console.print("[yellow]No backups found.[/]")
        return

    backup_files = list(backup_dir.glob("*.bak"))
    if not backup_files:
        console.print("[yellow]No backups found.[/]")
        return

    # Sort by modification time (newest first)
    backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    console.print("[bold]Available backups:[/]")
    for i, backup in enumerate(backup_files):
        mtime = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(backup.stat().st_mtime)
        )
        size = backup.stat().st_size / 1024  # Size in KB
        console.print(f"{i + 1}. {backup.name} ({mtime}, {size:.1f} KB)")


@config_app.command("factory-reset")
@with_explanation(
    "Reset configuration to factory default values (ignoring custom defaults)."
)
def factory_reset(
    confirm: bool = typer.Option(
        False, "--yes", "-y", help="Confirm reset without prompting"
    ),
):
    """Reset configuration to factory default values."""
    if not confirm:
        should_reset = typer.confirm(
            "Are you sure you want to reset all settings to factory defaults?"
        )
        if not should_reset:
            console.print("Factory reset cancelled.")
            return 1

    # Create a backup before resetting
    create_backup(get_config_file())
    create_backup(get_sensitive_config_file())

    # Import the original defaults directly from the module
    from .default_settings import DEFAULT_SETTINGS

    # Reset to factory defaults
    settings = DEFAULT_SETTINGS.copy()
    if "settings" not in settings:
        settings["settings"] = {}
    if "meta" not in settings["settings"]:
        settings["settings"]["meta"] = {}
    settings["settings"]["meta"]["last_updated"] = time.time()

    if save_settings(settings):
        console.print("[green]Configuration reset to factory defaults.[/]")
    else:
        console.print("[bold red]Error:[/] Failed to reset configuration.")


@config_app.command("chat-history")
@with_explanation("Manage chat history.")
def chat_history(
    clear: bool = typer.Option(False, "--clear", help="Clear chat history"),
    limit: int = typer.Option(
        10, "--limit", "-n", help="Number of history items to show"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    ),
):
    """Manage chat history."""
    if clear:
        if typer.confirm("Are you sure you want to clear all chat history?"):
            if clear_chat_history():
                console.print("[green]Chat history cleared.[/]")
            else:
                console.print("[bold red]Error:[/] Failed to clear chat history.")
        return

    history = get_chat_history(limit)

    if not history:
        console.print("[yellow]No chat history found.[/]")
        return

    if json_output:
        print(json.dumps(history, indent=2))
        return

    console.print(
        f"[bold]Chat history (showing {len(history)} of {len(get_chat_history())} items):[/]"
    )
    for i, item in enumerate(history):
        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(item.get("timestamp", 0))
        )
        console.print(f"[bold]{i + 1}. {timestamp}[/]")

        if "session_id" in item:
            console.print(f"  Session: {item['session_id']}")

        if "message" in item:
            console.print(f"  Message: {item['message'][:50]}...")

        if "metadata" in item:
            console.print(f"  Metadata: {json.dumps(item['metadata'], indent=2)}")

        console.print("")
