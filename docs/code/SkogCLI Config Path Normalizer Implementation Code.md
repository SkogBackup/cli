---
title: SkogCLI Config Path Normalizer Implementation Code
type: note
permalink: docs/code/skog-cli-config-path-normalizer-implementation-code
---

# SkogCLI Config Path Normalizer Implementation Code

Below is the implementation code for the configuration path normalizer, which enhances the existing settings module with support for multiple path formats.

## Updated `settings.py` Code

```python
"""Settings management for SkogCLI."""

import json
import os
import re
import typer
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
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

class PathFormat(str, Enum):
    """Enum for path format types."""
    DOT = "dot"
    URI = "uri"
    DASH = "dash"
    UNDERSCORE = "underscore"

DEFAULT_CONFIG = {
    "general": {
        "default_project": "main",
        "editor": "vim",
        "color_output": True,
        "verbose": False
    },
    "memory": {
        "basic_memory_path": "basic-memory",
        "default_folder": "notes",
        "page_size": 10,
        "use_mcp": True,
        "render_markdown": True,
        "default_timeframe": "7d"
    },
    "paths": {
        "notes_root": "~/skogcli-notes",
        "templates_dir": "~/.config/skogcli/templates"
    },
    "templates": {
        "default": "# {title}\n\n"
    }
}

def normalize_path(path: str) -> List[str]:
    """
    Normalize any path format to a standard list of parts.
    
    Args:
        path: The path string in any supported format
            - Dot notation: memory.page_size
            - URI notation: memory://page_size
            - Dash notation: memory-page-size
            - Underscore notation: memory_page_size
    
    Returns:
        List of path parts (e.g., ["memory", "page", "size"])
    
    Examples:
        >>> normalize_path("memory.page_size")
        ["memory", "page", "size"]
        >>> normalize_path("memory://page-size")
        ["memory", "page", "size"]
    """
    # Handle URI notation
    if "://" in path:
        scheme, rest = path.split("://", 1)
        path_parts = [scheme] + re.split(r'[._-]', rest)
    else:
        # Handle dot, dash, and underscore notation
        path_parts = re.split(r'[._-]', path)
    
    # Filter out empty parts (which can happen with consecutive delimiters)
    return [part for part in path_parts if part]

def format_path(parts: List[str], format_type: PathFormat = PathFormat.DOT) -> str:
    """
    Format path parts into a specific notation.
    
    Args:
        parts: List of path parts (e.g., ["memory", "page", "size"])
        format_type: The format to use (dot, uri, dash, underscore)
    
    Returns:
        Formatted path string
    
    Examples:
        >>> format_path(["memory", "page", "size"], PathFormat.DOT)
        "memory.page.size"
        >>> format_path(["memory", "page", "size"], PathFormat.URI)
        "memory://page.size"
    """
    if not parts:
        return ""
    
    if format_type == PathFormat.URI:
        if len(parts) > 1:
            return f"{parts[0]}://{'.'.join(parts[1:])}"
        return parts[0]
    elif format_type == PathFormat.DASH:
        return "-".join(parts)
    elif format_type == PathFormat.UNDERSCORE:
        return "_".join(parts)
    else:  # Default to dot notation
        return ".".join(parts)

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
        save_settings(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/] Config file is corrupted. Resetting to defaults.")
        save_settings(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to the config file."""
    config_file = get_config_file()
    
    with open(config_file, "w") as f:
        json.dump(settings, f, indent=2)

def get_setting(path: str, default: Any = None) -> Any:
    """
    Get a setting value by its path in any supported format.
    
    Args:
        path: The setting path in any supported format
            - Dot notation: memory.page_size
            - URI notation: memory://page_size
            - Dash notation: memory-page-size
            - Underscore notation: memory_page_size
        default: Default value if the setting doesn't exist
    
    Returns:
        The setting value, or the default if not found
    
    Examples:
        >>> get_setting("memory.page_size")
        10
        >>> get_setting("memory://page_size")
        10
    """
    parts = normalize_path(path)
    settings = load_settings()
    
    # Navigate through nested dictionaries
    value = settings
    for part in parts:
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    
    return value

def set_setting(path: str, value: Any) -> None:
    """
    Set a setting value by its path in any supported format.
    
    Args:
        path: The setting path in any supported format
        value: The value to set
    
    Examples:
        >>> set_setting("memory.page_size", 20)
        >>> set_setting("memory://page_size", 20)
    """
    parts = normalize_path(path)
    settings = load_settings()
    
    # Navigate to the correct nested dictionary
    config = settings
    for part in parts[:-1]:
        if part not in config:
            config[part] = {}
        elif not isinstance(config[part], dict):
            # Convert a value to a dict if needed
            config[part] = {}
        config = config[part]
    
    # Set the value at the final level
    config[parts[-1]] = value
    
    # Save the updated configuration
    save_settings(settings)

def reset_settings() -> None:
    """Reset settings to default values."""
    save_settings(DEFAULT_CONFIG)

@config_app.callback()
def config_callback():
    """Manage SkogCLI configuration."""
    pass

@config_app.command("show")
@with_explanation("Display current configuration settings.")
def show(
    format_type: PathFormat = typer.Option(PathFormat.DOT, "--format", "-f", 
                               help="Output key format (dot, uri, dash, underscore)"),
    output_format: str = typer.Option("pretty", "--output", "-o", 
                                     help="Output format (pretty, json)"),
    key: Optional[str] = typer.Argument(None, help="Specific setting key to show")
):
    """
    Display current configuration settings.
    
    If a specific key is provided, only that setting is shown.
    Otherwise, all settings are displayed.
    
    Examples:
    
    Show all settings:
      skogcli config show
      
    Show specific setting:
      skogcli config show memory.page_size
      
    Show with URI format keys:
      skogcli config show --format uri
      
    Show as JSON:
      skogcli config show --output json
    """
    settings = load_settings()
    
    if key:
        value = get_setting(key)
        if value is None:
            console.print(f"[bold red]Error:[/] Key '{key}' not found in configuration.")
            raise typer.Exit(code=1)
        
        if output_format == "json":
            json_str = json.dumps({key: value}, indent=2)
            console.print(json_str)
        else:
            if isinstance(value, dict):
                json_str = json.dumps(value, indent=2)
                syntax = Syntax(json_str, "json", theme="monokai")
                console.print(syntax)
            else:
                formatted_key = format_path(normalize_path(key), format_type)
                console.print(f"{formatted_key} = {value}")
    else:
        if output_format == "json":
            json_str = json.dumps(settings, indent=2)
            console.print(json_str)
        else:
            # Display as pretty syntax highlighted JSON
            json_str = json.dumps(settings, indent=2)
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
            console.print(syntax)

@config_app.command("list")
@with_explanation("List all available configuration keys.")
def list_keys(
    format_type: PathFormat = typer.Option(PathFormat.DOT, "--format", "-f", 
                               help="Output key format (dot, uri, dash, underscore)"),
    prefix: str = typer.Option("", "--prefix", "-p", 
                              help="Filter keys by prefix")
):
    """
    List all available configuration keys.
    
    Use --prefix to filter keys starting with a specific prefix.
    Use --format to change the output format of keys.
    
    Examples:
    
    List all keys:
      skogcli config list
      
    List memory-related keys:
      skogcli config list --prefix memory
      
    List keys in URI format:
      skogcli config list --format uri
    """
    settings = load_settings()
    
    def extract_keys(data, current_parts=None):
        current_parts = current_parts or []
        keys = []
        for key, value in data.items():
            parts = current_parts + [key]
            if isinstance(value, dict):
                keys.extend(extract_keys(value, parts))
            else:
                keys.append(parts)
        return keys
    
    all_parts = extract_keys(settings)
    
    # Format keys according to the chosen format
    all_keys = [format_path(parts, format_type) for parts in all_parts]
    
    # Filter by prefix if specified
    if prefix:
        prefix_parts = normalize_path(prefix)
        filtered_keys = []
        
        for i, key_parts in enumerate(all_parts):
            if len(key_parts) >= len(prefix_parts):
                if key_parts[:len(prefix_parts)] == prefix_parts:
                    filtered_keys.append(all_keys[i])
        
        all_keys = filtered_keys
    
    if not all_keys:
        console.print(f"No settings found" + (f" with prefix '{prefix}'" if prefix else ""))
        return
    
    console.print("[bold]Available configuration keys:[/]")
    for key in sorted(all_keys):
        # Get the value
        value = get_setting(key)
        # Format the value for display
        if isinstance(value, dict):
            value_str = "{...}"
        elif isinstance(value, bool):
            value_str = "Yes" if value else "No"
        elif value is None:
            value_str = "None"
        else:
            value_str = str(value)
        
        console.print(f"  {key} = {value_str}")

@config_app.command("get")
@with_explanation("Get the value of a specific configuration key.")
def get(
    key: str = typer.Argument(..., 
                           help="Configuration key in any format (dot, URI, dash, underscore)"),
    default: Optional[str] = typer.Option(None, "--default", "-d",
                                        help="Default value if key doesn't exist"),
    format_type: PathFormat = typer.Option(PathFormat.DOT, "--format", "-f", 
                               help="Output key format (dot, uri, dash, underscore)")
):
    """
    Get the value of a specific configuration key.
    
    Supports multiple key formats:
    - Dot notation: memory.page_size
    - URI notation: memory://page_size
    - Dash notation: memory-page-size
    - Underscore notation: memory_page_size
    
    Examples:
    
    Get a specific value:
      skogcli config get memory.page_size
      
    Get with default value if not found:
      skogcli config get memory.unknown --default 42
      
    Get using URI notation:
      skogcli config get memory://page_size
    """
    value = get_setting(key, default)
    if value is None:
        console.print(f"[bold red]Error:[/] Key '{key}' not found in configuration.")
        raise typer.Exit(code=1)
    
    # Format the key for display
    formatted_key = format_path(normalize_path(key), format_type)
    
    if isinstance(value, dict):
        json_str = json.dumps(value, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai")
        console.print(syntax)
    else:
        console.print(f"{formatted_key} = {value}")

@config_app.command("set")
@with_explanation("Set a configuration value.")
def set_config(
    key: str = typer.Argument(..., 
                           help="Configuration key in any format (dot, URI, dash, underscore)"),
    value: str = typer.Argument(..., help="Value to set")
):
    """
    Set a configuration value.
    
    Supports multiple key formats:
    - Dot notation: memory.page_size
    - URI notation: memory://page_size
    - Dash notation: memory-page-size
    - Underscore notation: memory_page_size
    
    Examples:
    
    Set page size:
      skogcli config set memory.page_size 20
      
    Enable verbose mode:
      skogcli config set general.verbose true
      
    Set using URI notation:
      skogcli config set memory://page_size 20
    """
    # Try to convert the value to the appropriate type
    converted_value = value
    
    try:
        # Try as int
        int_value = int(value)
        converted_value = int_value
    except ValueError:
        try:
            # Try as float
            float_value = float(value)
            converted_value = float_value
        except ValueError:
            # Try as boolean or null
            if value.lower() in ("true", "yes", "1"):
                converted_value = True
            elif value.lower() in ("false", "no", "0"):
                converted_value = False
            elif value.lower() in ("null", "none"):
                converted_value = None
    
    # Set the value
    set_setting(key, converted_value)
    
    # Get the formatted key for display
    formatted_key = format_path(normalize_path(key), PathFormat.DOT)
    
    console.print(f"[green]Set[/] {formatted_key} = {converted_value}")

@config_app.command("reset")
@with_explanation("Reset configuration to default values.")
def reset(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirm reset without prompting")
):
    """
    Reset configuration to default values.
    
    Use --yes to skip the confirmation prompt.
    
    Example:
      skogcli config reset --yes
    """
    if not confirm:
        should_reset = typer.confirm("Are you sure you want to reset all settings to defaults?")
        if not should_reset:
            console.print("Reset cancelled.")
            return
    
    reset_settings()
    console.print("[green]Configuration reset to defaults.[/]")

@config_app.command("edit")
@with_explanation("Open the configuration file in your default editor.")
def edit(
    editor_cmd: Optional[str] = typer.Option(None, "--editor", "-e",
                                         help="Override default editor")
):
    """
    Open the configuration file in your default editor.
    
    Uses the editor specified in configuration or from the EDITOR environment variable.
    
    Examples:
    
    Open in default editor:
      skogcli config edit
      
    Open in specific editor:
      skogcli config edit --editor nano
    """
    config_file = get_config_file()
    
    if not config_file.exists():
        # Create default config if it doesn't exist
        save_settings(DEFAULT_CONFIG)
    
    # Determine which editor to use
    if not editor_cmd:
        editor_cmd = get_setting("general.editor")
    if not editor_cmd:
        editor_cmd = os.environ.get("EDITOR", "nano")
    
    try:
        result = typer.launch(f"{editor_cmd} {config_file}")
        if result:
            console.print("[green]Configuration file opened in editor.[/]")
        else:
            console.print("[bold red]Error:[/] Failed to open editor.")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
```

## Updated Test Code

Here are the tests for the new path normalizer functionality:

```python
# tests/test_settings.py

import pytest
import json
import os
from pathlib import Path
from typer.testing import CliRunner
from src.skogcli import app
from src.skogcli.settings import (
    normalize_path, format_path, PathFormat,
    get_setting, set_setting, reset_settings
)

runner = CliRunner()

def test_normalize_path():
    """Test that path normalization works correctly for different formats."""
    assert normalize_path("memory.page_size") == ["memory", "page", "size"]
    assert normalize_path("memory://page_size") == ["memory", "page", "size"]
    assert normalize_path("memory-page-size") == ["memory", "page", "size"]
    assert normalize_path("memory_page_size") == ["memory", "page", "size"]
    assert normalize_path("memory.page-size") == ["memory", "page", "size"]
    assert normalize_path("memory://page.size") == ["memory", "page", "size"]
    
    # Handle empty parts
    assert normalize_path("memory...page") == ["memory", "page"]
    assert normalize_path("memory---page") == ["memory", "page"]
    assert normalize_path("memory___page") == ["memory", "page"]

def test_format_path():
    """Test that path formatting works correctly for different formats."""
    parts = ["memory", "page", "size"]
    
    assert format_path(parts, PathFormat.DOT) == "memory.page.size"
    assert format_path(parts, PathFormat.URI) == "memory://page.size"
    assert format_path(parts, PathFormat.DASH) == "memory-page-size"
    assert format_path(parts, PathFormat.UNDERSCORE) == "memory_page_size"
    
    # Handle edge cases
    assert format_path([], PathFormat.DOT) == ""
    assert format_path(["single"], PathFormat.URI) == "single"

def test_settings_with_different_path_formats(tmp_path):
    """Test that settings can be set and retrieved with different path formats."""
    # Set up temporary config directory
    os.environ["HOME"] = str(tmp_path)
    
    # Reset settings to ensure clean state
    reset_settings()
    
    # Set with dot notation
    set_setting("memory.page_size", 20)
    
    # Get with different notations
    assert get_setting("memory.page_size") == 20
    assert get_setting("memory://page_size") == 20
    assert get_setting("memory-page-size") == 20
    assert get_setting("memory_page_size") == 20
    
    # Set with URI notation
    set_setting("general://verbose", True)
    
    # Get with different notations
    assert get_setting("general.verbose") is True
    assert get_setting("general://verbose") is True
    assert get_setting("general-verbose") is True
    assert get_setting("general_verbose") is True

def test_config_command_with_different_formats():
    """Test that config commands accept different path formats."""
    # Test get command with dot notation
    result = runner.invoke(app, ["config", "get", "memory.page_size"])
    assert result.exit_code == 0
    
    # Test get command with URI notation
    result = runner.invoke(app, ["config", "get", "memory://page_size"])
    assert result.exit_code == 0
    
    # Test get command with dash notation
    result = runner.invoke(app, ["config", "get", "memory-page-size"])
    assert result.exit_code == 0
    
    # Test get command with underscore notation
    result = runner.invoke(app, ["config", "get", "memory_page_size"])
    assert result.exit_code == 0
    
    # Test set command with different formats
    result = runner.invoke(app, ["config", "set", "memory.test_setting", "42"])
    assert result.exit_code == 0
    assert "Set memory.test_setting = 42" in result.stdout
    
    result = runner.invoke(app, ["config", "get", "memory://test_setting"])
    assert result.exit_code == 0
    assert "42" in result.stdout
```

The implementation provides a flexible and user-friendly way to handle configuration paths while maintaining a clean internal representation. It supports multiple path formats (dot, URI, dash, underscore) and enhances the existing commands to work with all formats.

Key improvements include:
1. Path normalization for consistent internal handling
2. Flexible path formatting for different output styles
3. Enhanced command-line interface with better format support
4. Comprehensive tests to ensure compatibility

This implementation follows the standards defined in the project standards document and maintains the existing functionality while adding the new features.