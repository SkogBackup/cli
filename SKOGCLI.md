IMPORTANT: THIS FILE CONTAINS EVERYTHING YOU NEED. NO ADDITIONAL CALLS, EXTERNAL INFORMATION, OR FILES ARE NEEDED. DO NOT LOOK AT OTHER FILES OR MAKE ADDITIONAL CALLS.

# Development Methodology: TDD/DDD

This project follows Test-Driven Development (TDD) and Documentation-Driven Design (DDD) principles. Here are the key guidelines:

1. ALWAYS START BY WRITING TESTS FIRST - This is non-negotiable. No implementation should be written before its corresponding tests.
2. DO NOT MODIFY OR EVEN TOUCH SOURCE CODE without proper test coverage and documentation first.
3. Tests serve as executable specifications and should validate the documented behaviors precisely.
4. Documentation guides the design and implementation - follow the documentation to understand requirements.
5. Any new functionality must be properly documented before implementation begins.

## Development Workflow
1. Document the feature requirements (already done in this file)
2. Write tests that validate the desired behavior (YOU MUST START HERE)
3. Run tests to confirm they fail (red phase)
4. Only then implement the minimal code needed to make tests pass
5. Refactor while maintaining passing tests
6. Repeat for each feature

## Important Notes
- Source code should NOT be modified without corresponding tests
- Documentation is the primary source of truth for requirements
- Tests must match the documented behavior precisely

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
- Tests MUST be written BEFORE any implementation code
- All tests should verify behavior described in documentation

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
1. Write tests for each command based on documentation (START HERE)
2. Verify tests fail as expected (since only placeholders exist)
3. Implement helper functions with proper test coverage
4. Implement each command with corresponding test validation:
   - `create` command for creating notes with title, folder, content, and optional tags
   - `read` command with support for pagination and raw/formatted display
   - `search` command with filtering options
   - `list` command for recent activity
   - `sync` and `status` commands for database maintenance
5. Update tests as needed to verify actual functionality instead of placeholders