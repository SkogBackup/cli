---
title: SkogCLI Standards MCP Design
type: note
permalink: skog-ai/architecture/skog-cli-standards-mcp-design
---

# SkogCLI Standards MCP Design

This document outlines the design for a dedicated Standards MCP service to manage and enforce standards across SkogAI projects.

## Overview

The Standards MCP provides a centralized service for defining, accessing, and enforcing standards and conventions across the SkogAI ecosystem. It allows projects to:

1. **Query standards** to ensure compliance during development
2. **Validate implementations** against defined standards 
3. **Discover conventions** used in related projects
4. **Evolve standards** through a controlled process

## Core Features

### 1. Standards Registry

The Standards MCP maintains a registry of all standards organized by:

- **Category**: High-level grouping (e.g., code, configuration, documentation)
- **Scope**: Where the standard applies (e.g., global, project-specific)
- **Type**: The kind of standard (e.g., pattern, schema, format)

Each standard entry includes:
- **Name**: A unique identifier
- **Description**: Explanation of the standard
- **Definition**: The actual standard definition (pattern, schema, rules)
- **Examples**: Illustrative examples of compliance and non-compliance
- **Version**: Standard version with history
- **Metadata**: Tags, related standards, etc.

### 2. Standards Query API

The MCP provides an API for querying standards:

```python
# Get a specific standard
standard = standards_mcp.get_standard("config_paths")

# Query standards by category
code_standards = standards_mcp.query_standards(category="code")

# Check if a value complies with a standard
is_valid = standards_mcp.validate("config_paths", "memory.page_size")

# Get formatted examples of a standard
examples = standards_mcp.get_examples("config_paths", count=3)
```

### 3. Standards Enforcement

Standards can be actively enforced through:

- **Validation functions** that check if values comply with standards
- **Normalization functions** that convert values to standard-compliant formats
- **Helper utilities** that make it easier to follow standards

### 4. Standards Evolution

Standards can evolve through a controlled process:

- **Proposal** stage for suggesting new or updated standards
- **Review** stage for community feedback and refinement
- **Adoption** stage when a standard becomes official
- **Deprecation** when a standard is being phased out
- **Versioning** to track changes over time

## Implementation

### 1. Core Service

```python
class StandardsMCP:
    """Standards MCP service for managing project standards."""
    
    def __init__(self):
        """Initialize the standards registry."""
        self.registry = {}
        self.load_standards()
    
    def load_standards(self):
        """Load standards from the standards database."""
        # Load from database, file, or embedded definitions
        
    def get_standard(self, name: str) -> Dict:
        """Get a specific standard by name."""
        return self.registry.get(name)
    
    def query_standards(self, **filters) -> List[Dict]:
        """Query standards matching the given filters."""
        results = []
        for standard in self.registry.values():
            matches = True
            for key, value in filters.items():
                if standard.get(key) != value:
                    matches = False
                    break
            if matches:
                results.append(standard)
        return results
    
    def validate(self, standard_name: str, value: Any) -> bool:
        """Validate a value against a standard."""
        standard = self.get_standard(standard_name)
        if not standard:
            return False
            
        validator = self._get_validator(standard)
        return validator(value)
    
    def normalize(self, standard_name: str, value: Any) -> Any:
        """Normalize a value to comply with a standard."""
        standard = self.get_standard(standard_name)
        if not standard:
            return value
            
        normalizer = self._get_normalizer(standard)
        return normalizer(value)
    
    def get_examples(self, standard_name: str, count: int = 3) -> List[Dict]:
        """Get examples for a standard."""
        standard = self.get_standard(standard_name)
        if not standard or "examples" not in standard:
            return []
            
        examples = standard["examples"]
        return examples[:count] if count else examples
    
    def _get_validator(self, standard: Dict):
        """Get validation function for a standard."""
        # Return appropriate validator based on standard type
        
    def _get_normalizer(self, standard: Dict):
        """Get normalization function for a standard."""
        # Return appropriate normalizer based on standard type
```

### 2. Standards Definition Format

Standards are defined in a structured format:

```python
config_paths_standard = {
    "name": "config_paths",
    "category": "configuration",
    "scope": "global",
    "type": "pattern",
    "description": "Standard for configuration path formats",
    "definition": {
        "patterns": [
            r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$",  # Dot notation
            r"^[a-z][a-z0-9_]*://[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$",  # URI notation
            r"^[a-z][a-z0-9_]*(-[a-z][a-z0-9_]*)+$",  # Dash notation
            r"^[a-z][a-z0-9_]*(_[a-z][a-z0-9_]*)+$",  # Underscore notation
        ],
        "normalize": {
            "function": "normalize_config_path",
            "internal_format": "dot"
        }
    },
    "examples": [
        {
            "value": "memory.page_size",
            "format": "dot",
            "compliant": True,
            "description": "Dot notation example"
        },
        {
            "value": "memory://page_size",
            "format": "uri",
            "compliant": True,
            "description": "URI notation example"
        },
        {
            "value": "memory-page-size",
            "format": "dash",
            "compliant": True,
            "description": "Dash notation example"
        },
        {
            "value": "memory_page_size",
            "format": "underscore",
            "compliant": True,
            "description": "Underscore notation example"
        },
        {
            "value": "Memory.PageSize",
            "compliant": False,
            "description": "Non-compliant: incorrect casing"
        }
    ],
    "version": "1.0.0",
    "metadata": {
        "tags": ["configuration", "paths", "notation"],
        "related": ["file_paths", "resource_uris"]
    }
}
```

### 3. Client Interface

Projects use a client to interact with the Standards MCP:

```python
from standards_mcp import StandardsClient

# Create a client
standards = StandardsClient()

# Check if a configuration path is valid
if standards.validate("config_paths", user_input):
    # Process the input
    pass
else:
    # Display error message
    print("Invalid configuration path format")

# Normalize a path to the standard format
normalized = standards.normalize("config_paths", user_input)

# Get examples to show the user
examples = standards.get_examples("config_paths")
print("Example formats:", [ex["value"] for ex in examples if ex["compliant"]])
```

### 4. Standards CLI Integration

Command-line tools can use standards for validation and documentation:

```python
@config_app.command("get")
def get(
    key: str = typer.Argument(..., 
                           help="Configuration key in any format"),
    format_type: str = typer.Option("dot", "--format", "-f", 
                               help="Output format")
):
    """Get a configuration value."""
    # Validate the key format
    if not standards.validate("config_paths", key):
        # Get examples to show the user
        examples = standards.get_examples("config_paths")
        example_str = ", ".join([ex["value"] for ex in examples if ex["compliant"]][:3])
        
        typer.echo(f"Invalid key format. Examples: {example_str}")
        raise typer.Exit(code=1)
    
    # Normalize the key to dot notation internally
    normalized = standards.normalize("config_paths", key)
    
    # Get the value
    value = get_setting(normalized)
    
    # Format the key for display
    display_key = standards.format("config_paths", normalized, format_type)
    
    typer.echo(f"{display_key} = {value}")
```

## Using the Standards MCP with Config Paths

The Standards MCP would provide a clean, systematic way to handle config paths:

1. **Definition**: The `config_paths` standard defines the acceptable formats
2. **Validation**: Functions to check if a path conforms to any of the formats
3. **Normalization**: Convert any format to the canonical internal format (dot notation)
4. **Formatting**: Convert the internal format to any of the display formats
5. **Discovery**: Documentation and examples accessible programmatically

For example, the configuration module would use it like this:

```python
# In settings.py

from standards_mcp import StandardsClient

standards = StandardsClient()

def get_setting(path: str, default: Any = None) -> Any:
    """Get a setting value by its path in any supported format."""
    # Validate the path
    if not standards.validate("config_paths", path):
        raise ValueError(f"Invalid configuration path: {path}")
    
    # Normalize to internal format
    internal_path = standards.normalize("config_paths", path)
    
    # Split the normalized path
    parts = internal_path.split(".")
    
    # Get the value from the configuration
    # ... existing implementation ...
```

### Integration with Current Code

For a transitional approach, the Standards MCP could initially be implemented as a local utility in the `settings.py` file:

```python
class ConfigPathStandard:
    """Local implementation of the config_paths standard."""
    
    @staticmethod
    def validate(path: str) -> bool:
        """Check if a path conforms to any of the standard formats."""
        # Implement validation logic
        
    @staticmethod
    def normalize(path: str) -> str:
        """Normalize a path to the canonical format (dot notation)."""
        # Use the normalize_path function from our implementation
        parts = normalize_path(path)
        return ".".join(parts)
    
    @staticmethod
    def format(path: str, format_type: str) -> str:
        """Format a path to the specified format."""
        # Use the format_path function from our implementation
        parts = normalize_path(path)
        return format_path(parts, format_type)
```

## Benefits of the Standards MCP Approach

1. **Centralized Standards**: Single source of truth for all standards
2. **Programmatic Access**: Standards can be queried and used by code
3. **Validation and Normalization**: Standardized API for checking and converting values
4. **Documentation as Code**: Examples and explanations accessible to both humans and code
5. **Evolution Mechanism**: Structured process for updating standards
6. **Cross-Project Consistency**: Common standards can be shared across projects

The Standards MCP would be a powerful tool for maintaining consistency across the SkogAI ecosystem, making it easier for developers to follow best practices and for code to maintain standards over time.