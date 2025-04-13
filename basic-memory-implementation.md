# SkogCLI Memory Module Implementation

This document outlines the implementation plan for integrating basic-memory into SkogCLI as a simplified wrapper module.

## Overview

The memory module will provide a streamlined interface to basic-memory's core functionality, making it easier to manage personal knowledge directly from SkogCLI. The implementation will focus on the most commonly used features while maintaining consistency with SkogCLI's design patterns.

## Command Structure

```
skogcli memory [OPTIONS] COMMAND [ARGS]...
```

### Subcommands

1. `create`: Create or update a note
2. `read`: Read a note from the knowledge base
3. `search`: Search across the knowledge base
4. `list`: List recent notes or activity
5. `sync`: Synchronize files with the database
6. `status`: Show sync status

## Implementation Details

### Command Mapping

| SkogCLI Command | basic-memory Equivalent | Description |
|-----------------|-------------------------|-------------|
| `memory create` | `tool write-note` | Create or update a note with title and folder |
| `memory read` | `tool read-note` | Read a note by identifier with pagination |
| `memory search` | `tool search-notes` | Search across all content with filters |
| `memory list` | `tool recent-activity` | List recent notes/activity with timeframe |
| `memory sync` | `sync` | Sync knowledge files with database |
| `memory status` | `status` | Show sync status |

### Core Module Structure

```python
# src/skogcli/memory.py

import typer
import subprocess
from typing import Optional, List
from rich.console import Console
from rich.markdown import Markdown
from .decorators import with_explanation

memory_app = typer.Typer(
    help="Knowledge management powered by basic-memory",
    no_args_is_help=True
)

console = Console()

def run_basic_memory(args: List[str]) -> subprocess.CompletedProcess:
    """Run basic-memory with the given arguments."""
    cmd = ["uvx", "basic-memory"] + args
    return subprocess.run(cmd, capture_output=True, text=True)

@memory_app.callback()
def memory_callback():
    """Knowledge management powered by basic-memory."""
    pass

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
      
    Create from stdin:
      echo "# My Idea\n\nThis is a great idea." | skogcli memory create "My Idea" notes
      
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

@memory_app.command("read")
@with_explanation("Read a note from your knowledge base.")
def read(
    identifier: str = typer.Argument(..., help="Note identifier"),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(10, "--page-size", help="Number of items per page"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Specific project to use"),
    raw: bool = typer.Option(False, "--raw", help="Display raw markdown without rendering"),
):
    """
    Read a note from your knowledge base.
    
    The note will be rendered as rich markdown by default.
    Use --raw to display the unprocessed markdown.
    """
    cmd = ["tool", "read-note", identifier, "--page", str(page), "--page-size", str(page_size)]
    if project:
        cmd = ["--project", project] + cmd
        
    result = run_basic_memory(cmd)
    
    if result.returncode == 0:
        if raw:
            typer.echo(result.stdout)
        else:
            console.print(Markdown(result.stdout))
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)

@memory_app.command("search")
@with_explanation("Search across your knowledge base.")
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

@memory_app.command("list")
@with_explanation("List recent notes and activity in your knowledge base.")
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

### Integration with SkogCLI

In `src/skogcli/__init__.py`, add:

```python
from .memory import memory_app

# Add the memory app as a subcommand
app.add_typer(memory_app, name="memory")
```

## User Experience

### Creating a Note

```bash
# Create a note with inline content
skogcli memory create "My Great Idea" notes --content "# My Great Idea\n\nThis is a brilliant idea I had."

# Create a note with tags
skogcli memory create "Meeting Notes" meetings --tags "work,important,2025"

# Create a note from stdin (interactive mode)
skogcli memory create "Weekly Update" reports
```

### Reading a Note

```bash
# Read a note with formatted markdown
skogcli memory read "My Great Idea"

# Read raw markdown
skogcli memory read "Meeting Notes" --raw

# Read with pagination
skogcli memory read "Long Document" --page 2 --page-size 20
```

### Searching

```bash
# Basic search
skogcli memory search "brilliant idea"

# Search only titles
skogcli memory search "meeting" --title

# Search with date filter
skogcli memory search "important" --after-date "1 week"

# Paginate results
skogcli memory search "project ideas" --page 2 --page-size 15
```

### Listing Recent Activity

```bash
# List recent notes (default 7 days)
skogcli memory list

# List specific type
skogcli memory list --type entity

# Custom timeframe
skogcli memory list --timeframe 30d

# Adjust depth and related items
skogcli memory list --depth 2 --max-related 20
```

### Sync and Status

```bash
# Sync files with database
skogcli memory sync

# Check sync status
skogcli memory status
```

## Project Selection

All commands support the `--project` option to specify which basic-memory project to use:

```bash
# Use specific project
skogcli memory create notes/idea.md --content "..." --project work

# Read from specific project
skogcli memory read notes/meeting.md --project personal
```

## Error Handling

The implementation includes proper error handling:

1. Captures and displays error messages from basic-memory
2. Uses appropriate exit codes for error conditions
3. Provides clear feedback for successful operations

## Advantages of This Approach

1. **Simplified Interface**: Provides a streamlined, intuitive interface to basic-memory
2. **Consistent Design**: Follows SkogCLI's existing patterns and conventions
3. **Rich Output**: Leverages rich formatting for better readability
4. **Focused Functionality**: Includes only the most essential commands
5. **Extensible**: Can be easily expanded to include more basic-memory features

## Future Enhancements

1. **Context Building**: Add integration with basic-memory's context building
2. **Conversation Continuation**: Support for continuing conversations
3. **Import Capabilities**: Add support for importing from various sources
4. **Project Management**: Add commands for managing basic-memory projects
5. **Configuration Integration**: Integrate with SkogCLI's config system
