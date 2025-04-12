run skogcli via "uv run skogcli"

use "uv add <package> && uv lock && uv sync" instead of "pip install"

empty calls to a command should always return help - use the no_args_is_help=True parameter in typer.Typer() to enable this behavior

# Typer Best Practices
- Use docstrings for command descriptions
- Use help parameter in Arguments and Options for detailed help
- Use Annotated for type hints with metadata
- Create subcommands with typer.Typer() and app.add_typer()
- Use Enum classes for choice options
- Set context_settings for consistent help behavior

# Rich Integration
- Use Rich for enhanced terminal output
- Create tables with rich.table.Table for structured data display
- Use console.print() for styled output
- Format command output consistently across the application

# Configuration Management
- Implement a config command for managing application settings
- Use --show to display current configuration
- Use --set and --value for modifying configuration
- Include a --reset option to restore defaults
- Store configuration in a standard location (e.g., ~/.config/skogcli/config.json)

# Testing with pytest
- Run tests with `uv run pytest tests/`
- Run specific test files with `uv run pytest tests/test_examples.py`
- Run specific test functions with `uv run pytest tests/test_examples.py::test_examples_basic`
- Use verbose output with `-v` flag: `uv run pytest tests/ -v`
- Use the test runner script: `./tests/run_tests.sh [options]`
- Test Typer CLI apps with `CliRunner` from `typer.testing`
- Verify exit codes and stdout content in assertions

# Memory Module Implementation

## Current Status
The memory module has been implemented with placeholder functionality ("Not implemented yet") for the following commands:
- `create`: Create or update a note in a knowledge base
- `read`: Read a note from the knowledge base
- `search`: Search across the knowledge base
- `list`: List recent activity
- `sync`: Synchronize knowledge files with database
- `status`: Show sync status between files and database

## Implementation Details
The memory module is planned as a wrapper around basic-memory with the following components:

### Command Mapping
| SkogCLI Command | basic-memory Equivalent | Description |
|-----------------|-------------------------|-------------|
| `memory create` | `tool write-note` | Create or update a note with title and folder |
| `memory read` | `tool read-note` | Read a note by identifier with pagination |
| `memory search` | `tool search-notes` | Search across all content with filters |
| `memory list` | `tool recent-activity` | List recent notes/activity with timeframe |
| `memory sync` | `sync` | Sync knowledge files with database |
| `memory status` | `status` | Show sync status |

### Helper Functions
The implementation requires helper functions to interact with basic-memory:
```python
def run_basic_memory(args: List[str]) -> subprocess.CompletedProcess:
    """Run basic-memory with the given arguments."""
    cmd = ["basic-memory"] + args
    return subprocess.run(cmd, capture_output=True, text=True)

def process_markdown(markdown_str: str, raw: bool = False) -> Union[str, Markdown]:
    """Process markdown string for display."""
    if raw:
        return markdown_str
    return Markdown(markdown_str)
```

### Implementation Process
1. Implement helper functions
2. Implement each command:
   - `create` command for creating notes with title, folder, content, and optional tags
   - `read` command with support for pagination and raw/formatted display
   - `search` command with filtering options
   - `list` command for recent activity
   - `sync` and `status` commands for database maintenance
3. Update tests to verify actual functionality rather than placeholders