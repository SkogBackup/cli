---
title: 'SkogCLI Preset States: Comprehensive Implementation Guide'
type: note
permalink: skogcli/features/skog-cli-preset-states-comprehensive-implementation-guide
---

# SkogCLI Preset States: Comprehensive Implementation Guide

## Concept Overview

Preset States enable saving and loading complete AI assistant contexts in SkogCLI. This allows developers to instantly access specialized assistants with full context for different projects or tasks without rebuilding context each time.

## Key Use Cases

1. **Project-Specific Contexts**
   - SkogCLI development context
   - Memory system integration context
   - MCP protocol development context
   
2. **Task-Specific Assistants**
   - Code reviewer mode
   - Documentation writer mode
   - Architecture design mode
   - Debugging assistant mode

3. **Context Preservation**
   - Save valuable context built during complex discussions
   - Transfer context between sessions without loss
   - Create progressive context states as projects evolve

## Technical Architecture

### Data Model

**State Package**:
```typescript
interface StateMetadata {
  name: string;               // Unique identifier for this state
  category: string;           // Organizational category
  description: string;        // Human-readable description
  created_at: string;         // ISO timestamp
  updated_at: string;         // ISO timestamp
  version: string;            // Semver version of state format
  tags: string[];             // Optional tags for filtering
}

interface StateContext {
  documents: string[];        // Paths to relevant documents
  codebase: {
    root: string;             // Root directory of project
    main_files: string[];     // Key files for context
    file_patterns: string[];  // Glob patterns for included files
  };
  memory_state: {
    categories: string[];     // Memory categories to load
    global_memories: boolean; // Whether to include global memories
    timeframe: string;        // How far back to load memories
  };
  chat_history?: {
    summary: string;          // Summary of previous context
    key_points: string[];     // Important points from history
    include_raw: boolean;     // Whether to include raw history
  };
}

interface StateConfig {
  model: string;              // Model identifier
  extensions: string[];       // Enabled extensions
  parameters: {
    temperature: number;      // Generation temperature
    top_p: number;            // Top-p sampling parameter
    max_tokens: number;       // Maximum token generation limit
    [key: string]: any;       // Other model-specific parameters
  };
  instructions: string | {    // Instructions for the assistant
    file: string;             // Path to instructions file
    content: string;          // Direct instruction content
  };
  system_message?: string;    // Custom system message
}

interface PresetState {
  metadata: StateMetadata;
  context: StateContext;
  configuration: StateConfig;
}
```

### Storage Architecture

1. **File Location**
   - Primary: `~/.skogcli/states/[name].json`
   - Shared: `~/.skogcli/shared_states/[name].json`

2. **Version Control Integration**
   - Optional git repository for state tracking
   - Commit messages for state evolution

3. **Compression & Optimization**
   - Large states compressed with gzip
   - Reference-based storage for common elements

### State Capture Process

1. **Context Collection**
   - Document ingestion tracking
   - Code navigation history
   - Important file identification
   - Memory category utilization

2. **Configuration Capture**
   - Current model settings
   - Extension configuration
   - Custom instructions

3. **State Optimization**
   - Remove redundant/unused context
   - Prioritize most relevant information
   - Extract key insights for summary

### State Restoration Process

1. **Environment Preparation**
   - Extension activation
   - Model configuration
   - Memory system preparation

2. **Context Loading**
   - Document preloading
   - Code indexing
   - Memory retrieval

3. **Assistant Initialization**
   - System message construction
   - Instructions application
   - Previous context summarization

## Implementation Flow

### Command Structure

```
skogcli state <command> [options]
```

### Subcommands

1. **Save Command**
   ```
   skogcli state save NAME [options]
   ```
   Options:
   - `--category TEXT`: Category for organization
   - `--description TEXT`: Human description
   - `--tags TEXT`: Comma-separated tags
   - `--include-history`: Include chat history
   - `--shared`: Save as shared state

2. **Load Command**
   ```
   skogcli state load NAME [options]
   ```
   Options:
   - `--include-history`: Restore chat history
   - `--merge`: Merge with current context
   - `--version TEXT`: Specific state version

3. **List Command**
   ```
   skogcli state list [options]
   ```
   Options:
   - `--category TEXT`: Filter by category
   - `--tag TEXT`: Filter by tag
   - `--details`: Show detailed info
   - `--format [table|json]`: Output format

4. **Update Command**
   ```
   skogcli state update NAME [options]
   ```
   Options:
   - `--description TEXT`: Update description
   - `--category TEXT`: Update category
   - `--tags TEXT`: Update tags

5. **Info Command**
   ```
   skogcli state info NAME [options]
   ```
   Options:
   - `--format [text|json]`: Output format

6. **Delete Command**
   ```
   skogcli state delete NAME [options]
   ```
   Options:
   - `--force`: Delete without confirmation

7. **Copy Command**
   ```
   skogcli state copy SOURCE TARGET [options]
   ```
   Options:
   - `--overwrite`: Overwrite existing target

8. **Export Command**
   ```
   skogcli state export NAME PATH [options]
   ```
   Options:
   - `--format [json|yaml]`: Export format

9. **Import Command**
   ```
   skogcli state import PATH [NAME] [options]
   ```
   Options:
   - `--overwrite`: Overwrite existing state

### Shorthand Commands

```
skogcli with NAME [options]
```
Equivalent to `skogcli state load NAME` followed by starting a session.

## Python Implementation

### Core State Module

```python
# src/skogcli/state.py

import typer
import json
import os
import gzip
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from rich.table import Table
from rich.console import Console
from rich.markdown import Markdown
import yaml

from .decorators import with_explanation

state_app = typer.Typer(
    help="Manage AI assistant preset states",
    no_args_is_help=True
)

console = Console()

# State directories
STATE_DIR = Path.home() / ".skogcli" / "states"
STATE_DIR.mkdir(parents=True, exist_ok=True)

SHARED_STATE_DIR = Path.home() / ".skogcli" / "shared_states"
SHARED_STATE_DIR.mkdir(parents=True, exist_ok=True)

# Current session state (for capture and updates)
_current_context: Dict[str, Any] = {
    "documents": [],
    "codebase": {
        "root": "",
        "main_files": [],
        "file_patterns": []
    },
    "memory_state": {
        "categories": [],
        "global_memories": True,
        "timeframe": "all"
    }
}

_current_config: Dict[str, Any] = {
    "model": "default",
    "extensions": [],
    "parameters": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 4096
    },
    "instructions": ""
}

def get_state_path(name: str, shared: bool = False) -> Path:
    """Get the path for a state by name."""
    if shared:
        return SHARED_STATE_DIR / f"{name}.json"
    return STATE_DIR / f"{name}.json"

def load_state_file(path: Path) -> Dict[str, Any]:
    """Load a state file with support for compressed states."""
    if path.name.endswith(".gz"):
        with gzip.open(path, 'rt') as f:
            return json.load(f)
    else:
        with open(path, 'r') as f:
            return json.load(f)

def save_state_file(path: Path, state: Dict[str, Any], compress: bool = False) -> None:
    """Save a state file with optional compression."""
    if compress:
        save_path = Path(str(path) + ".gz")
        with gzip.open(save_path, 'wt') as f:
            json.dump(state, f, indent=2)
    else:
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)

# Update context tracking (would be called during normal operations)
def track_document(doc_path: str) -> None:
    """Track a document being used in the current context."""
    if doc_path not in _current_context["documents"]:
        _current_context["documents"].append(doc_path)

def track_code_file(file_path: str) -> None:
    """Track a code file being used in the current context."""
    if file_path not in _current_context["codebase"]["main_files"]:
        _current_context["codebase"]["main_files"].append(file_path)

def track_memory_category(category: str) -> None:
    """Track a memory category being used."""
    if category not in _current_context["memory_state"]["categories"]:
        _current_context["memory_state"]["categories"].append(category)

def set_codebase_root(root_path: str) -> None:
    """Set the codebase root for the current context."""
    _current_context["codebase"]["root"] = root_path

# Actual command implementations
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
    tags: str = typer.Option("", help="Comma-separated tags"),
    include_history: bool = typer.Option(False, help="Include conversation history"),
    shared: bool = typer.Option(False, help="Save as a shared state"),
    compress: bool = typer.Option(False, help="Compress the state file")
):
    """
    Save the current assistant state with its context and configuration.
    
    This allows quickly restoring this exact state in future sessions.
    """
    # Generate state file path
    state_path = get_state_path(name, shared)
    
    # Check if state already exists
    if state_path.exists():
        overwrite = typer.confirm(f"State '{name}' already exists. Overwrite?", default=False)
        if not overwrite:
            typer.echo("Operation cancelled.")
            raise typer.Exit()
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    
    # Build state object
    state = {
        "metadata": {
            "name": name,
            "category": category,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "tags": tag_list
        },
        "context": _current_context.copy(),
        "configuration": _current_config.copy()
    }
    
    # Add chat history if requested
    if include_history:
        # This would capture actual history in implementation
        state["context"]["chat_history"] = {
            "summary": "Context from previous conversation",
            "key_points": [],
            "include_raw": True
        }
    
    # Save state to file
    save_state_file(state_path, state, compress)
    
    typer.echo(f"✓ State saved: {name}" + (" (shared)" if shared else ""))
    
    # Show confirmation with size info
    file_size = state_path.stat().st_size
    typer.echo(f"  File: {state_path}")
    typer.echo(f"  Size: {file_size / 1024:.1f} KB")

@state_app.command("list")
@with_explanation("List available assistant preset states.")
def list_states(
    category: Optional[str] = typer.Option(None, help="Filter by category"),
    tag: Optional[str] = typer.Option(None, help="Filter by tag"),
    shared: bool = typer.Option(False, help="List shared states"),
    details: bool = typer.Option(False, "--details", "-d", help="Show detailed information"),
    format: str = typer.Option("table", help="Output format (table or json)")
):
    """
    List available assistant preset states.
    
    Optionally filter by category or show detailed information.
    """
    # Determine which directory to use
    states_dir = SHARED_STATE_DIR if shared else STATE_DIR
    
    # Create table for display
    table = Table(title=f"Available Assistant States{' (Shared)' if shared else ''}")
    
    # Add columns
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Last Updated", style="blue")
    table.add_column("Size", style="magenta")
    if details:
        table.add_column("Description", style="yellow")
        table.add_column("Tags", style="red")
    
    # Load and filter states
    states = []
    for state_file in states_dir.glob("*.json*"):  # Include .json.gz
        try:
            state = load_state_file(state_file)
            
            # Apply category filter if provided
            if category and state["metadata"]["category"] != category:
                continue
                
            # Apply tag filter if provided
            if tag and tag not in state["metadata"].get("tags", []):
                continue
            
            # Add file size information
            file_size = state_file.stat().st_size
            state["metadata"]["file_size"] = file_size
            
            # Add to list
            states.append(state)
        except (json.JSONDecodeError, KeyError) as e:
            typer.echo(f"Error loading state {state_file}: {e}", err=True)
    
    # Sort states by last updated
    states.sort(key=lambda s: s["metadata"]["updated_at"], reverse=True)
    
    if format == "json":
        # Output as JSON
        typer.echo(json.dumps({"states": states}, indent=2))
    else:
        # Add rows to table
        for state in states:
            meta = state["metadata"]
            size_str = f"{meta['file_size'] / 1024:.1f} KB"
            
            if details:
                tag_str = ", ".join(meta.get("tags", []))
                table.add_row(
                    meta["name"],
                    meta["category"],
                    meta["updated_at"].split("T")[0],  # Just show date part
                    size_str,
                    meta.get("description", ""),
                    tag_str
                )
            else:
                table.add_row(
                    meta["name"],
                    meta["category"],
                    meta["updated_at"].split("T")[0],  # Just show date part
                    size_str
                )
        
        # Print table
        console.print(table)
        
        # Show count
        typer.echo(f"\nTotal states: {len(states)}")

@state_app.command("load")
@with_explanation("Load a saved assistant state with its full context.")
def load_state(
    name: str = typer.Argument(..., help="Name of the state to load"),
    include_history: bool = typer.Option(False, help="Include conversation history if available"),
    merge: bool = typer.Option(False, help="Merge with current context instead of replacing"),
    shared: bool = typer.Option(False, help="Load from shared states")
):
    """
    Load a saved assistant state with its full context.
    
    This restores the assistant to the exact state that was saved.
    """
    # Generate state file path
    state_path = get_state_path(name, shared)
    
    # Check for compressed version if regular doesn't exist
    if not state_path.exists():
        compressed_path = Path(str(state_path) + ".gz")
        if compressed_path.exists():
            state_path = compressed_path
        else:
            typer.echo(f"Error: State '{name}' not found.")
            raise typer.Exit(code=1)
    
    # Load state
    state = load_state_file(state_path)
    
    # Apply state to current session
    if merge:
        # Merge context - would add to current rather than replace
        typer.echo(f"Merging state '{name}' with current context...")
        # Implementation would merge _current_context with state["context"]
    else:
        # Replace context entirely
        typer.echo(f"Loading state '{name}'...")
        # Implementation would replace _current_context with state["context"]
    
    # In a real implementation, this would now apply the state to the assistant
    global _current_context, _current_config
    _current_context = state["context"].copy()
    _current_config = state["configuration"].copy()
    
    typer.echo(f"✓ State loaded: {name}" + (" (shared)" if shared else ""))
    
    # Show a summary of what was loaded
    meta = state["metadata"]
    typer.echo(f"\nState information:")
    typer.echo(f"  Name: {meta['name']}")
    typer.echo(f"  Category: {meta['category']}")
    typer.echo(f"  Last updated: {meta['updated_at']}")
    if meta.get('description'):
        typer.echo(f"  Description: {meta['description']}")
    
    # Show context summary
    context = state["context"]
    typer.echo(f"\nContext loaded:")
    typer.echo(f"  Documents: {len(context['documents'])}")
    typer.echo(f"  Codebase root: {context['codebase']['root']}")
    typer.echo(f"  Memory categories: {', '.join(context['memory_state']['categories'])}")
    
    # Show chat history status
    if include_history and "chat_history" in context:
        typer.echo(f"\nChat history loaded: {len(context['chat_history'].get('key_points', []))} key points")

@state_app.command("update")
@with_explanation("Update an existing assistant state with current context.")
def update_state(
    name: str = typer.Argument(..., help="Name of the state to update"),
    description: Optional[str] = typer.Option(None, help="Update description"),
    category: Optional[str] = typer.Option(None, help="Update category"),
    tags: Optional[str] = typer.Option(None, help="Update tags (comma-separated)"),
    context_only: bool = typer.Option(False, help="Only update context, not metadata"),
    shared: bool = typer.Option(False, help="Update a shared state")
):
    """
    Update an existing assistant state with the current context.
    
    This preserves metadata while updating context and configuration.
    """
    # Generate state file path
    state_path = get_state_path(name, shared)
    
    # Check for compressed version if regular doesn't exist
    if not state_path.exists():
        compressed_path = Path(str(state_path) + ".gz")
        if compressed_path.exists():
            state_path = compressed_path
        else:
            typer.echo(f"Error: State '{name}' not found.")
            raise typer.Exit(code=1)
    
    # Load existing state
    state = load_state_file(state_path)
    
    # Update metadata if not context_only
    if not context_only:
        if description is not None:
            state["metadata"]["description"] = description
        
        if category is not None:
            state["metadata"]["category"] = category
            
        if tags is not None:
            state["metadata"]["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
    
    # Update context and configuration from current session
    state["context"] = _current_context.copy()
    state["configuration"] = _current_config.copy()
    
    # Update timestamp
    state["metadata"]["updated_at"] = datetime.now().isoformat()
    
    # Save updated state
    save_state_file(state_path, state, state_path.name.endswith(".gz"))
    
    typer.echo(f"✓ State updated: {name}" + (" (shared)" if shared else ""))

@state_app.command("info")
@with_explanation("Show detailed information about a saved state.")
def state_info(
    name: str = typer.Argument(..., help="Name of the state to show info for"),
    format: str = typer.Option("text", help="Output format (text or json)"),
    shared: bool = typer.Option(False, help="Show info for a shared state")
):
    """
    Show detailed information about a saved assistant state.
    """
    # Generate state file path
    state_path = get_state_path(name, shared)
    
    # Check for compressed version if regular doesn't exist
    if not state_path.exists():
        compressed_path = Path(str(state_path) + ".gz")
        if compressed_path.exists():
            state_path = compressed_path
        else:
            typer.echo(f"Error: State '{name}' not found.")
            raise typer.Exit(code=1)
    
    # Load state
    state = load_state_file(state_path)
    
    if format == "json":
        # Add file info
        state["_file_info"] = {
            "path": str(state_path),
            "size": state_path.stat().st_size,
            "compressed": state_path.name.endswith(".gz")
        }
        # Output as JSON
        typer.echo(json.dumps(state, indent=2))
    else:
        # Display formatted information
        meta = state["metadata"]
        context = state["context"]
        config = state["configuration"]
        
        typer.echo(f"State: {meta['name']}" + (" (shared)" if shared else ""))
        typer.echo("=" * (len(meta['name']) + 7 + (9 if shared else 0)))
        typer.echo(f"Category: {meta['category']}")
        typer.echo(f"Created: {meta['created_at']}")
        typer.echo(f"Updated: {meta['updated_at']}")
        typer.echo(f"Version: {meta['version']}")
        typer.echo(f"Tags: {', '.join(meta.get('tags', []))}" if meta.get('tags') else "Tags: None")
        if meta.get('description'):
            typer.echo(f"\nDescription:\n{meta['description']}")
        
        typer.echo(f"\nFile Information:")
        typer.echo(f"  Path: {state_path}")
        typer.echo(f"  Size: {state_path.stat().st_size / 1024:.1f} KB")
        typer.echo(f"  Compressed: {state_path.name.endswith('.gz')}")
        
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
        typer.echo(f"  Parameters:")
        for k, v in config['parameters'].items():
            typer.echo(f"    - {k}: {v}")
        typer.echo(f"  Extensions:")
        for ext in config['extensions']:
            typer.echo(f"    - {ext}")
        if config.get('instructions'):
            if isinstance(config['instructions'], str):
                preview = config['instructions'][:50] + "..." if len(config['instructions']) > 50 else config['instructions']
                typer.echo(f"  Instructions: {preview}")
            else:
                typer.echo(f"  Instructions: {config['instructions'].get('file', 'Custom instructions')}")

@state_app.command("delete")
@with_explanation("Delete a saved assistant state.")
def delete_state(
    name: str = typer.Argument(..., help="Name of the state to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Delete without confirmation"),
    shared: bool = typer.Option(False, help="Delete a shared state")
):
    """
    Delete a saved assistant state.
    
    Removes the state file from the system.
    """
    # Generate state file path
    state_path = get_state_path(name, shared)
    
    # Check for compressed version if regular doesn't exist
    if not state_path.exists():
        compressed_path = Path(str(state_path) + ".gz")
        if compressed_path.exists():
            state_path = compressed_path
        else:
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
    
    typer.echo(f"✓ State deleted: {name}" + (" (shared)" if shared else ""))

@state_app.command("copy")
@with_explanation("Copy a state to a new name.")
def copy_state(
    source: str = typer.Argument(..., help="Source state name"),
    target: str = typer.Argument(..., help="Target state name"),
    source_shared: bool = typer.Option(False, "--source-shared", help="Source is a shared state"),
    target_shared: bool = typer.Option(False, "--target-shared", help="Target should be a shared state"),
    overwrite: bool = typer.Option(False, help="Overwrite target if it exists")
):
    """
    Copy an existing state to a new name.
    
    This creates a duplicate state with a new name.
    """
    # Generate state file paths
    source_path = get_state_path(source, source_shared)
    target_path = get_state_path(target, target_shared)
    
    # Check for compressed version if regular doesn't exist
    if not source_path.exists():
        compressed_path = Path(str(source_path) + ".gz")
        if compressed_path.exists():
            source_path = compressed_path
        else:
            typer.echo(f"Error: Source state '{source}' not found.")
            raise typer.Exit(code=1)
    
    # Check if target exists
    if target_path.exists() and not overwrite:
        typer.echo(f"Error: Target state '{target}' already exists. Use --overwrite to replace it.")
        raise typer.Exit(code=1)
    
    # Load source state
    state = load_state_file(source_path)
    
    # Update metadata for the copy
    state["metadata"]["name"] = target
    state["metadata"]["created_at"] = datetime.now().isoformat()
    state["metadata"]["updated_at"] = datetime.now().isoformat()
    
    # Save to target location
    save_state_file(target_path, state, source_path.name.endswith(".gz"))
    
    typer.echo(f"✓ State copied: {source} → {target}")
    if source_shared != target_shared:
        typer.echo(f"  Converted: {'shared → local' if source_shared else 'local → shared'}")

@state_app.command("export")
@with_explanation("Export a state to a file.")
def export_state(
    name: str = typer.Argument(..., help="Name of the state to export"),
    path: str = typer.Argument(..., help="Export destination path"),
    format: str = typer.Option("json", help="Export format (json or yaml)"),
    shared: bool = typer.Option(False, help="Export a shared state")
):
    """
    Export a state to a file in JSON or YAML format.
    
    This allows sharing states or backing them up.
    """
    # Generate state file path
    state_path = get_state_path(name, shared)
    
    # Check for compressed version if regular doesn't exist
    if not state_path.exists():
        compressed_path = Path(str(state_path) + ".gz")
        if compressed_path.exists():
            state_path = compressed_path
        else:
            typer.echo(f"Error: State '{name}' not found.")
            raise typer.Exit(code=1)
    
    # Load state
    state = load_state_file(state_path)
    
    # Add file info
    state["_export_info"] = {
        "exported_at": datetime.now().isoformat(),
        "exported_by": os.environ.get("USER", "unknown"),
        "original_path": str(state_path)
    }
    
    # Export to specified format
    export_path = Path(path)
    if format.lower() == "yaml":
        with open(export_path, 'w') as f:
            yaml.dump(state, f, sort_keys=False)
    else:
        with open(export_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    typer.echo(f"✓ State exported: {name} → {export_path}")
    typer.echo(f"  Format: {format.lower()}")
    typer.echo(f"  Size: {export_path.stat().st_size / 1024:.1f} KB")

@state_app.command("import")
@with_explanation("Import a state from a file.")
def import_state(
    path: str = typer.Argument(..., help="Path to the state file to import"),
    name: Optional[str] = typer.Argument(None, help="Name for the imported state (default: use name in file)"),
    shared: bool = typer.Option(False, help="Import as a shared state"),
    overwrite: bool = typer.Option(False, help="Overwrite existing state"),
    compress: bool = typer.Option(False, help="Compress the imported state")
):
    """
    Import a state from a JSON or YAML file.
    
    This allows using states created elsewhere.
    """
    # Load the import file
    import_path = Path(path)
    if not import_path.exists():
        typer.echo(f"Error: Import file not found: {import_path}")
        raise typer.Exit(code=1)
    
    # Detect format and load
    if import_path.suffix.lower() in (".yaml", ".yml"):
        with open(import_path, 'r') as f:
            state = yaml.safe_load(f)
    else:
        with open(import_path, 'r') as f:
            state = json.load(f)
    
    # Determine state name
    if name is None:
        if "metadata" in state and "name" in state["metadata"]:
            name = state["metadata"]["name"]
        else:
            name = import_path.stem
    
    # Update metadata
    state["metadata"]["name"] = name
    state["metadata"]["imported_at"] = datetime.now().isoformat()
    if "_export_info" in state:
        state["metadata"]["imported_from"] = state["_export_info"]
        del state["_export_info"]
    
    # Generate target path
    target_path = get_state_path(name, shared)
    
    # Check if target exists
    if target_path.exists() and not overwrite:
        typer.echo(f"Error: State '{name}' already exists. Use --overwrite to replace it.")
        raise typer.Exit(code=1)
    
    # Save the state
    save_state_file(target_path, state, compress)
    
    typer.echo(f"✓ State imported: {import_path} → {name}" + (" (shared)" if shared else ""))
    if compress:
        typer.echo("  Compressed: Yes")

# Add the 'with' command for quick access
@state_app.command("with")
@with_explanation("Start a session with a specific assistant state.")
def with_state(
    name: str = typer.Argument(..., help="Name of the state to use"),
    shared: bool = typer.Option(False, help="Use a shared state")
):
    """
    Start a new session with the specified assistant state.
    
    This is a convenience shortcut for 'load' that also starts a session.
    """
    # First load the state
    load_state(name, shared=shared)
    
    # Then start a session with this state
    # In a real implementation, this would launch the assistant with the loaded state
    typer.echo(f"\nStarting session with state '{name}'...")
    
    # Placeholder for actual session launch
    typer.echo("Session started!")
```

### Integration into Main Application

```python
# src/skogcli/__init__.py

from .state import state_app

# Add the state app
app.add_typer(state_app, name="state")

# Add shorthand for 'with' command
@app.command("with")
def with_state_shorthand(
    name: str,
    shared: bool = typer.Option(False, help="Use a shared state")
):
    """Start a session with a specific assistant state."""
    from .state import with_state
    with_state(name, shared)
```

## User Experience Examples

### Typical Workflows

#### Development Workflow

```bash
# Morning routine - load development context
$ skogcli with skogcli-dev
✓ State loaded: skogcli-dev
Starting session with state 'skogcli-dev'...

# After making significant progress
$ skogcli state update skogcli-dev
✓ State updated: skogcli-dev
```

#### Context Switching

```bash
# Working on different modules
$ skogcli with memory-integration
✓ State loaded: memory-integration
Starting session with state 'memory-integration'...

# Later, switch to documentation
$ skogcli with documentation
✓ State loaded: documentation
Starting session with state 'documentation'...
```

#### Creating Specialized Assistants

```bash
# Create a code review assistant
$ skogcli state save code-reviewer --category specialized --description "Assistant for code review tasks" --tags "review,code,quality"
✓ State saved: code-reviewer

# Create an architecture planning assistant
$ skogcli state save architect --category specialized --description "Assistant for architecture planning" --tags "architecture,design,planning"
✓ State saved: architect
```

#### Project Management

```bash
# List all available project contexts
$ skogcli state list --category projects --details
[Table output with project states]

# Get details on a specific context
$ skogcli state info skogcli-dev
[Detailed information about the state]
```

### Import/Export Flow

```bash
# Export state for sharing
$ skogcli state export skogcli-dev ./exports/skogcli-dev.yaml --format yaml
✓ State exported: skogcli-dev → ./exports/skogcli-dev.yaml

# Import on another system
$ skogcli state import ./imports/skogcli-dev.yaml
✓ State imported: ./imports/skogcli-dev.yaml → skogcli-dev
```

### Managing Shared States

```bash
# Create a shared state for team use
$ skogcli state save team-workflow --shared
✓ State saved: team-workflow (shared)

# List shared states
$ skogcli state list --shared
[Table of shared states]

# Use a shared state
$ skogcli with team-workflow --shared
✓ State loaded: team-workflow (shared)
```

## Advanced Features for Future Versions

### 1. State Version Control

```bash
# List versions of a state
$ skogcli state versions skogcli-dev
[List of historical versions]

# Restore a previous version
$ skogcli state restore skogcli-dev --version 2023-04-13T14:30:00Z
✓ Restored version from 2023-04-13T14:30:00Z
```

### 2. Differential Updates

```bash
# Update only specific aspects
$ skogcli state patch skogcli-dev --context-only
✓ Context patched: skogcli-dev

# Show differences between versions
$ skogcli state diff skogcli-dev --with-version 2023-04-12T15:00:00Z
[Shows differences between current and specific version]
```

### 3. State Composition

```bash
# Merge multiple states
$ skogcli state compose new-state --from base-state --with code-context --with documentation-context
✓ Composed state created: new-state

# Create a state from multiple components
$ skogcli state assemble fullstack-dev --components frontend-dev,backend-dev,database-dev
✓ Assembled state created: fullstack-dev
```

### 4. State Testing

```bash
# Validate a state
$ skogcli state validate skogcli-dev
✓ State validation passed: All resources accessible

# Test state functionality
$ skogcli state test skogcli-dev
Running test queries...
✓ Test passed: 5/5 test queries successful
```

## Benefits and ROI

1. **Time Savings**
   - Eliminates 5-10 minutes of context building per session
   - In a typical work week (5 sessions): 25-50 minutes saved
   - For a team of 5 developers: 2-4 hours saved weekly

2. **Context Quality**
   - Ensures complete and consistent context
   - Prevents knowledge gaps in repeated interactions
   - Improves assistant response accuracy

3. **Workflow Integration**
   - Seamlessly fits into existing CLI workflows
   - Enables task-specific AI assistance
   - Supports shared states for team collaboration

4. **Knowledge Management**
   - Preserves valuable project context
   - Provides historical snapshots of project understanding
   - Reduces knowledge loss during context switches

## Compatibility Considerations

1. **Model Compatibility**
   - States should track which model they were created with
   - Warning system for loading states with different models
   - Context truncation for smaller context window models

2. **Extension Compatibility**
   - Check and warn about missing extensions
   - Graceful degradation for unavailable tools

3. **Cross-Platform Support**
   - Path normalization for Windows/Unix compatibility
   - Encoding consistency for international characters

4. **Version Migration**
   - Schema evolution support
   - Upgrade paths for older state formats

## Conclusion

The Preset States feature provides a powerful mechanism for preserving and transferring AI assistant context across sessions. It transforms SkogCLI from a session-based tool to a persistent AI partner with specialized knowledge domains that can be instantly accessed.

This implementation plan provides a comprehensive approach to building this feature with a focus on usability, efficiency, and extensibility.