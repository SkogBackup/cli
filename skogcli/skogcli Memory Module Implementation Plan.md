---
title: skogcli Memory Module Implementation Plan
type: note
permalink: projects/skogcli/skogcli-memory-module-implementation-plan
tags:
- '#skogcli #memory-module #implementation-plan'
---

# skogcli Memory Module Implementation

This document outlines the actual implementation plan for the memory module in skogcli, progressing from the current placeholder functions to fully implemented ones.

## Current Status

The memory module has been implemented with placeholder functionality ("Not implemented yet") for these commands:

- `create`: Create or update a note in a knowledge base
- `read`: Read a note from the knowledge base
- `search`: Search across the knowledge base
- `list`: List recent activity
- `sync`: Synchronize knowledge files with database
- `status`: Show sync status between files and database

All commands have complete CLI interfaces with appropriate arguments and options, and comprehensive tests are in place to verify the structure.

## Implementation Plan

### 1. Add Command Helper Functions

First, we'll add helper functions to interact with basic-memory:

```python
import subprocess
from typing import List, Optional, Union
from rich.markdown import Markdown

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

### 2. Implement `create` Command

The create command will be implemented to allow creating or updating notes:

```python
@memory_app.command("create")
@with_explanation("Create or update a note in your knowledge base.")
def create(
    title: str = typer.Argument(..., help="Title of the note"),
    folder: str = typer.Argument(..., help="Folder to create the note in"),
    content: Optional[str] = typer.Option(None, "--content", "-c", help="Note content (if not provided, read from stdin)"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Tags to apply to the note (comma-separated)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Specific project to use"),
):
    """
    Create or update a note in your knowledge base.
    
    Examples:
    
    Create from argument:
      skogcli memory create "My Idea" notes --content "# My Idea\n\nThis is a great idea."
      
    Create with tags:
      skogcli memory create "Meeting Notes" meetings --tags "work,important,2025"
    """
    cmd = ["tool", "write-note", "--title", title, "--folder", folder]
    if tags:
        cmd.extend(["--tags", tags])
    
    if project:
        cmd = ["--project", project] + cmd
        
    if content:
        result = run_basic_memory(cmd + ["--content", content])
    else:
        # Read from stdin
        typer.echo("Enter note content (Ctrl+D to finish):")
        from_stdin = typer.get_text_stream('stdin').read()
        result = run_basic_memory(cmd + ["--content", from_stdin])
    
    if result.returncode == 0:
        typer.echo(f"✓ Note saved: {title} in {folder}")
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)
```

### 3. Implement `read` Command

```python
@memory_app.command("read")
@with_explanation("Read a note from your knowledge base.")
def read(
    identifier: str = typer.Argument(..., help="Note identifier"),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(10, "--page-size", help="Number of items per page"),
    raw: bool = typer.Option(False, "--raw", help="Display raw markdown without rendering"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Specific project to use"),
):
    """
    Read a note from your knowledge base.
    
    The note will be rendered as rich markdown by default.
    Use --raw to display the unprocessed markdown.
    
    Examples:
    
    Read a note:
      skogcli memory read "My Note"
      
    Read raw markdown:
      skogcli memory read "Meeting Notes" --raw
      
    Paginate content:
      skogcli memory read "Long Document" --page 2 --page-size 20
    """
    cmd = ["tool", "read-note", identifier, "--page", str(page), "--page-size", str(page_size)]
    if project:
        cmd = ["--project", project] + cmd
        
    result = run_basic_memory(cmd)
    
    if result.returncode == 0:
        if raw:
            typer.echo(result.stdout)
        else:
            console.print(process_markdown(result.stdout))
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)
```

### 4. Implement `search` Command

```python
@memory_app.command("search")
@with_explanation("Search across your knowledge base for specific content.")
def search(
    query: str = typer.Argument(..., help="Search query"),
    permalink: bool = typer.Option(False, "--permalink", help="Search permalink values"),
    title: bool = typer.Option(False, "--title", help="Search title values"),
    after_date: Optional[str] = typer.Option(None, "--after-date", help="Search results after date (e.g. '2d', '1 week')"),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(10, "--page-size", help="Number of items per page"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Specific project to use"),
):
    """
    Search across your knowledge base for specific content.
    
    Results will be displayed with titles and snippets.
    
    Examples:
    
    Basic search:
      skogcli memory search "project ideas"
      
    Search only titles:
      skogcli memory search "meeting" --title
      
    Search with date filter:
      skogcli memory search "important" --after-date "1 week"
    """
    cmd = ["tool", "search-notes", query, "--page", str(page), "--page-size", str(page_size)]
    
    if permalink:
        cmd.append("--permalink")
    if title:
        cmd.append("--title")
    if after_date:
        cmd.extend(["--after_date", after_date])
    
    if project:
        cmd = ["--project", project] + cmd
        
    result = run_basic_memory(cmd)
    
    if result.returncode == 0:
        console.print(result.stdout)
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)
```

### 5. Implement `list` Command

```python
@memory_app.command("list")
@with_explanation("List recent activity across your knowledge base.")
def list_notes(
    type: Optional[str] = typer.Option(None, "--type", help="Activity type (entity, observation, relation)"),
    depth: int = typer.Option(1, "--depth", help="Depth of related entities"),
    timeframe: str = typer.Option("7d", "--timeframe", help="Timeframe for recent activity (e.g., '7d', '2w')"),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(10, "--page-size", help="Number of items per page"),
    max_related: int = typer.Option(10, "--max-related", help="Maximum number of related items"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Specific project to use"),
):
    """
    List recent activity across your knowledge base.
    
    Displays recently created or updated notes.
    
    Examples:
    
    List recent activity (default 7 days):
      skogcli memory list
      
    List specific type:
      skogcli memory list --type entity
      
    Custom timeframe:
      skogcli memory list --timeframe 30d
    """
    cmd = ["tool", "recent-activity", 
           "--depth", str(depth),
           "--timeframe", timeframe,
           "--page", str(page),
           "--page-size", str(page_size),
           "--max-related", str(max_related)]
    
    if type:
        cmd.extend(["--type", type])
    
    if project:
        cmd = ["--project", project] + cmd
        
    result = run_basic_memory(cmd)
    
    if result.returncode == 0:
        console.print(result.stdout)
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)
```

### 6. Implement `sync` Command

```python
@memory_app.command("sync")
@with_explanation("Synchronize your knowledge files with the database.")
def sync(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Specific project to use"),
):
    """
    Synchronize your knowledge files with the database.
    
    This ensures all files are properly indexed and searchable.
    """
    cmd = ["sync"]
    if project:
        cmd = ["--project", project] + cmd
        
    result = run_basic_memory(cmd)
    
    if result.returncode == 0:
        typer.echo("Synchronization completed successfully.")
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)
```

### 7. Implement `status` Command

```python
@memory_app.command("status")
@with_explanation("Show sync status between files and the database.")
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Specific project to use"),
):
    """
    Show sync status between your knowledge files and the database.
    
    Displays which files need to be synchronized.
    """
    cmd = ["status"]
    if project:
        cmd = ["--project", project] + cmd
        
    result = run_basic_memory(cmd)
    
    if result.returncode == 0:
        console.print(result.stdout)
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)
```

## Testing Strategy

The testing approach will evolve from verifying command structure to checking actual functionality:

1. First phase: Test command structure and help text (current tests)
2. Second phase: Mock `subprocess.run` to test command construction
3. Third phase: Integration tests with basic-memory

### Example of Second Phase Test

```python
@patch('subprocess.run')
def test_memory_create_command_functionality(mock_run):
    # Set up the mock
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = "Note created successfully"
    mock_run.return_value = mock_process
    
    # Test basic invocation
    result = runner.invoke(app, ["memory", "create", "Test Note", "test", "--content", "Test content"])
    assert result.exit_code == 0
    assert "Note saved: Test Note in test" in result.stdout
    
    # Verify subprocess call
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    cmd = args[0]
    assert cmd[0] == "basic-memory"
    assert "tool" in cmd
    assert "write-note" in cmd
    assert "--title" in cmd
    assert "Test Note" in cmd
    assert "--folder" in cmd
    assert "test" in cmd
    assert "--content" in cmd
    assert "Test content" in cmd
```

## Implementation Timeline

1. **Phase 1**: Add helper functions and update tests to mock subprocess
2. **Phase 2**: Implement the `create` command and verify with tests
3. **Phase 3**: Implement the `read` command and verify
4. **Phase 4**: Implement the `search` command
5. **Phase 5**: Implement the `list` command
6. **Phase 6**: Implement the `sync` and `status` commands
7. **Phase 7**: Add integration tests for the full workflow

## Future Enhancements

Once the basic functionality is implemented, we can consider these enhancements:

1. **Improved Formatting**: Better display of search results and lists using rich tables
2. **Caching**: Local caching of frequently accessed notes
3. **Templates**: Support for creating notes from templates
4. **Batch Operations**: Support for bulk operations on multiple notes
5. **Configuration Integration**: Integrate with skogcli's config system
6. **Additional Commands**: Import, export, and project management