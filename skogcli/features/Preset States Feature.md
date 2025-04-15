---
title: Preset States Feature
type: note
permalink: skogcli/features/preset-states-feature
---

# SkogCLI Preset States Feature

## Overview

The "Preset States" feature would allow saving and loading complete AI assistant states with full context, enabling instant access to specialized assistants for different projects and tasks.

## Motivation

When working on a project like SkogCLI:
- Context building takes valuable time at the start of each session
- Similar contexts are often rebuilt repeatedly for the same project
- Specialized knowledge needs to be reloaded for each specific task

Instead of recreating this context each time, we can maintain a library of preset assistant states that have the full context for different projects and tasks already loaded and ready to use.

## Implementation Concept

### Core Components

1. **State Snapshots**
   - Capture complete assistant state including:
     - Loaded context/knowledge
     - Active tools configuration
     - Project-specific information
     - Conversation history (optional)

2. **State Management**
   - Commands to save, list, and load states
   - Categorization system for different projects/tasks
   - Versioning for states as projects evolve

3. **Quick Access**
   - Shorthand commands to summon specific states
   - Tab completion for available states
   - Default states for common tasks

### Command Interface

```
# Save current assistant state
skogcli state save "skogcli-dev" --category "development" --description "Full context for SkogCLI development"

# List available states
skogcli state list
skogcli state list --category "development"

# Load a specific state
skogcli state load "skogcli-dev"

# Quick access (shorthand)
skogcli with skogcli-dev

# Update an existing state
skogcli state update "skogcli-dev"

# State information
skogcli state info "skogcli-dev"
```

## Technical Implementation

### State Storage Format

States would be stored as structured packages containing:

```json
{
  "metadata": {
    "name": "skogcli-dev",
    "category": "development",
    "description": "Full context for SkogCLI development",
    "created_at": "2025-04-13T20:30:00Z",
    "updated_at": "2025-04-13T20:30:00Z",
    "version": "1.0.0"
  },
  "context": {
    "documents": [
      "/path/to/document1.md",
      "/path/to/document2.md"
    ],
    "codebase": {
      "root": "/path/to/codebase",
      "main_files": [
        "src/skogcli/__main__.py",
        "src/skogcli/memory.py"
      ]
    },
    "memory_state": {
      "categories": ["project_info", "development_notes", "architecture"]
    }
  },
  "configuration": {
    "model": "Claude-3-Opus",
    "extensions": ["memory", "computercontroller", "developer", "skogai-memory"],
    "instructions": "file:///path/to/custom_instructions.md"
  }
}
```

### Integration with SkogCLI Memory

The preset states would leverage the existing memory system:

1. Each state would reference a specific set of memory categories
2. State loading would pre-load these memory categories
3. Project-specific documents would be linked directly

### Implementing in Python

```python
# src/skogcli/state.py

import typer
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from rich.table import Table
from rich.console import Console

from .decorators import with_explanation

state_app = typer.Typer(
    help="Manage AI assistant preset states",
    no_args_is_help=True
)

console = Console()

# State directory
STATE_DIR = Path.home() / ".skogcli" / "states"
STATE_DIR.mkdir(parents=True, exist_ok=True)

@state_app.callback()
def state_callback():
    """Manage AI assistant preset states."""
    pass

@state_app.command("save")
@with_explanation("Save the current assistant state with context and configuration.")
def save_state(
    name: str = typer.Argument(..., help="Name of the state to save"),
    category: str = typer.Option("general", help="Category for organizing states"),
    description: str = typer.Option("", help="Description of this state"),
    include_history: bool = typer.Option(False, help="Include conversation history")
):
    """
    Save the current assistant state with its context and configuration.
    
    This allows quickly restoring this exact state in future sessions.
    """
    # Generate state file path
    state_path = STATE_DIR / f"{name}.json"
    
    # Check if state already exists
    if state_path.exists():
        overwrite = typer.confirm(f"State '{name}' already exists. Overwrite?", default=False)
        if not overwrite:
            typer.echo("Operation cancelled.")
            raise typer.Exit()
    
    # Collect current context
    # In a real implementation, this would gather active context from the assistant
    current_context = {
        "documents": [],  # Would be populated with currently loaded documents
        "codebase": {
            "root": os.getcwd(),
            "main_files": []  # Would be populated with currently referenced files
        },
        "memory_state": {
            "categories": []  # Would be populated with active memory categories
        }
    }
    
    # Collect current configuration
    current_config = {
        "model": "Claude-3-Opus",  # Would be the actual model in use
        "extensions": ["memory", "computercontroller", "developer", "skogai-memory"],
        "instructions": ""  # Would be the actual instructions in use
    }
    
    # Build state object
    state = {
        "metadata": {
            "name": name,
            "category": category,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0"
        },
        "context": current_context,
        "configuration": current_config
    }
    
    # Save state to file
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    typer.echo(f"✓ State saved: {name}")

@state_app.command("list")
@with_explanation("List available assistant preset states.")
def list_states(
    category: Optional[str] = typer.Option(None, help="Filter by category"),
    show_details: bool = typer.Option(False, "--details", "-d", help="Show detailed information")
):
    """
    List available assistant preset states.
    
    Optionally filter by category or show detailed information.
    """
    # Create table for display
    table = Table(title="Available Assistant States")
    
    # Add columns
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Last Updated", style="blue")
    if show_details:
        table.add_column("Description", style="yellow")
    
    # Load and filter states
    states = []
    for state_file in STATE_DIR.glob("*.json"):
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Apply category filter if provided
        if category and state["metadata"]["category"] != category:
            continue
        
        # Add to list
        states.append(state)
    
    # Sort states by last updated
    states.sort(key=lambda s: s["metadata"]["updated_at"], reverse=True)
    
    # Add rows to table
    for state in states:
        meta = state["metadata"]
        if show_details:
            table.add_row(
                meta["name"],
                meta["category"],
                meta["updated_at"].split("T")[0],  # Just show date part
                meta["description"]
            )
        else:
            table.add_row(
                meta["name"],
                meta["category"],
                meta["updated_at"].split("T")[0]  # Just show date part
            )
    
    # Print table
    console.print(table)
    
    # Show count
    typer.echo(f"\nTotal states: {len(states)}")

@state_app.command("load")
@with_explanation("Load a saved assistant state with its full context.")
def load_state(
    name: str = typer.Argument(..., help="Name of the state to load"),
    include_history: bool = typer.Option(False, help="Include conversation history if available")
):
    """
    Load a saved assistant state with its full context.
    
    This restores the assistant to the exact state that was saved.
    """
    # Generate state file path
    state_path = STATE_DIR / f"{name}.json"
    
    # Check if state exists
    if not state_path.exists():
        typer.echo(f"Error: State '{name}' not found.")
        raise typer.Exit(code=1)
    
    # Load state
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    # In a real implementation, this would now apply the state to the assistant
    # - Load referenced documents
    # - Set up the correct configuration
    # - Restore memory categories
    
    typer.echo(f"✓ State loaded: {name}")
    
    # Show a summary of what was loaded
    meta = state["metadata"]
    typer.echo(f"\nState information:")
    typer.echo(f"  Name: {meta['name']}")
    typer.echo(f"  Category: {meta['category']}")
    typer.echo(f"  Last updated: {meta['updated_at']}")
    if meta['description']:
        typer.echo(f"  Description: {meta['description']}")
    
    # Show context summary
    context = state["context"]
    typer.echo(f"\nContext loaded:")
    typer.echo(f"  Documents: {len(context['documents'])}")
    typer.echo(f"  Codebase root: {context['codebase']['root']}")
    typer.echo(f"  Memory categories: {', '.join(context['memory_state']['categories'])}")

@state_app.command("update")
@with_explanation("Update an existing assistant state with current context.")
def update_state(
    name: str = typer.Argument(..., help="Name of the state to update")
):
    """
    Update an existing assistant state with the current context.
    
    This preserves metadata while updating context and configuration.
    """
    # Generate state file path
    state_path = STATE_DIR / f"{name}.json"
    
    # Check if state exists
    if not state_path.exists():
        typer.echo(f"Error: State '{name}' not found.")
        raise typer.Exit(code=1)
    
    # Load existing state
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    # Collect current context and configuration
    # Similar to save_state but would update rather than create new
    
    # Update timestamp
    state["metadata"]["updated_at"] = datetime.now().isoformat()
    
    # Save updated state
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    typer.echo(f"✓ State updated: {name}")

@state_app.command("info")
@with_explanation("Show detailed information about a saved state.")
def state_info(
    name: str = typer.Argument(..., help="Name of the state to show info for")
):
    """
    Show detailed information about a saved assistant state.
    """
    # Generate state file path
    state_path = STATE_DIR / f"{name}.json"
    
    # Check if state exists
    if not state_path.exists():
        typer.echo(f"Error: State '{name}' not found.")
        raise typer.Exit(code=1)
    
    # Load state
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    # Display formatted information
    meta = state["metadata"]
    context = state["context"]
    config = state["configuration"]
    
    typer.echo(f"State: {meta['name']}")
    typer.echo("=" * (len(meta['name']) + 7))
    typer.echo(f"Category: {meta['category']}")
    typer.echo(f"Created: {meta['created_at']}")
    typer.echo(f"Updated: {meta['updated_at']}")
    typer.echo(f"Version: {meta['version']}")
    if meta['description']:
        typer.echo(f"\nDescription:\n{meta['description']}")
    
    typer.echo("\nContext:")
    typer.echo(f"  Documents: {len(context['documents'])}")
    if context['documents']:
        for doc in context['documents'][:5]:  # Show first 5
            typer.echo(f"    - {doc}")
        if len(context['documents']) > 5:
            typer.echo(f"    ... and {len(context['documents']) - 5} more")
    
    typer.echo(f"  Codebase: {context['codebase']['root']}")
    if context['codebase']['main_files']:
        for file in context['codebase']['main_files'][:5]:  # Show first 5
            typer.echo(f"    - {file}")
        if len(context['codebase']['main_files']) > 5:
            typer.echo(f"    ... and {len(context['codebase']['main_files']) - 5} more")
    
    typer.echo(f"  Memory Categories:")
    for cat in context['memory_state']['categories']:
        typer.echo(f"    - {cat}")
    
    typer.echo("\nConfiguration:")
    typer.echo(f"  Model: {config['model']}")
    typer.echo(f"  Extensions:")
    for ext in config['extensions']:
        typer.echo(f"    - {ext}")
    if config['instructions']:
        typer.echo(f"  Custom Instructions: {config['instructions']}")

@state_app.command("delete")
@with_explanation("Delete a saved assistant state.")
def delete_state(
    name: str = typer.Argument(..., help="Name of the state to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Delete without confirmation")
):
    """
    Delete a saved assistant state.
    
    Removes the state file from the system.
    """
    # Generate state file path
    state_path = STATE_DIR / f"{name}.json"
    
    # Check if state exists
    if not state_path.exists():
        typer.echo(f"Error: State '{name}' not found.")
        raise typer.Exit(code=1)
    
    # Confirm deletion
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete state '{name}'?", default=False)
        if not confirm:
            typer.echo("Operation cancelled.")
            raise typer.Exit()
    
    # Delete the state file
    state_path.unlink()
    
    typer.echo(f"✓ State deleted: {name}")

# Add the 'with' command for quick access
@state_app.command("with")
@with_explanation("Start a session with a specific assistant state.")
def with_state(
    name: str = typer.Argument(..., help="Name of the state to use")
):
    """
    Start a new session with the specified assistant state.
    
    This is a convenience shortcut for 'load' that also starts a session.
    """
    # First load the state
    load_state(name)
    
    # Then start a session with this state
    # In a real implementation, this would launch the assistant with the loaded state
    typer.echo(f"\nStarting session with state '{name}'...")
    
    # Placeholder for actual session launch
    typer.echo("Session started!")

# Add to SkogCLI main app
def setup():
    from .main import app
    app.add_typer(state_app, name="state")
```

### Integration into `__init__.py`

```python
from .state import state_app

# Add the state app
app.add_typer(state_app, name="state")

# Add shorthand for 'with' command
@app.command("with")
def with_state_shorthand(name: str):
    """Start a session with a specific assistant state."""
    from .state import with_state
    with_state(name)
```

## User Experience Examples

### Development Workflow

```bash
# At the start of a workday:
$ skogcli with skogcli-dev
✓ State loaded: skogcli-dev
Starting session with state 'skogcli-dev'...

# AI assistant is immediately ready with full project context:
# - Code structure understanding
# - Recent development history
# - Project architecture
# - Development goals
```

### Context Switching

```bash
# Working on multiple projects:
$ skogcli with skogai-memory
✓ State loaded: skogai-memory
Starting session with state 'skogai-memory'...

# Later switching to another project:
$ skogcli with skogcli-dev
✓ State loaded: skogcli-dev
Starting session with state 'skogcli-dev'...
```

### Specialized Tasks

```bash
# For code review tasks:
$ skogcli with code-reviewer
✓ State loaded: code-reviewer
Starting session with state 'code-reviewer'...

# For documentation writing:
$ skogcli with docs-writer
✓ State loaded: docs-writer
Starting session with state 'docs-writer'...

# For architecture planning:
$ skogcli with architect
✓ State loaded: architect
Starting session with state 'architect'...
```

## Benefits

1. **Time Savings**
   - Eliminate context rebuilding (potentially saving 5-10 minutes per session)
   - Instantly switch between different projects or task types

2. **Consistency**
   - Ensure the assistant always has the same baseline understanding
   - Maintain consistent context across multiple sessions

3. **Specialization**
   - Create purpose-built assistants for different task types
   - Optimize context for specific kinds of work

4. **Knowledge Persistence**
   - Preserve valuable context across sessions
   - Build on previous insights without starting from scratch

## Implementation Timeline

1. **Phase 1: Core State Management**
   - Basic save/load/list functionality
   - Simple metadata tracking

2. **Phase 2: Context Integration**
   - Full context capture and restoration
   - Memory system integration

3. **Phase 3: Advanced Features**
   - State versioning and history
   - Differential updates
   - State sharing capabilities

4. **Phase 4: UI Enhancements**
   - Visual state selection interface
   - State preview capabilities

## Conclusion

The Preset States feature would significantly enhance developer productivity by eliminating repetitive context building and enabling rapid context switching between projects and tasks. By maintaining a library of specialized assistant states, developers can instantly access the right context for any work they're doing.

This feature aligns perfectly with the SkogCLI philosophy of making AI assistance seamlessly integrated into development workflows.