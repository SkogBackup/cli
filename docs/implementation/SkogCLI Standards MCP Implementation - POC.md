---
title: SkogCLI Standards MCP Implementation - POC
type: note
permalink: docs/implementation/skog-cli-standards-mcp-implementation-poc
---

# SkogCLI Standards MCP Implementation - Proof of Concept

This document provides a practical implementation of the Standards MCP concept that can be used immediately for handling configuration paths.

## Local Standards Module

While we work toward a full MCP implementation, we can create a local standards module that serves a similar purpose:

```python
# src/skogcli/standards.py

import re
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable, Pattern

class PathFormat(str, Enum):
    """Enum for path format types."""
    DOT = "dot"
    URI = "uri"
    DASH = "dash"
    UNDERSCORE = "underscore"

class Standard:
    """Base class for standards."""
    
    def __init__(self, name: str, description: str):
        """Initialize a standard."""
        self.name = name
        self.description = description
    
    def validate(self, value: Any) -> bool:
        """Validate a value against this standard."""
        raise NotImplementedError("Subclasses must implement validate")
    
    def normalize(self, value: Any) -> Any:
        """Normalize a value to comply with this standard."""
        raise NotImplementedError("Subclasses must implement normalize")
    
    def format(self, value: Any, format_type: Any) -> Any:
        """Format a value in a specific format."""
        raise NotImplementedError("Subclasses must implement format")
    
    def get_examples(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get examples for this standard."""
        examples = getattr(self, "examples", [])
        return examples[:count] if count else examples


class PatternStandard(Standard):
    """Standard based on regex patterns."""
    
    def __init__(self, name: str, description: str, patterns: List[str],
                 normalize_func: Callable[[str], Any] = None,
                 format_func: Callable[[Any, Any], str] = None,
                 examples: List[Dict[str, Any]] = None):
        """Initialize a pattern standard."""
        super().__init__(name, description)
        self.patterns = [re.compile(pattern) for pattern in patterns]
        self.normalize_func = normalize_func
        self.format_func = format_func
        self.examples = examples or []
    
    def validate(self, value: str) -> bool:
        """Check if value matches any of the patterns."""
        for pattern in self.patterns:
            if pattern.match(value):
                return True
        return False
    
    def normalize(self, value: str) -> Any:
        """Normalize a value using the normalize function."""
        if self.normalize_func:
            return self.normalize_func(value)
        return value
    
    def format(self, value: Any, format_type: Any) -> str:
        """Format a value using the format function."""
        if self.format_func:
            return self.format_func(value, format_type)
        return str(value)


class StandardsRegistry:
    """Registry for standards."""
    
    def __init__(self):
        """Initialize the registry."""
        self.standards = {}
    
    def register(self, standard: Standard):
        """Register a standard."""
        self.standards[standard.name] = standard
    
    def get(self, name: str) -> Optional[Standard]:
        """Get a standard by name."""
        return self.standards.get(name)
    
    def validate(self, name: str, value: Any) -> bool:
        """Validate a value against a standard."""
        standard = self.get(name)
        if not standard:
            raise ValueError(f"Unknown standard: {name}")
        return standard.validate(value)
    
    def normalize(self, name: str, value: Any) -> Any:
        """Normalize a value to comply with a standard."""
        standard = self.get(name)
        if not standard:
            raise ValueError(f"Unknown standard: {name}")
        return standard.normalize(value)
    
    def format(self, name: str, value: Any, format_type: Any) -> Any:
        """Format a value in a specific format."""
        standard = self.get(name)
        if not standard:
            raise ValueError(f"Unknown standard: {name}")
        return standard.format(value, format_type)
    
    def get_examples(self, name: str, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get examples for a standard."""
        standard = self.get(name)
        if not standard:
            raise ValueError(f"Unknown standard: {name}")
        return standard.get_examples(count)


# Create the registry
standards = StandardsRegistry()

# Define standards

# 1. Configuration Path Standard
def normalize_config_path(path: str) -> List[str]:
    """
    Normalize a configuration path to path parts.
    
    Examples:
        >>> normalize_config_path("memory.page_size")
        ["memory", "page", "size"]
        >>> normalize_config_path("memory://page-size")
        ["memory", "page", "size"]
    """
    # Handle URI notation
    if "://" in path:
        scheme, rest = path.split("://", 1)
        path_parts = [scheme] + re.split(r'[._-]', rest)
    else:
        # Handle dot, dash, and underscore notation
        path_parts = re.split(r'[._-]', path)
    
    # Filter out empty parts
    return [part for part in path_parts if part]

def format_config_path(parts: List[str], format_type: PathFormat = PathFormat.DOT) -> str:
    """
    Format path parts into a specific notation.
    
    Examples:
        >>> format_config_path(["memory", "page", "size"], PathFormat.DOT)
        "memory.page.size"
        >>> format_config_path(["memory", "page", "size"], PathFormat.URI)
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

# Register the config_paths standard
config_paths_standard = PatternStandard(
    name="config_paths",
    description="Standard for configuration path formats",
    patterns=[
        r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$",  # Dot notation
        r"^[a-z][a-z0-9_]*://[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$",  # URI notation
        r"^[a-z][a-z0-9_]*(-[a-z][a-z0-9_]*)+$",  # Dash notation
        r"^[a-z][a-z0-9_]*(_[a-z][a-z0-9_]*)+$",  # Underscore notation
    ],
    normalize_func=normalize_config_path,
    format_func=format_config_path,
    examples=[
        {
            "value": "memory.page_size",
            "format": PathFormat.DOT,
            "compliant": True,
            "description": "Dot notation example"
        },
        {
            "value": "memory://page_size",
            "format": PathFormat.URI,
            "compliant": True,
            "description": "URI notation example"
        },
        {
            "value": "memory-page-size",
            "format": PathFormat.DASH,
            "compliant": True,
            "description": "Dash notation example"
        },
        {
            "value": "memory_page_size",
            "format": PathFormat.UNDERSCORE,
            "compliant": True,
            "description": "Underscore notation example"
        },
        {
            "value": "Memory.PageSize",
            "compliant": False,
            "description": "Non-compliant: incorrect casing"
        }
    ]
)

standards.register(config_paths_standard)
```

## Integration with Settings Module

Now we can update the settings module to use the standards module:

```python
# src/skogcli/settings.py

import json
import os
import typer
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from rich.console import Console
from rich.syntax import Syntax
from rich import print as rprint
from .decorators import with_explanation
from .standards import standards, PathFormat

console = Console()

# Create a Typer app for the config commands
config_app = typer.Typer(
    help="Manage SkogCLI configuration",
    no_args_is_help=True
)

# ... [keep existing code] ...

def get_setting(path: str, default: Any = None) -> Any:
    """
    Get a setting value by its path in any supported format.
    
    Args:
        path: The setting path in any supported format
        default: Default value if the setting doesn't exist
    
    Returns:
        The setting value, or the default if not found
    
    Examples:
        >>> get_setting("memory.page_size")
        10
        >>> get_setting("memory://page_size")
        10
    """
    try:
        # Validate the path format
        if not standards.validate("config_paths", path):
            # Provide helpful error message with examples
            examples = standards.get_examples("config_paths")
            valid_examples = [ex["value"] for ex in examples if ex.get("compliant", False)]
            example_str = ", ".join(valid_examples[:3])
            raise ValueError(f"Invalid configuration path format. Examples: {example_str}")
        
        # Normalize to path parts
        parts = standards.normalize("config_paths", path)
        
        # Get the config
        settings = load_settings()
        
        # Navigate through nested dictionaries
        value = settings
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
        
        return value
    except ValueError as e:
        # Log the error but return default value rather than crashing
        console.print(f"[bold red]Error:[/] {str(e)}")
        return default

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
    # Validate the path format
    if not standards.validate("config_paths", path):
        # Provide helpful error message with examples
        examples = standards.get_examples("config_paths")
        valid_examples = [ex["value"] for ex in examples if ex.get("compliant", False)]
        example_str = ", ".join(valid_examples[:3])
        raise ValueError(f"Invalid configuration path format. Examples: {example_str}")
    
    # Normalize to path parts
    parts = standards.normalize("config_paths", path)
    
    # Get the config
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

# ... [Update CLI commands to use standards] ...

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
    """
    settings_data = load_settings()
    
    if key:
        try:
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
                    # Format the key using the standard
                    parts = standards.normalize("config_paths", key)
                    formatted_key = standards.format("config_paths", parts, format_type)
                    console.print(f"{formatted_key} = {value}")
        except ValueError as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
            raise typer.Exit(code=1)
    else:
        if output_format == "json":
            json_str = json.dumps(settings_data, indent=2)
            console.print(json_str)
        else:
            # Display as pretty syntax highlighted JSON
            json_str = json.dumps(settings_data, indent=2)
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
            console.print(syntax)

# ... [Other updated commands] ...
```

## Advantages of this Approach

1. **Structured Standards System**: 
   - Provides a clear, structured way to define and use standards
   - Standards are objects with well-defined interfaces
   - Registry enables dynamic lookup and management

2. **Separation of Concerns**:
   - Standards definitions are separate from their usage
   - Each standard has its own validation, normalization, and formatting logic
   - Easy to add new standards without changing usage code

3. **Rich Standard Definitions**:
   - Includes examples for documentation and error messages
   - Has both human-readable description and machine-readable rules
   - Supports multiple validation patterns per standard

4. **Future Compatibility**:
   - Local implementation can be easily migrated to an MCP service later
   - Standard interface makes switching implementations transparent to code
   - Maintains the core concept of standards as a managed resource

5. **Practical Implementation**:
   - Can be used immediately in the settings module
   - No external dependencies beyond what's already in the project
   - Maintains backward compatibility with existing code

## Usage Examples

With this implementation, we can use the standards system in our code:

```python
# Import the standards registry
from src.skogcli.standards import standards, PathFormat

# Validate a configuration path
try:
    if standards.validate("config_paths", user_input):
        print("Valid configuration path")
    else:
        print("Invalid configuration path")
except ValueError as e:
    print(f"Error: {str(e)}")

# Normalize a path to its parts
parts = standards.normalize("config_paths", "memory.page_size")
# Returns: ["memory", "page", "size"]

# Format a path in a specific format
uri_path = standards.format("config_paths", parts, PathFormat.URI)
# Returns: "memory://page.size"

# Get examples for a standard
examples = standards.get_examples("config_paths")
for ex in examples:
    if ex.get("compliant", False):
        print(f"Valid example: {ex['value']} ({ex['description']})")
    else:
        print(f"Invalid example: {ex['value']} ({ex['description']})")
```

This proof-of-concept implementation provides a solid foundation that can be evolved into a full MCP service in the future.