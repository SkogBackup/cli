import json
import subprocess
from pathlib import Path
from typing import Optional, List

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
    """Get a list of activity types for completion."""
    return ["entity", "observation", "relation", "note", "file"]


def get_timeframe_options() -> List[str]:
    """Get a list of common timeframe options for completion."""
    return [
        "15m",
        "30m",
        "1h",
        "6h",
        "12h",
        "24h",
        "2d",
        "3d",
        "1w",
        "2w",
        "3w",
        "1m",
        "3m",
        "6m",
        "1y",
        "2y",
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
        result = run_basic_memory(["tool", "list-folders", "--format", "json"])
        if result.returncode == 0:
            folders_data = json.loads(result.stdout)
            return [folder["name"] for folder in folders_data.get("folders", [])]
    except (json.JSONDecodeError, subprocess.SubprocessError, Exception):
        pass

    return ["notes", "meetings", "projects", "ideas", "research", "journal"]


def get_memory_projects() -> List[str]:
    """Get a list of memory projects for completion."""
    try:
        result = run_basic_memory(["tool", "list-projects", "--format", "json"])
        if result.returncode == 0:
            projects_data = json.loads(result.stdout)
            return [project["name"] for project in projects_data.get("projects", [])]
    except (json.JSONDecodeError, subprocess.SubprocessError, Exception):
        pass

    projects = ["default"]
    default_project = get_setting("memory.default_project")
    if default_project and default_project not in projects:
        projects.append(default_project)
    return projects


def run_basic_memory(args: List[str]) -> subprocess.CompletedProcess:
    """Run basic-memory with the given arguments."""
    cmd = ["uvx", "basic-memory"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result
    except FileNotFoundError:
        console.print(
            "[red]Error:[/] basic-memory not found. Please install it with 'uv add basic-memory'",
            style="bold",
        )
        raise typer.Exit(code=1)
    except subprocess.SubprocessError as e:
        console.print(f"[red]Error running basic-memory:[/] {str(e)}", style="bold")
        raise typer.Exit(code=1)


@memory_app.callback(invoke_without_command=True, no_args_is_help=True)
def memory_callback():
    """Knowledge management powered by basic-memory."""
    pass


@memory_app.command(name="bm", help="Direct passthrough to basic-memory command")
def basic_memory_passthrough(
    args: List[str] = typer.Argument(..., help="Arguments to pass to basic-memory")
):
    """Direct passthrough to basic-memory command."""
    result = run_basic_memory(args)
    if result.stdout:
        typer.echo(result.stdout)
    if result.stderr:
        typer.echo(result.stderr, err=True)
    if result.returncode != 0:
        raise typer.Exit(code=result.returncode)


@memory_app.command(
    name="write", help="Create or update a note in your knowledge base."
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
    """Create or update a note in your knowledge base."""
    cmd = ["tool", "write-note", "--title", title, "--folder", folder]
    if tags:
        cmd.extend(["--tags", tags])

    if project:
        cmd = ["--project", project] + cmd

    if content:
        result = run_basic_memory(cmd + ["--content", content])
    else:
        typer.echo("Enter note content (Ctrl+D to finish):")
        from_stdin = typer.get_text_stream("stdin").read()
        result = run_basic_memory(cmd + ["--content", from_stdin])

    if result.returncode == 0:
        typer.echo(f"✓ Note saved: {title} in {folder}")
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(name="create", help="Create or update a note")
def create(
    title: str = typer.Argument(..., help="Title of the note"),
    folder: str = typer.Argument(
        ..., help="Folder to create the note in", autocompletion=get_memory_folders
    ),
    content: Optional[str] = typer.Option(
        None, "--content", "-c", help="Note content (if not provided, read from stdin)"
    ),
    tags: Optional[str] = typer.Option(
        None, "--tag", "-t", help="Tags to apply to the note (comma-separated)"
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to use",
        autocompletion=get_memory_projects,
    ),
):
    """Create or update a note in your knowledge base."""
    # Delegate to write command
    write(title=title, folder=folder, content=content, tags=tags, project=project)


def get_note_identifiers() -> List[str]:
    """Get a list of note identifiers for completion."""
    try:
        result = run_basic_memory(
            ["tool", "recent-notes", "--format", "json", "--limit", "20"]
        )
        if result.returncode == 0:
            notes_data = json.loads(result.stdout)
            identifiers = []
            for note in notes_data.get("notes", []):
                if "permalink" in note:
                    identifiers.append(note["permalink"])
                if "title" in note:
                    identifiers.append(note["title"])
            identifiers.extend(["latest", "recent"])
            return identifiers
    except Exception:
        pass

    return ["latest", "recent", "last-meeting", "project-ideas", "todo"]


@memory_app.command(name="read", help="Read a note by its identifier")
def read(
    identifier: str = typer.Argument(
        ...,
        help="Note identifier in format 'folder/title' or just 'title' to search in all folders",
        autocompletion=get_note_identifiers,
    ),
    page: int = typer.Option(
        1, "--page", "-p", min=1, help="Page number for pagination"
    ),
    page_size: int = typer.Option(
        10, "--page-size", "-s", min=1, max=100, help="Number of items per page"
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-P",
        help="Specific project to use",
        autocompletion=get_memory_projects,
    ),
    raw: bool = typer.Option(
        False, "--raw", "-r", help="Display raw markdown without rich formatting"
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save note content to a file instead of displaying it",
    ),
):
    """Read a note from your knowledge base."""
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
            if output_file:
                output_file.write_text(result.stdout)
            else:
                typer.echo(result.stdout)
        else:
            try:
                data = json.loads(result.stdout)
                if "content" in data:
                    content = data["content"]
                    console.print(Markdown(content))

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
                    console.print(Markdown(result.stdout))
            except (json.JSONDecodeError, KeyError):
                console.print(Markdown(result.stdout))
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(name="search", help="Search notes by content or metadata")
def search(
    query: str = typer.Argument(..., help="Search query"),
    permalink: bool = typer.Option(
        False, "--permalink", help="Search only in permalink values"
    ),
    title: bool = typer.Option(False, "--title", help="Search only in title values"),
    after_date: Optional[str] = typer.Option(
        None, "--after-date", "-a", help="Filter results after this date"
    ),
    before_date: Optional[str] = typer.Option(
        None, "--before-date", "-b", help="Filter results before this date"
    ),
    page: int = typer.Option(
        1, "--page", "-p", min=1, help="Page number for pagination"
    ),
    page_size: int = typer.Option(
        10, "--page-size", "-s", min=1, max=100, help="Number of items per page"
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-P",
        help="Specific project to search in",
        autocompletion=get_memory_projects,
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json, markdown)"
    ),
):
    """Search across your knowledge base for specific content."""
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

    result = run_basic_memory(cmd)

    if result.returncode == 0:
        if output_format == "json":
            typer.echo(result.stdout)
        elif output_format == "markdown":
            console.print(Markdown(result.stdout))
        else:
            try:
                data = json.loads(result.stdout)
                from rich.table import Table

                table = Table(title=f"Search Results: '{query}'")
                table.add_column("Type", style="cyan")
                table.add_column("Title", style="green")
                table.add_column("Created At", style="yellow")
                table.add_column("Path", style="blue")

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

                console.print(table)

                results = data.get("results", [])
                total_results = len(results)
                current_page = data.get("page", 1) or data.get("current_page", 1)
                page_size = data.get("page_size", 10)
                total_pages = (
                    (total_results + page_size - 1) // page_size
                    if total_results > 0
                    else 0
                )

                console.print(f"\nTotal results: {total_results}")
                console.print(f"Page {current_page} of {total_pages}")

            except (json.JSONDecodeError, KeyError):
                console.print(Markdown(result.stdout))
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(name="list", help="List recent notes and activity")
def list_notes(
    type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by activity type",
        autocompletion=get_activity_types,
    ),
    folder: Optional[str] = typer.Option(
        None,
        "--folder",
        "-f",
        help="Filter by folder",
        autocompletion=get_memory_folders,
    ),
    depth: int = typer.Option(
        1, "--depth", "-d", min=0, max=5, help="Depth of related entities to show"
    ),
    timeframe: str = typer.Option(
        "7d",
        "--timeframe",
        "-T",
        help="Time range to show (e.g., '7d', '2w', '1m')",
        autocompletion=get_timeframe_options,
    ),
    page: int = typer.Option(
        1, "--page", "-p", min=1, help="Page number for pagination"
    ),
    page_size: int = typer.Option(
        10, "--page-size", "-s", min=1, max=100, help="Number of items per page"
    ),
    max_related: int = typer.Option(
        5,
        "--max-related",
        "-m",
        min=0,
        help="Maximum number of related items to show per result",
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-P",
        help="Specific project to list from",
        autocompletion=get_memory_projects,
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json, csv, markdown)"
    ),
):
    """List recent activity across your knowledge base."""
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

    result = run_basic_memory(cmd)

    if result.returncode == 0:
        if output_format == "json":
            typer.echo(result.stdout)
        elif output_format == "markdown":
            console.print(Markdown(result.stdout))
        else:
            try:
                data = json.loads(result.stdout)
                
                # Handle the nested structure of recent-activity results
                raw_results = data.get("results", [])
                results = []
                for item in raw_results:
                    if "primary_result" in item:
                        # Extract the primary_result which contains the actual data
                        results.append(item["primary_result"])
                    else:
                        # Fallback for other structures
                        results.append(item)
                
                # Generate markdown output
                markdown_content = f"# Recent Activity ({timeframe})\n\n"
                
                for item in results:
                    item_type = item.get("type", "")
                    title = item.get("title", "")
                    created_at = (
                        item.get("created_at", "").split(".")[0]
                        if item.get("created_at")
                        else ""
                    )
                    file_path = item.get("file_path", "")
                    
                    markdown_content += f"## {title}\n"
                    markdown_content += f"- **Type**: {item_type}\n"
                    markdown_content += f"- **Created**: {created_at}\n"
                    markdown_content += f"- **Path**: {file_path}\n\n"

                console.print(Markdown(markdown_content))

                total_results = len(results)
                current_page = data.get("page", 1) or data.get("current_page", 1)
                page_size = data.get("page_size", 10)
                total_pages = (
                    (total_results + page_size - 1) // page_size
                    if total_results > 0
                    else 0
                )

                console.print(f"\nTotal results: {total_results}")
                console.print(f"Page {current_page} of {total_pages}")

            except (json.JSONDecodeError, KeyError):
                console.print(Markdown(result.stdout))
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(name="sync", help="Sync notes with the database")
def sync(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Specific project to sync",
        autocompletion=get_memory_projects,
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force sync even if no changes detected"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would be synced without making changes",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
):
    """Synchronize your knowledge files with the database."""
    cmd = ["sync"]
    if project:
        cmd = ["--project", project] + cmd

    if force:
        cmd.append("--force")
    if dry_run:
        cmd.append("--dry-run")
    if verbose:
        cmd.append("--verbose")

    result = run_basic_memory(cmd)

    if result.returncode == 0:
        typer.echo(result.stdout)
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)


@memory_app.command(name="status", help="Show project status and statistics")
def status(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Show status for specific project",
        autocompletion=get_memory_projects,
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json, yaml)"
    ),
    show_all: bool = typer.Option(
        False, "--all", "-a", help="Show all projects status (if no project specified)"
    ),
    check: bool = typer.Option(
        False,
        "--check",
        "-c",
        help="Only show status code (0: success, 1: warning, 2: error)",
    ),
):
    """Show project information and sync status."""
    cmd = ["project", "info"]

    if output_format == "json":
        cmd.append("--json")
    elif output_format == "yaml":
        cmd.append("--yaml")

    if show_all and not project:
        projects_cmd = ["tool", "list-projects", "--format", "json"]
        projects_result = run_basic_memory(projects_cmd)

        if projects_result.returncode == 0:
            try:
                projects_data = json.loads(projects_result.stdout)
                project_list = [p["name"] for p in projects_data.get("projects", [])]

                if len(project_list) > 1:
                    console.print("[bold]Status for all projects:[/bold]\n")

                    for idx, proj in enumerate(project_list):
                        proj_cmd = cmd.copy()
                        proj_cmd = ["--project", proj] + proj_cmd
                        proj_result = run_basic_memory(proj_cmd)

                        if proj_result.returncode == 0:
                            if idx > 0:
                                console.print("\n" + "-" * 50 + "\n")
                            typer.echo(proj_result.stdout)
                        else:
                            console.print(
                                f"[red]Error getting status for project {proj}[/red]"
                            )

                    return 0
            except (json.JSONDecodeError, KeyError):
                pass

    if project:
        cmd = ["--project", project] + cmd

    result = run_basic_memory(cmd)

    if result.returncode == 0:
        if check:
            status_code = 0
            try:
                if output_format != "json":
                    json_cmd = cmd.copy()
                    if "--json" not in json_cmd:
                        json_cmd.append("--json")
                    json_result = run_basic_memory(json_cmd)
                    if json_result.returncode != 0:
                        return 2
                    data = json.loads(json_result.stdout)
                else:
                    data = json.loads(result.stdout)

                if data.get("sync_status", {}).get("needs_sync", False):
                    status_code = 1
                if "error" in data:
                    status_code = 2
            except (json.JSONDecodeError, KeyError):
                status_code = 2

            return status_code

        if output_format in ["json", "yaml"]:
            typer.echo(result.stdout)
        else:
            try:
                data = json.loads(result.stdout)

                project_name = data.get("project_name", "default")
                project_path = data.get("project_path", "")

                console.print(
                    Panel(
                        f"[bold cyan]Project:[/bold cyan] {project_name}\n"
                        f"[bold cyan]Path:[/bold cyan] {project_path}",
                        title="Project Information",
                    )
                )

                stats = data.get("statistics", {}) or data.get("stats", {})
                entities = stats.get("total_entities", 0)
                notes = stats.get("entity_types", {}).get("note", 0)
                observations = stats.get("total_observations", 0)
                relations = stats.get("total_relations", 0)

                system_info = data.get("system", {})
                last_sync = system_info.get("watch_status", {}).get(
                    "last_scan", "Never"
                )

                console.print(
                    Panel(
                        f"[bold cyan]Entities:[/bold cyan] {entities}\n"
                        f"[bold cyan]Notes:[/bold cyan] {notes}\n"
                        f"[bold cyan]Observations:[/bold cyan] {observations}\n"
                        f"[bold cyan]Relations:[/bold cyan] {relations}\n"
                        f"[bold cyan]Last Sync:[/bold cyan] {last_sync}",
                        title="Statistics",
                    )
                )

                watch_status = data.get("system", {}).get("watch_status", {})
                needs_sync = False
                files_to_sync = []

                recent_events = watch_status.get("recent_events", [])
                if recent_events:
                    needs_sync = True
                    files_to_sync = [event.get("path", "") for event in recent_events]

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
                console.print(result.stdout)
    else:
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)
