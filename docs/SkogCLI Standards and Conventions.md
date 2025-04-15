---
title: SkogCLI Standards and Conventions
type: note
permalink: docs/skog-cli-standards-and-conventions
---

# SkogCLI Standards and Conventions

This document serves as the central reference for standards, conventions, and patterns used across the SkogCLI project.

## Naming Conventions

### File and Directory Naming
- Package names: lowercase, no underscores (e.g., `skogcli`)
- Module names: lowercase, underscores for readability (e.g., `config_utils.py`)
- Test files: prefix with `test_` (e.g., `test_memory.py`)
- Documentation files: Title case with hyphens (e.g., `SkogCLI-Standards.md`)

### Code Naming
- Functions/Methods: `snake_case` (e.g., `get_config_value`)
- Classes: `PascalCase` (e.g., `ConfigManager`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CONFIG`)
- Variables: `snake_case` (e.g., `page_size`)
- Type variables: `PascalCase` (e.g., `T`, `ConfigDict`)

## Path and Identifier Standards

### Configuration Paths
All these formats are equivalent and should be supported by the configuration system:

| Format      | Example               | Notes                              |
|-------------|----------------------|-----------------------------------|
| Dot notation| `memory.page_size`   | Default internal representation    |
| URI notation| `memory://page_size` | Compatible with resource addressing|
| Dash notation| `memory-page-size`  | Alternative for command line usage |
| Underscore  | `memory_page_size`   | Consistent with variable naming    |

The configuration system will normalize these paths internally while supporting all formats in the user interface.

### Resource URIs
URIs are used across SkogCLI for addressing resources:

| URI Scheme   | Format                          | Purpose                      |
|--------------|--------------------------------|------------------------------|
| `memory://`  | `memory://[entity]/[id]`       | Accessing memory entries     |
| `notes://`   | `notes://[folder]/[title]`     | Accessing notes              |
| `template://`| `template://[name]`            | Referencing templates        |
| `config://`  | `config://[section]/[key]`     | Referencing configuration    |

## Code Structure

### Module Organization
- `__init__.py`: Package exports and Typer app registration
- `settings.py`: Configuration loading and management
- `memory.py`: Memory module functionality
- `decorators.py`: Shared decorators and utilities

### Function Structure
- Place imports at the top of the file
- Group imports: standard library → third-party → local
- Use type hints consistently
- Include docstrings for all public functions/classes
- Follow the principle of least surprise

## CLI Command Structure

### Command Naming
- Use nouns for resource commands (e.g., `config`, `memory`)
- Use verbs for action commands (e.g., `show`, `set`, `list`)
- Be consistent with similar CLI tools

### Command Arguments
- Use positional arguments for required inputs
- Use options (--flags) for optional configurations
- Include detailed help text for all arguments/options
- Default to help when no args provided (`no_args_is_help=True`)

### Output Formatting
- Use Rich for consistent, attractive output
- Use tables for structured data
- Use color consistently: green for success, red for errors
- Provide both human-readable and machine-readable outputs

## Testing Standards

### Test Organization
- One test file per module 
- Group tests by functionality
- Name tests descriptively (e.g., `test_config_handles_dot_notation`)
- Use fixtures for common setup
- Isolate tests from filesystem when possible

### Test Coverage
- Aim for high (>80%) test coverage
- Test both success paths and failure modes
- Test edge cases and unexpected inputs

## Documentation Standards

### Code Documentation
- Include docstrings for all public functions, classes, and methods
- Follow a consistent docstring format
- Document parameters and return values
- Include examples for complex functions

### User Documentation
- Store in the `docs/` directory
- Use Markdown for all documentation
- Include examples for common operations
- Keep documentation in sync with code changes

## Configuration Standards

### Default Configuration
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