---
title: SkogCLI Config Path Normalizer Implementation
type: note
permalink: docs/implementations/skog-cli-config-path-normalizer-implementation
---

# SkogCLI Config Path Normalizer Implementation

This document outlines the implementation plan for the configuration path normalizer in SkogCLI's settings module.

## Overview

The path normalizer provides a system for handling multiple path formats in configuration keys:
- Dot notation: `memory.page_size`
- URI notation: `memory://page_size`
- Dash notation: `memory-page-size`
- Underscore notation: `memory_page_size`

## Implementation

### 1. Add Required Imports

```python
import re
from enum import Enum
from typing import List, Any, Dict, Optional, Union
```

### 2. Define Path Format Types

```python
class PathFormat(str, Enum):
    """Enum for path format types."""
    DOT = "dot"
    URI = "uri"
    DASH = "dash"
    UNDERSCORE = "underscore"
```

### 3. Implement Path Normalization

```python
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
```

### 4. Implement Path Formatting

```python
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
```

### 5. Enhance the Settings Class

```python
class Settings:
    # ... existing code ...
    
    def get_setting(self, path: str, default: Any = None) -> Any:
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
        
        # Navigate through nested dictionaries
        value = self.config
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
        
        return value
    
    def set_setting(self, path: str, value: Any) -> None:
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
        
        # Navigate to the correct nested dictionary
        config = self.config
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
        self.save_settings(self.config)
```

### 6. Update CLI Command Help Text

```python
@config_app.command("get")
@with_explanation("Get the value of a specific configuration key.")
def get(key: str = typer.Argument(..., help="Configuration key in any format (dot, URI, dash, underscore)")):
    """
    Get the value of a specific configuration key.
    
    Supports multiple key formats:
    - Dot notation: memory.page_size
    - URI notation: memory://page_size
    - Dash notation: memory-page-size
    - Underscore notation: memory_page_size
    """
    # Implementation using the enhanced get_setting
```

## Testing Plan

### 1. Unit Tests for Path Normalization

```python
def test_normalize_path():
    """Test that path normalization works correctly for different formats."""
    assert normalize_path("memory.page_size") == ["memory", "page", "size"]
    assert normalize_path("memory://page_size") == ["memory", "page", "size"]
    assert normalize_path("memory-page-size") == ["memory", "page", "size"]
    assert normalize_path("memory_page_size") == ["memory", "page", "size"]
    assert normalize_path("memory.page-size") == ["memory", "page", "size"]
    assert normalize_path("memory://page.size") == ["memory", "page", "size"]
```

### 2. Unit Tests for Path Formatting

```python
def test_format_path():
    """Test that path formatting works correctly for different formats."""
    parts = ["memory", "page", "size"]
    
    assert format_path(parts, PathFormat.DOT) == "memory.page.size"
    assert format_path(parts, PathFormat.URI) == "memory://page.size"
    assert format_path(parts, PathFormat.DASH) == "memory-page-size"
    assert format_path(parts, PathFormat.UNDERSCORE) == "memory_page_size"
```

### 3. Integration Tests for Settings

```python
def test_settings_with_different_path_formats(temp_config):
    """Test that settings can be set and retrieved with different path formats."""
    # Set with dot notation
    settings.set_setting("memory.page_size", 20)
    
    # Get with different notations
    assert settings.get_setting("memory.page_size") == 20
    assert settings.get_setting("memory://page_size") == 20
    assert settings.get_setting("memory-page-size") == 20
    assert settings.get_setting("memory_page_size") == 20
```

## Integration with CLI Commands

All config commands should support multiple path formats:

```python
# Example command handler
@config_app.command("set")
@with_explanation("Set a configuration value.")
def set_config(
    key: str = typer.Argument(..., 
                            help="Setting key in any format (e.g., 'memory.page_size', 'memory://page_size')"),
    value: str = typer.Argument(..., help="Value to set")
):
    """
    Set a configuration value.
    
    Examples:
    
    Set page size:
      skogcli config set memory.page_size 20
      skogcli config set memory://page_size 20
    """
    # Implementation with type conversion and error handling
```

## Conclusion

This implementation enables a flexible configuration system that supports multiple path formats while maintaining clean internal representation. The normalized path approach makes the code more maintainable while providing a very user-friendly interface for configuration management.