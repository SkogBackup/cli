import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .settings import get_setting

# Create the CLI app with consistent settings
memory_app = typer.Typer(
    help="Knowledge management for SkogAI agents and their shared memories",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


def get_activity_types() -> List[str]:
    """Get a list of activity types for completion.

    Returns:
        List[str]: List of valid activity types
    """
    return ["entity", "observation", "relation", "note", "file"]


def get_timeframe_options() -> List[str]:
    """Get a list of common timeframe options for completion.

    Returns:
        List[str]: List of valid timeframe strings
    """
    return [
        # Short-term
        "15m",
        "30m",
        "1h",
        "6h",
        "12h",
        "24h",
        # Days
        "2d",
        "3d",
        "1w",
        "2w",
        "3w",
        # Months
        "1m",
        "3m",
        "6m",
        # Years
        "1y",
        "2y",
        # Special
        "today",
        "yesterday",
        "this-week",
        "this-month",
        "this-year",
        "all",
    ]


def get_memory_folders() -> List[str]:
    """Get a list of memory folders for completion."""
    try:
        result = run_skogai_memory(["tool", "list-folders", "--format", "json"])
        if result.returncode == 0:
            folders_data = json.loads(result.stdout)
            return [folder["name"] for folder in folders_data.get("folders", [])]
    except (json.JSONDecodeError, subprocess.SubprocessError):
        pass

    # Fallback to hardcoded list
    return ["notes", "meetings", "projects", "ideas", "research", "journal"]


def get_memory_projects() -> List[str]:
    """Get a list of memory projects for completion."""
    try:
        result = run_skogai_memory(["tool", "list-projects", "--format", "json"])
        if result.returncode == 0:
            projects_data = json.loads(result.stdout)
            return [project["name"] for project in projects_data.get("projects", [])]
    except (json.JSONDecodeError, subprocess.SubprocessError):
        pass

    # Fallback to settings and defaults
    projects = ["default"]
    default_project = get_setting("memory.default_project")
    if default_project and default_project not in projects:
        projects.append(default_project)
    return projects


def run_skogai_memory(args: List[str]) -> subprocess.CompletedProcess:
    """Run skogai-memory with the given arguments.

    Args:
        args: List of command line arguments to pass to skogai-memory

    Returns:
        subprocess.CompletedProcess: The result of the command execution

    Raises:
        typer.Exit: If skogai-memory is not found or command fails
    """
    cmd = ["skogai-memory"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,  # We'll handle non-zero return codes manually
        )
        return result
    except FileNotFoundError:
        console.print(
            "[red]Error:[/] skogai-memory not found. Please install it with 'uv add skogai-memory'",
            style="bold",
        )
        raise typer.Exit(code=1)
    except subprocess.SubprocessError as e:
        console.print(f"[red]Error running skogai-memory:[/] {str(e)}", style="bold")
        raise typer.Exit(code=1)


@memory_app.callback(invoke_without_command=True, no_args_is_help=True)
def memory_callback():
    """Knowledge management powered by skogai-memory.

    This CLI provides commands to manage and interact with your knowledge base.
    """
    pass


@memory_app.command(
    name="create",
    no_args_is_help=True,
    help="Create or update a note in your knowledge base.",
    short_help="Create or update a note",
)
@memory_app.command(name="write", hidden=True)  # Alias for create
@memory_app.command(name="add", hidden=True)  # Another alias
@memory_app.command(name="new", hidden=True)  # One more alias
def create(
    title: str = typer.Argument(
        ...,
        help="Title of the note",
        show_default=False,
    ),
    folder: str = typer.Argument(
        ...,
        help="Folder to create the note in",
        autocompletion=get_memory_folders,
        show_default=False,
    ),
    content: Optional[str] = typer.Option(
        None,
        "--content",
        "-c",
        help="Note content (if not provided, read from stdin)",
        show_default=False,
    ),
    tags: Optional[str] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Tags to apply to the note (comma-separated)",
        show_default=False,
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to use",
        autocompletion=get_memory_projects,
        show_default=False,
    ),
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
        result = run_skogai_memory(cmd + ["--content", content])
    else:
        # Read from stdin
        typer.echo("Enter note content (Ctrl+D to finish):")
        from_stdin = typer.get_text_stream("stdin").read()
        result = run_skogai_memory(cmd + ["--content", from_stdin])

    if result.returncode == 0:
        typer.echo(f"✓ Note saved: {title} in {folder}")
        return 0  # Ensure the command returns 0
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(
    name="write",
    no_args_is_help=True,
    help="Create or update a note in your knowledge base.",
)
def write(
    title: str = typer.Argument(..., help="Title of the note"),
    folder: str = typer.Argument(
        ..., help="Folder to create the note in", autocompletion=get_memory_folders
    ),
    content: Optional[str] = typer.Option(
        None, "--content", "-c", help="Note content (if not provided, read from stdin)"
    ),
    tags: Optional[str] = typer.Option(
        None, "--tags", "-t", help="Tags to apply to the note (comma-separated)"
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to use",
        autocompletion=get_memory_projects,
    ),
):
    """
    Create or update a note in your knowledge base.

    This is an alias for the 'create' command.

    Examples:

    Create from argument:
      skogcli memory write "My Idea" notes --content "# My Idea\n\nThis is a great idea."

    Create from stdin:
      echo "# My Idea\n\nThis is a great idea." | skogcli memory write "My Idea" notes

    Create with tags:
      skogcli memory write "Meeting Notes" meetings --tags "work,important,2025"
    """
    cmd = ["tool", "write-note", "--title", title, "--folder", folder]
    if tags:
        cmd.extend(["--tags", tags])

    if project:
        cmd = ["--project", project] + cmd

    if content:
        result = run_skogai_memory(cmd + ["--content", content])
    else:
        # Read from stdin
        typer.echo("Enter note content (Ctrl+D to finish):")
        from_stdin = typer.get_text_stream("stdin").read()
        result = run_skogai_memory(cmd + ["--content", from_stdin])

    if result.returncode == 0:
        typer.echo(f"✓ Note saved: {title} in {folder}")
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


def get_note_identifiers() -> List[str]:
    """Get a list of note identifiers for completion.

    Returns:
        List[str]: List of note identifiers in the format 'folder/title'
    """
    try:
        result = run_skogai_memory(
            [
                "tool",
                "recent-notes",
                "--format",
                "json",
                "--limit",
                "20",
            ]  # Increased limit for better UX
        )
        if result.returncode == 0:
            import json

            notes_data = json.loads(result.stdout)
            identifiers = []
            for note in notes_data.get("notes", []):
                # Add both permalink and title as possible identifiers
                if "permalink" in note:
                    identifiers.append(note["permalink"])
                if "title" in note:
                    identifiers.append(note["title"])
            # Add special identifiers
            identifiers.extend(["latest", "recent"])
            return identifiers
    except Exception:
        pass

    # Fallback to hardcoded list
    return ["latest", "recent", "last-meeting", "project-ideas", "todo"]


@memory_app.command(
    name="read",
    no_args_is_help=True,
    help="Read a note from your knowledge base.",
    short_help="Read a note by its identifier",
)
@memory_app.command(name="show", hidden=True)  # Alias for read
def read(
    identifier: str = typer.Argument(
        ...,
        help="Note identifier in format 'folder/title' or just 'title' to search in all folders",
        autocompletion=get_note_identifiers,
        show_default=False,
    ),
    page: int = typer.Option(
        1,
        "--page",
        "-p",
        min=1,
        help="Page number for pagination",
        show_default=True,
    ),
    page_size: int = typer.Option(
        10,
        "--page-size",
        "-s",
        min=1,
        max=100,
        help="Number of items per page",
        show_default=True,
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-P",
        help="Specific project to use",
        autocompletion=get_memory_projects,
        show_default=False,
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        "-r",
        help="Display raw markdown without rich formatting",
        show_default=True,
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save note content to a file instead of displaying it",
        show_default=False,
    ),
):
    """
    Read a note from your knowledge base.

    Examples:

    Read a note by identifier:
      skogcli memory read "My Note"

    Read a note from a specific project:
      skogcli memory read "My Note" --project my-project

    Display raw markdown:
      skogcli memory read "My Note" --raw

    Save note content to a file:
      skogcli memory read "My Note" --output note.md
    """
    cmd = [
        "tool",
        "read-note",
        identifier,
        "--page",
        str(page),
        "--page-size",
        str(page_size),
    ]
    if project:
        cmd = ["--project", project] + cmd

    result = run_skogai_memory(cmd)

    if result.returncode == 0:
        if raw:
            # Display raw markdown
            if output_file:
                output_file.write_text(result.stdout)
            else:
                typer.echo(result.stdout)
        else:
            try:
                # Try to parse the JSON output for better formatting
                import json

                data = json.loads(result.stdout)

                # Extract the content if available
                if "content" in data:
                    content = data["content"]
                    console.print(Markdown(content))

                    # Print metadata
                    console.print("\n[bold cyan]Metadata:[/bold cyan]")
                    if "title" in data:
                        console.print(f"[bold]Title:[/bold] {data['title']}")
                    if "file_path" in data:
                        console.print(f"[bold]Path:[/bold] {data['file_path']}")
                    if "created_at" in data:
                        console.print(
                            f"[bold]Created:[/bold] {data['created_at'].split('.')[0]}"
                        )
                    if "updated_at" in data:
                        console.print(
                            f"[bold]Updated:[/bold] {data['updated_at'].split('.')[0]}"
                        )
                else:
                    # If no content field, just render the whole output as markdown
                    console.print(Markdown(result.stdout))
            except (json.JSONDecodeError, KeyError):
                # Fallback to rendering the whole output as markdown
                console.print(Markdown(result.stdout))
        return 0  # Ensure the command returns 0
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(
    name="search",
    no_args_is_help=True,
    help="Search across your knowledge base for specific content.",
    short_help="Search notes by content or metadata",
)
@memory_app.command(name="find", hidden=True)  # Alias for search
def search(
    query: str = typer.Argument(
        ...,
        help="Search query (supports simple text or regex with --regex flag)",
        show_default=False,
    ),
    permalink: bool = typer.Option(
        False,
        "--permalink/--no-permalink",
        help="Search only in permalink values",
        show_default=True,
    ),
    title: bool = typer.Option(
        False,
        "--title/--no-title",
        help="Search only in title values",
        show_default=True,
    ),
    after_date: Optional[str] = typer.Option(
        None,
        "--after-date",
        "-a",
        help="Filter results after this date (e.g., '2d', '1 week', '2023-01-01')",
        show_default=False,
    ),
    before_date: Optional[str] = typer.Option(
        None,
        "--before-date",
        "-b",
        help="Filter results before this date",
        show_default=False,
    ),
    page: int = typer.Option(
        1,
        "--page",
        "-p",
        min=1,
        help="Page number for pagination",
        show_default=True,
    ),
    page_size: int = typer.Option(
        10,
        "--page-size",
        "-s",
        min=1,
        max=100,
        help="Number of items per page",
        show_default=True,
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-P",
        help="Specific project to search in",
        autocompletion=get_memory_projects,
        show_default=False,
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (table, json, markdown)",
        show_default=True,
    ),
):
    """
    Search across your knowledge base for specific content.

    Examples:

    Basic search:
      skogcli memory search "project ideas"

    Search only titles:
      skogcli memory search "meeting" --title

    Search with date filter:
      skogcli memory search "important" --after-date "1 week"

    Search with regex:
      skogcli memory search "regex:project.*ideas"

    Display results in JSON:
      skogcli memory search "project ideas" --format json
    """
    cmd = [
        "tool",
        "search-notes",
        query,
        "--page",
        str(page),
        "--page-size",
        str(page_size),
    ]

    if permalink:
        cmd.append("--permalink")
    if title:
        cmd.append("--title")
    if after_date:
        cmd.extend(["--after_date", after_date])
    if before_date:
        cmd.extend(["--before_date", before_date])

    if project:
        cmd = ["--project", project] + cmd

    result = run_skogai_memory(cmd)

    if result.returncode == 0:
        if output_format == "json":
            # Display raw JSON output
            typer.echo(result.stdout)
        elif output_format == "markdown":
            # Render the output as markdown
            console.print(Markdown(result.stdout))
        else:
            try:
                # Try to parse the JSON output for better formatting
                import json

                data = json.loads(result.stdout)

                # Create a table for the results
                from rich.table import Table

                table = Table(title=f"Search Results: '{query}'")

                # Add columns
                table.add_column("Type", style="cyan")
                table.add_column("Title", style="green")
                table.add_column("Created At", style="yellow")
                table.add_column("Path", style="blue")

                # Add rows
                for item in data.get("results", []):
                    table.add_row(
                        item.get("type", ""),
                        item.get("title", ""),
                        (
                            item.get("created_at", "").split(".")[0]
                            if item.get("created_at")
                            else ""
                        ),
                        item.get("file_path", ""),
                    )

                # Print the table
                console.print(table)

                # Show metadata
                total_results = len(data.get("results", []))
                current_page = data.get("current_page", 1)
                page_size = data.get("page_size", 10)
                total_pages = (
                    (total_results + page_size - 1) // page_size
                    if total_results > 0
                    else 0
                )

                console.print(f"\nTotal results: {total_results}")
                console.print(f"Page {current_page} of {total_pages}")

            except (json.JSONDecodeError, KeyError):
                # Fallback to rendering the whole output as markdown
                console.print(Markdown(result.stdout))
        return 0  # Ensure the command returns 0
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(
    name="list",
    no_args_is_help=True,
    help="List recent activity across your knowledge base.",
    short_help="List recent notes and activity",
)
@memory_app.command(name="ls", hidden=True)  # Short alias
def list_notes(
    type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by activity type",
        autocompletion=get_activity_types,
        show_default=False,
    ),
    folder: Optional[str] = typer.Option(
        None,
        "--folder",
        "-f",
        help="Filter by folder",
        autocompletion=get_memory_folders,
        show_default=False,
    ),
    depth: int = typer.Option(
        1,
        "--depth",
        "-d",
        min=0,
        max=5,
        help="Depth of related entities to show",
        show_default=True,
    ),
    timeframe: str = typer.Option(
        "7d",
        "--timeframe",
        "-T",
        help="Time range to show (e.g., '7d', '2w', '1m')",
        autocompletion=get_timeframe_options,
        show_default=True,
    ),
    page: int = typer.Option(
        1,
        "--page",
        "-p",
        min=1,
        help="Page number for pagination",
        show_default=True,
    ),
    page_size: int = typer.Option(
        10,
        "--page-size",
        "-s",
        min=1,
        max=100,
        help="Number of items per page",
        show_default=True,
    ),
    max_related: int = typer.Option(
        5,
        "--max-related",
        "-m",
        min=0,
        help="Maximum number of related items to show per result",
        show_default=True,
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-P",
        help="Specific project to list from",
        autocompletion=get_memory_projects,
        show_default=False,
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (table, json, csv, markdown)",
        show_default=True,
    ),
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all items (ignores pagination)",
        show_default=True,
    ),
):
    """
    List recent activity across your knowledge base.

    Examples:

    List recent activity (default 7 days):
      skogcli memory list

    List specific type:
      skogcli memory list --type entity

    Custom timeframe:
      skogcli memory list --timeframe 30d

    Display results in JSON:
      skogcli memory list --format json
    """
    cmd = [
        "tool",
        "recent-activity",
        "--depth",
        str(depth),
        "--timeframe",
        timeframe,
        "--page",
        str(page),
        "--page-size",
        str(page_size),
        "--max-related",
        str(max_related),
    ]

    if type:
        cmd.extend(["--type", type])
    if folder:
        cmd.extend(["--folder", folder])

    if project:
        cmd = ["--project", project] + cmd

    result = run_skogai_memory(cmd)

    if result.returncode == 0:
        if output_format == "json":
            # Display raw JSON output
            typer.echo(result.stdout)
        elif output_format == "markdown":
            # Render the output as markdown
            console.print(Markdown(result.stdout))
        else:
            try:
                # Try to parse the JSON output for better formatting
                import json

                data = json.loads(result.stdout)

                # Create a table for the results
                from rich.table import Table

                table = Table(title=f"Recent Activity ({timeframe})")

                # Add columns
                table.add_column("Type", style="cyan")
                table.add_column("Title", style="green")
                table.add_column("Created At", style="yellow")
                table.add_column("Path", style="blue")

                # Add rows
                for item in data.get("results", []):
                    table.add_row(
                        item.get("type", ""),
                        item.get("title", ""),
                        (
                            item.get("created_at", "").split(".")[0]
                            if item.get("created_at")
                            else ""
                        ),
                        item.get("file_path", ""),
                    )

                # Print the table
                console.print(table)

                # Show metadata
                total_results = len(data.get("results", []))
                current_page = data.get("current_page", 1)
                page_size = data.get("page_size", 10)
                total_pages = (
                    (total_results + page_size - 1) // page_size
                    if total_results > 0
                    else 0
                )

                console.print(f"\nTotal results: {total_results}")
                console.print(f"Page {current_page} of {total_pages}")

            except (json.JSONDecodeError, KeyError):
                # Fallback to rendering the whole output as markdown
                console.print(Markdown(result.stdout))
        return 0  # Ensure the command returns 0
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(
    name="sync",
    no_args_is_help=True,
    help="Synchronize your knowledge files with the database.",
    short_help="Sync notes with the database",
)
def sync(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to sync",
        autocompletion=get_memory_projects,
        show_default=False,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force sync even if no changes detected",
        show_default=True,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would be synced without making changes",
        show_default=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
        show_default=True,
    ),
):
    """
    Synchronize your knowledge files with the database.

    Examples:

    Sync all projects:
      skogcli memory sync

    Sync a specific project:
      skogcli memory sync --project my-project

    Force sync:
      skogcli memory sync --force

    Dry run:
      skogcli memory sync --dry-run
    """
    cmd = ["sync"]
    if project:
        cmd = ["--project", project] + cmd

    if force:
        cmd.append("--force")
    if dry_run:
        cmd.append("--dry-run")
    if verbose:
        cmd.append("--verbose")

    result = run_skogai_memory(cmd)

    if result.returncode == 0:
        # Output the actual return from the original command
        typer.echo(result.stdout)
        return 0  # Ensure the command returns 0
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(
    name="status",
    no_args_is_help=True,
    help="Show project information and sync status.",
    short_help="Show project status and statistics",
)
@memory_app.command(name="info", hidden=True)  # Alias for status
def status(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Show status for specific project",
        autocompletion=get_memory_projects,
        show_default=False,
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (table, json, yaml)",
        show_default=True,
    ),
    show_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all projects status (if no project specified)",
        show_default=True,
    ),
    check: bool = typer.Option(
        False,
        "--check",
        "-c",
        help="Only show status code (0: success, 1: warning, 2: error)",
        show_default=True,
    ),
):
    """
    Show project information and sync status.

    Examples:

    Show status for all projects:
      skogcli memory status

    Show status for a specific project:
      skogcli memory status --project my-project

    Display results in JSON:
      skogcli memory status --format json
    Displays information about the current project, including:
    - Project name and location
    - Number of notes and entities
    - Last sync time
    - Files that need to be synchronized
    """
    cmd = ["project", "info"]

    if output_format == "json":
        cmd.append("--json")
    elif output_format == "yaml":
        cmd.append("--yaml")

    if project:
        cmd = ["--project", project] + cmd

    result = run_skogai_memory(cmd)

    if result.returncode == 0:
        if output_format in ["json", "yaml"]:
            # Just print the raw output
            typer.echo(result.stdout)
        else:
            try:
                # Try to parse the JSON output for better formatting
                import json

                data = json.loads(result.stdout)

                # Create a rich display
                from rich.panel import Panel

                # Project info section
                project_name = data.get("project_name", "default")
                project_path = data.get("project_path", "")

                console.print(
                    Panel(
                        f"[bold cyan]Project:[/bold cyan] {project_name}\n"
                        f"[bold cyan]Path:[/bold cyan] {project_path}",
                        title="Project Information",
                    )
                )

                # Stats section
                stats = data.get("stats", {})
                entities = stats.get("entities", 0)
                notes = stats.get("notes", 0)
                last_sync = stats.get("last_sync", "Never")

                console.print(
                    Panel(
                        f"[bold cyan]Entities:[/bold cyan] {entities}\n"
                        f"[bold cyan]Notes:[/bold cyan] {notes}\n"
                        f"[bold cyan]Last Sync:[/bold cyan] {last_sync}",
                        title="Statistics",
                    )
                )

                # Sync status
                sync_status = data.get("sync_status", {})
                needs_sync = sync_status.get("needs_sync", False)
                files_to_sync = sync_status.get("files_to_sync", [])

                if needs_sync:
                    console.print(
                        "[bold yellow]Files needing synchronization:[/bold yellow]"
                    )
                    for file in files_to_sync:
                        console.print(f"  • {file}")
                else:
                    console.print(
                        "[bold green]All files are synchronized.[/bold green]"
                    )

            except (json.JSONDecodeError, KeyError):
                # Fallback to raw output if JSON parsing fails
                console.print(result.stdout)
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(
    name="recent-activity",
    no_args_is_help=True,
    help="List recent activity across your knowledge base (alias for 'list').",
    short_help="Alias for 'list' command",
    hidden=True,  # Prevents showing in --help, but still usable
)
def recent_activity(
    type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by activity type",
        autocompletion=get_activity_types,
        show_default=False,
    ),
    depth: int = typer.Option(
        1,
        "--depth",
        "-d",
        min=0,
        max=5,
        help="Depth of related entities to show",
        show_default=True,
    ),
    timeframe: str = typer.Option(
        "7d",
        "--timeframe",
        "-T",
        help="Time range to show (e.g., '7d', '2w', '1m')",
        autocompletion=get_timeframe_options,
        show_default=True,
    ),
    page: int = typer.Option(
        1,
        "--page",
        "-p",
        min=1,
        help="Page number for pagination",
        show_default=True,
    ),
    page_size: int = typer.Option(
        10,
        "--page-size",
        "-s",
        min=1,
        max=100,
        help="Number of items per page",
        show_default=True,
    ),
    max_related: int = typer.Option(
        5,
        "--max-related",
        "-m",
        min=0,
        help="Maximum number of related items to show per result",
        show_default=True,
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-P",
        help="Specific project to list from",
        autocompletion=get_memory_projects,
        show_default=False,
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (table, json, csv, markdown)",
        show_default=True,
    ),
    show_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all items (ignores pagination)",
        show_default=True,
    ),
):
    """List recent activity (alias for 'list' command)."""
    # Call the list_notes function with all the same arguments
    list_notes(
        type=type,
        folder=None,  # recent-activity doesn't have a folder parameter
        depth=depth,
        timeframe=timeframe,
        page=page,
        page_size=page_size,
        max_related=max_related,
        project=project,
        output_format=output_format,
        all=show_all,
    )
