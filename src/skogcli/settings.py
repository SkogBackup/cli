"""Settings management for SkogCLI."""

import json
import os
import typer
from pathlib import Path
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.syntax import Syntax
from rich import print as rprint
from .decorators import with_explanation

console = Console()

# Create a Typer app for the config commands
config_app = typer.Typer(
    help="Manage SkogCLI configuration",
    no_args_is_help=True
)

DEFAULT_SETTINGS = {
    "memory": {
        "default_project": None,
        "page_size": 10,
    },
    "ui": {
        "theme": "default",
        "verbose": False,
    }
}

def get_config_dir() -> Path:
    """Get the configuration directory, creating it if it doesn't exist."""
    config_dir = Path.home() / ".config" / "skogcli"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_config_file() -> Path:
    """Get the path to the configuration file."""
    return get_config_dir() / "config.json"

def load_settings() -> Dict[str, Any]:
    """Load settings from the config file, or create default settings if the file doesn't exist."""
    config_file = get_config_file()
    
    if not config_file.exists():
        # Create default config
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/] Config file is corrupted. Resetting to defaults.")
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

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

def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to the config file."""
    config_file = get_config_file()
    
    with open(config_file, "w") as f:
        json.dump(settings, f, indent=2)

def get_setting(key: str) -> Any:
    """Get a setting value by its key (supports dot notation for nested settings)."""
    settings = load_settings()
    
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

def set_setting(key: str, value: Any) -> None:
    """Set a setting value by its key (supports dot notation for nested settings)."""
    settings = load_settings()
    
    if "." in key:
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
    
    save_settings(settings)

def reset_settings() -> None:
    """Reset settings to default values."""
    save_settings(DEFAULT_SETTINGS)

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
        autocompletion=lambda: get_config_keys()
    )
):
    """Get the value of a specific configuration key."""
    value = get_setting(key)
    if value is None:
        console.print(f"[bold red]Error:[/] Key '{key}' not found in configuration.")
        return
    
    if isinstance(value, dict):
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
        autocompletion=lambda: get_config_keys()
    ),
    value: str = typer.Argument(..., help="Value to set")
):
    """Set the value of a specific configuration key."""
    # Try to convert the value to the appropriate type
    try:
        # Try as int
        int_value = int(value)
        set_setting(key, int_value)
        console.print(f"[green]Set[/] {key} = {int_value}")
        return 0  # Ensure the command returns 0
    except ValueError:
        pass
    
    try:
        # Try as float
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
    console.print(f"[green]Set[/] {key} = \"{value}\"")
    return 0  # Ensure the command returns 0

@config_app.command("reset")
@with_explanation("Reset configuration to default values.")
def reset(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirm reset without prompting")
):
    """Reset configuration to default values."""
    if not confirm:
        should_reset = typer.confirm("Are you sure you want to reset all settings to defaults?")
        if not should_reset:
            console.print("Reset cancelled.")
            return 1  # Ensure the command returns 1 if reset is cancelled
    
    reset_settings()
    console.print("[green]Configuration reset to defaults.[/]")
    return 0  # Ensure the command returns 0

@config_app.command("edit")
@with_explanation("Open the configuration file in your default editor.")
def edit():
    """Open the configuration file in your default editor."""
    config_file = get_config_file()
    
    if not config_file.exists():
        # Create default config if it doesn't exist
        save_settings(DEFAULT_SETTINGS)
    
    # Use the EDITOR environment variable, or fall back to common editors
    editor = os.environ.get("EDITOR", "nano")
    
    try:
        # Use os.system to properly invoke the editor with the file path
        exit_code = os.system(f"{editor} {config_file}")
        if exit_code == 0:
            console.print("[green]Configuration file edited successfully.[/]")
        else:
            console.print(f"[bold red]Error:[/] Editor exited with code {exit_code}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
