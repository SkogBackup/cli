---
title: SkogCLI Config Module Implementation
type: note
permalink: projects/skogcli/skog-cli-config-module-implementation
---

# SkogCLI Config Module Implementation

This document outlines the implementation plan for the configuration management module in SkogCLI.

## Overview

The config module provides a comprehensive system for managing application settings through a JSON-based configuration file stored in the user's home directory. It offers CLI commands for viewing, modifying, and resetting configuration values.

## Configuration Structure

```json
{
  "general": {
    "default_project": "main",
    "editor": "vim",
    "color_output": true,
    "verbose": false
  },
  "memory": {
    "basic_memory_path": "basic-memory",
    "default_folder": "notes",
    "page_size": 10,
    "use_mcp": true,
    "render_markdown": true,
    "default_timeframe": "7d"
  },
  "paths": {
    "notes_root": "~/skogcli-notes",
    "templates_dir": "~/.config/skogcli/templates"
  },
  "templates": {
    "default": "# {title}\n\n",
    "meeting": "# {title}\n\nDate: {date}\n\n## Attendees\n\n## Agenda\n\n## Notes\n\n## Action Items\n\n"
  }
}
```

## Implementation Details

### Settings Module

```python
# src/skogcli/settings.py
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
import typer

class Settings:
    """Manages SkogCLI configuration settings."""
    
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
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize settings with optional custom config directory."""
        if config_dir:
            self.config_dir = Path(config_dir).expanduser().resolve()
        else:
            self.config_dir = Path.home() / ".config" / "skogcli"
            
        self.config_file = self.config_dir / "config.json"
        self.config = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from config file or create with defaults if not exists."""
        if not self.config_file.exists():
            # Create directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save default settings
            return self.save_settings(self.DEFAULT_CONFIG)
        
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            typer.echo(f"Error: Config file corrupt. Resetting to defaults.")
            return self.save_settings(self.DEFAULT_CONFIG)
    
    def save_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Save settings to config file."""
        with open(self.config_file, "w") as f:
            json.dump(settings, f, indent=2)
        return settings
    
    def get_setting(self, path: str, default: Any = None) -> Any:
        """Get a setting value using dot notation path (e.g., 'memory.page_size')."""
        parts = path.split(".")
        value = self.config
        
        for part in parts:
            if part not in value:
                return default
            value = value[part]
            
        return value
    
    def set_setting(self, path: str, value: Any) -> None:
        """Set a setting value using dot notation path."""
        parts = path.split(".")
        config = self.config
        
        # Navigate to the correct nested dictionary
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        # Set the value
        config[parts[-1]] = value
        
        # Save the updated configuration
        self.save_settings(self.config)
    
    def reset_settings(self) -> None:
        """Reset all settings to defaults."""
        self.config = self.save_settings(self.DEFAULT_CONFIG)
    
    def list_keys(self, prefix: str = "") -> list[str]:
        """List all available settings keys with optional prefix filter."""
        keys = []
        
        def _collect_keys(d, current_prefix=""):
            for k, v in d.items():
                key = f"{current_prefix}.{k}" if current_prefix else k
                if isinstance(v, dict):
                    _collect_keys(v, key)
                else:
                    keys.append(key)
        
        _collect_keys(self.config)
        
        if prefix:
            return [k for k in keys if k.startswith(prefix)]
        return keys

# Create a singleton instance for global access
settings = Settings()
```

### Config CLI Module

```python
# src/skogcli/config.py
import typer
import json
import os
import subprocess
from typing import Optional
from rich.console import Console
from rich.table import Table
from .settings import settings
from .decorators import with_explanation

config_app = typer.Typer(
    help="Manage SkogCLI configuration",
    no_args_is_help=True
)

console = Console()

@config_app.callback()
def config_callback():
    """Manage SkogCLI configuration."""
    pass

@config_app.command("show")
@with_explanation("Display current configuration settings.")
def show(
    format: str = typer.Option("pretty", "--format", "-f", 
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
      
    Show as JSON:
      skogcli config show --format json
    """
    if key:
        value = settings.get_setting(key)
        if value is None:
            typer.echo(f"Setting '{key}' not found")
            raise typer.Exit(code=1)
        
        if format == "json":
            typer.echo(json.dumps({key: value}, indent=2))
        else:
            typer.echo(f"{key}: {value}")
    else:
        if format == "json":
            typer.echo(json.dumps(settings.config, indent=2))
        else:
            # Create a rich table for pretty display
            table = Table(title="SkogCLI Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")
            
            for full_key in settings.list_keys():
                value = settings.get_setting(full_key)
                # Convert boolean values to yes/no for better readability
                if isinstance(value, bool):
                    value = "Yes" if value else "No"
                table.add_row(full_key, str(value))
                
            console.print(table)

@config_app.command("set")
@with_explanation("Set a configuration value.")
def set_config(
    key: str = typer.Argument(..., help="Setting key (e.g., 'memory.page_size')"),
    value: str = typer.Argument(..., help="Value to set")
):
    """
    Set a configuration value.
    
    Examples:
    
    Set page size:
      skogcli config set memory.page_size 20
      
    Enable verbose mode:
      skogcli config set general.verbose true
    """
    # Convert string values to appropriate types
    if value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
    elif value.isdigit():
        value = int(value)
    
    try:
        settings.set_setting(key, value)
        typer.echo(f"✓ Setting '{key}' updated to '{value}'")
    except Exception as e:
        typer.echo(f"Error setting '{key}': {str(e)}")
        raise typer.Exit(code=1)

@config_app.command("reset")
@with_explanation("Reset configuration to default values.")
def reset(
    confirm: bool = typer.Option(False, "--yes", "-y", 
                                help="Skip confirmation prompt")
):
    """
    Reset configuration to default values.
    
    Use --yes to skip the confirmation prompt.
    
    Example:
      skogcli config reset --yes
    """
    if not confirm:
        confirm = typer.confirm("Are you sure you want to reset all settings to defaults?")
        
    if confirm:
        settings.reset_settings()
        typer.echo("✓ Configuration reset to defaults")
    else:
        typer.echo("Reset cancelled")

@config_app.command("list-keys")
@with_explanation("List all available configuration keys.")
def list_keys(
    prefix: str = typer.Option("", "--prefix", "-p", 
                              help="Filter keys by prefix")
):
    """
    List all available configuration keys.
    
    Use --prefix to filter keys starting with a specific prefix.
    
    Examples:
    
    List all keys:
      skogcli config list-keys
      
    List memory-related keys:
      skogcli config list-keys --prefix memory
    """
    keys = settings.list_keys(prefix)
    
    if not keys:
        typer.echo(f"No settings found" + (f" with prefix '{prefix}'" if prefix else ""))
        return
    
    # Create a rich table for pretty display
    table = Table(title="Available Configuration Keys")
    table.add_column("Key", style="cyan")
    
    for key in sorted(keys):
        table.add_row(key)
        
    console.print(table)

@config_app.command("get")
@with_explanation("Get a single configuration value (for scripts).")
def get(
    key: str = typer.Argument(..., help="Setting key to retrieve"),
    default: Optional[str] = typer.Option(None, "--default", "-d",
                                        help="Default value if key doesn't exist")
):
    """
    Get a single configuration value.
    
    This command is useful for scripts as it outputs just the raw value.
    
    Examples:
    
    Get a specific value:
      skogcli config get memory.page_size
      
    Get with default value if not found:
      skogcli config get custom.setting --default "fallback"
    """
    value = settings.get_setting(key, default)
    if value is None:
        typer.echo(f"Setting '{key}' not found")
        raise typer.Exit(code=1)
    
    # Output as string for consistency
    typer.echo(str(value))

@config_app.command("edit")
@with_explanation("Open configuration file in editor.")
def edit(
    editor: Optional[str] = typer.Option(None, "--editor", "-e",
                                       help="Override default editor")
):
    """
    Open configuration file in your editor.
    
    Uses the editor specified in configuration or from the EDITOR environment variable.
    
    Examples:
    
    Open in default editor:
      skogcli config edit
      
    Open in specific editor:
      skogcli config edit --editor nano
    """
    # Determine which editor to use
    editor_cmd = editor
    if not editor_cmd:
        editor_cmd = settings.get_setting("general.editor")
    if not editor_cmd:
        editor_cmd = os.environ.get("EDITOR", "vim")
    
    try:
        # Open the config file in the editor
        subprocess.run([editor_cmd, settings.config_file], check=True)
        typer.echo(f"Configuration file edited: {settings.config_file}")
        
        # Reload settings after edit
        settings.config = settings.load_settings()
    except subprocess.SubprocessError as e:
        typer.echo(f"Error opening editor: {str(e)}")
        raise typer.Exit(code=1)
```

### Integration with Main App

```python
# In src/skogcli/__init__.py
from .config import config_app

# Add the config app as a subcommand
app.add_typer(config_app, name="config")
```

## User Experience

### Viewing Configuration

```bash
# Show all settings in pretty format
skogcli config show

# Show specific setting
skogcli config show memory.page_size

# Output in JSON format
skogcli config show --format json
```

### Modifying Configuration

```bash
# Set page size for pagination
skogcli config set memory.page_size 20

# Enable/disable features
skogcli config set memory.render_markdown true

# Set string values
skogcli config set general.editor "vim"
```

### Resetting Configuration

```bash
# Reset with confirmation prompt
skogcli config reset

# Reset without confirmation
skogcli config reset --yes
```

### Discovering Available Settings

```bash
# List all available configuration keys
skogcli config list-keys

# List only memory-related keys
skogcli config list-keys --prefix memory
```

### For Scripting

```bash
# Get a specific value (outputs raw value without formatting)
skogcli config get memory.page_size

# Get with default value if not found
skogcli config get custom.setting --default "fallback"
```

### Editing Configuration

```bash
# Open in default editor
skogcli config edit

# Open in specific editor
skogcli config edit --editor nano
```

## Error Handling

The implementation includes proper error handling:

1. Validates configuration file integrity
2. Provides clear error messages
3. Uses appropriate exit codes for scripts
4. Safeguards against invalid modifications
5. Includes confirmation for destructive actions

## Advantages of This Approach

1. **Simplicity**: Single JSON file is easy to understand and edit
2. **Flexibility**: Nested structure allows for logical grouping of related settings
3. **Extensibility**: New sections can be added without breaking existing configuration
4. **User-friendly**: Rich tables for pretty display of configuration
5. **Script-friendly**: Commands designed for both human and programmatic use
6. **Discoverability**: Commands to list and explore available settings

## Future Enhancements

1. **Schema Validation**: Add JSON schema validation for configuration files
2. **Environment Variable Override**: Support for overriding settings with environment variables
3. **Project-specific Configuration**: Add support for project-level configuration overrides
4. **Configuration Profiles**: Support for switching between different configuration profiles
5. **Import/Export**: Commands for importing/exporting configuration between environments