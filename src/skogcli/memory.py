import typer
import subprocess
from typing import Optional, List, Callable, Iterable
from rich.console import Console
from rich.markdown import Markdown
from .decorators import with_explanation
from .settings import get_setting

memory_app = typer.Typer(
    help="Knowledge management for SkogAI agents and the memories they want to share between eachother",
    no_args_is_help=True,
)


def get_memory_folders() -> List[str]:
    """Get a list of memory folders for completion."""
    # Try to get folders from basic-memory
    try:
        result = run_basic_memory(["tool", "list-folders", "--format", "json"])
        if result.returncode == 0:
            import json

            folders_data = json.loads(result.stdout)
            return [folder["name"] for folder in folders_data.get("folders", [])]
    except Exception:
        pass

    # Fallback to hardcoded list
    return ["notes", "meetings", "projects", "ideas", "research", "journal"]


def get_memory_projects() -> List[str]:
    """Get a list of memory projects for completion."""
    # Try to get projects from basic-memory
    try:
        result = run_basic_memory(["tool", "list-projects", "--format", "json"])
        if result.returncode == 0:
            import json

            projects_data = json.loads(result.stdout)
            return [project["name"] for project in projects_data.get("projects", [])]
    except Exception:
        pass

    # Fallback to settings and defaults
    default_project = get_setting("memory.default_project")
    projects = ["default"]
    if default_project and default_project not in projects:
        projects.append(default_project)
    return projects


console = Console()


def run_basic_memory(args: List[str]) -> subprocess.CompletedProcess:
    """Run basic-memory with the given arguments."""
    cmd = ["uvx", "basic-memory"] + args
    try:
        return subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        typer.echo(
            "Error: basic-memory not found. Please install it with 'uv add basic-memory'"
        )
        raise typer.Exit(code=1)


@memory_app.callback()
def memory_callback():
    """Knowledge management powered by basic-memory."""
    pass


@memory_app.command("create")
@with_explanation("Create or update a note in your knowledge base.")
def create(
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
        from_stdin = typer.get_text_stream("stdin").read()
        result = run_basic_memory(cmd + ["--content", from_stdin])

    if result.returncode == 0:
        typer.echo(f"✓ Note saved: {title} in {folder}")
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command("write")
@with_explanation("Create or update a note in your knowledge base (alias for create).")
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
        result = run_basic_memory(cmd + ["--content", content])
    else:
        # Read from stdin
        typer.echo("Enter note content (Ctrl+D to finish):")
        from_stdin = typer.get_text_stream("stdin").read()
        result = run_basic_memory(cmd + ["--content", from_stdin])

    if result.returncode == 0:
        typer.echo(f"✓ Note saved: {title} in {folder}")
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


def get_note_identifiers() -> List[str]:
    """Get a list of note identifiers for completion."""
    # Try to get recent notes from basic-memory
    try:
        result = run_basic_memory(
            ["tool", "recent-notes", "--format", "json", "--limit", "10"]
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


@memory_app.command("read")
@with_explanation("Read a note from your knowledge base.")
def read(
    identifier: str = typer.Argument(
        ..., help="Note identifier", autocompletion=get_note_identifiers
    ),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(10, "--page-size", help="Number of items per page"),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to use",
        autocompletion=get_memory_projects,
    ),
    raw: bool = typer.Option(
        False, "--raw", help="Display raw markdown without rendering"
    ),
):
    """
    Read a note from your knowledge base.

    The note will be rendered as rich markdown by default.
    Use --raw to display the unprocessed markdown.
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

    result = run_basic_memory(cmd)

    if result.returncode == 0:
        if raw:
            typer.echo(result.stdout)
        else:
            try:
                # Try to parse the JSON output
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
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command("search")
@with_explanation("Search across your knowledge base.")
def search(
    query: str = typer.Argument(..., help="Search query"),
    permalink: bool = typer.Option(
        False, "--permalink", help="Search permalink values"
    ),
    title: bool = typer.Option(False, "--title", help="Search title values"),
    after_date: Optional[str] = typer.Option(
        None, "--after-date", help="Search results after date (e.g. '2d', '1 week')"
    ),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(10, "--page-size", help="Number of items per page"),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to use",
        autocompletion=get_memory_projects,
    ),
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

    if project:
        cmd = ["--project", project] + cmd

    result = run_basic_memory(cmd)

    if result.returncode == 0:
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
                    item.get("created_at", "").split(".")[0] if item.get("created_at") else "",
                    item.get("file_path", ""),
                )

            # Print the table
            console.print(table)

            # Show metadata
            total_results = len(data.get("results", []))
            current_page = data.get("current_page", 1)
            page_size = data.get("page_size", 10)
            total_pages = (total_results + page_size - 1) // page_size if total_results > 0 else 0
            
            console.print(f"\nTotal results: {total_results}")
            console.print(f"Page {current_page} of {total_pages}")

        except (json.JSONDecodeError, KeyError):
            # Fallback to raw output if JSON parsing fails
            console.print(result.stdout)
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


def get_activity_types() -> List[str]:
    """Get a list of activity types for completion."""
    # These are the standard activity types in basic-memory
    return ["entity", "observation", "relation", "all", "note", "tag"]


def get_timeframe_options() -> List[str]:
    """Get a list of timeframe options for completion."""
    # Common timeframe options that basic-memory accepts
    return [
        "1d",
        "3d",
        "7d",
        "14d",
        "30d",
        "1w",
        "2w",
        "1m",
        "3m",
        "6m",
        "1y",
        "today",
        "yesterday",
        "this-week",
        "last-week",
        "this-month",
        "last-month",
    ]


@memory_app.command("list")
@with_explanation("List recent notes and activity in your knowledge base.")
def list_notes(
    type: Optional[str] = typer.Option(
        None,
        "--type",
        help="Activity type (entity, observation, relation)",
        autocompletion=get_activity_types,
    ),
    depth: int = typer.Option(1, "--depth", help="Depth of related entities"),
    timeframe: str = typer.Option(
        "7d",
        "--timeframe",
        help="Timeframe for recent activity (e.g., '7d', '2w')",
        autocompletion=get_timeframe_options,
    ),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(10, "--page-size", help="Number of items per page"),
    max_related: int = typer.Option(
        10, "--max-related", help="Maximum number of related items"
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to use",
        autocompletion=get_memory_projects,
    ),
    raw: bool = typer.Option(
        False, "--raw", help="Display raw JSON output without formatting"
    ),
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

    if project:
        cmd = ["--project", project] + cmd

    result = run_basic_memory(cmd)

    if result.returncode == 0:
        if raw:
            # Display raw JSON output
            typer.echo(result.stdout)
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

                # Add rows - handle both "results" (from search) and "primary_results" (from list/recent-activity)
                results = data.get("results", data.get("primary_results", []))
                for item in results:
                    table.add_row(
                        item.get("type", ""),
                        item.get("title", ""),
                        item.get("created_at", "").split(".")[0] if item.get("created_at") else "",
                        item.get("file_path", ""),
                    )

                # Print the table
                console.print(table)

                # Show metadata - handle both formats
                results = data.get("results", data.get("primary_results", []))
                metadata = data.get("metadata", {})
                
                # Get total results either from metadata or by counting
                total_results = metadata.get("total_results", len(results))
                
                # Get current page and page size
                current_page = data.get("current_page", data.get("page", 1))
                page_size = data.get("page_size", 10)
                
                # Calculate total pages
                total_pages = (total_results + page_size - 1) // page_size if total_results > 0 else 0
                
                console.print(f"\nTotal results: {total_results}")
                console.print(f"Page {current_page} of {total_pages}")

            except (json.JSONDecodeError, KeyError):
                # Fallback to raw output if JSON parsing fails
                console.print(result.stdout)
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command("sync")
@with_explanation("Synchronize your knowledge files with the database.")
def sync(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to use",
        autocompletion=get_memory_projects,
    ),
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
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to use",
        autocompletion=get_memory_projects,
    ),
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


@memory_app.command("recent-activity")
@with_explanation(
    "List recent notes and activity in your knowledge base (alias for list)."
)
def recent_activity(
    type: Optional[str] = typer.Option(
        None,
        "--type",
        help="Activity type (entity, observation, relation)",
        autocompletion=get_activity_types,
    ),
    depth: int = typer.Option(1, "--depth", help="Depth of related entities"),
    timeframe: str = typer.Option(
        "7d",
        "--timeframe",
        help="Timeframe for recent activity (e.g., '7d', '2w')",
        autocompletion=get_timeframe_options,
    ),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(10, "--page-size", help="Number of items per page"),
    max_related: int = typer.Option(
        10, "--max-related", help="Maximum number of related items"
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to use",
        autocompletion=get_memory_projects,
    ),
    raw: bool = typer.Option(
        False, "--raw", help="Display raw JSON output without formatting"
    ),
):
    """
    List recent activity across your knowledge base.

    This is an alias for the 'list' command.

    Examples:

    List recent activity (default 7 days):
      skogcli memory recent-activity

    List specific type:
      skogcli memory recent-activity --type entity

    Custom timeframe:
      skogcli memory recent-activity --timeframe 30d
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

    if project:
        cmd = ["--project", project] + cmd

    result = run_basic_memory(cmd)

    if result.returncode == 0:
        if raw:
            # Display raw JSON output
            typer.echo(result.stdout)
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

                # Add rows - handle both "results" (from search) and "primary_results" (from list/recent-activity)
                results = data.get("results", data.get("primary_results", []))
                for item in results:
                    table.add_row(
                        item.get("type", ""),
                        item.get("title", ""),
                        item.get("created_at", "").split(".")[0] if item.get("created_at") else "",
                        item.get("file_path", ""),
                    )

                # Print the table
                console.print(table)

                # Show metadata - handle both formats
                results = data.get("results", data.get("primary_results", []))
                metadata = data.get("metadata", {})
                
                # Get total results either from metadata or by counting
                total_results = metadata.get("total_results", len(results))
                
                # Get current page and page size
                current_page = data.get("current_page", data.get("page", 1))
                page_size = data.get("page_size", 10)
                
                # Calculate total pages
                total_pages = (total_results + page_size - 1) // page_size if total_results > 0 else 0
                
                console.print(f"\nTotal results: {total_results}")
                console.print(f"Page {current_page} of {total_pages}")

            except (json.JSONDecodeError, KeyError):
                # Fallback to raw output if JSON parsing fails
                console.print(result.stdout)
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)
