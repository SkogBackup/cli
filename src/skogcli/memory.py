import typer
import subprocess
from typing import Optional, List, Callable
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

@memory_app.command("write")
@with_explanation("Create or update a note in your knowledge base (alias for create).")
def write(
    title: str = typer.Argument(..., help="Title of the note"),
    folder: str = typer.Argument(..., help="Folder to create the note in"),
    content: Optional[str] = typer.Option(None, "--content", "-c", help="Note content (if not provided, read from stdin)"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Tags to apply to the note (comma-separated)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Specific project to use"),
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
