import typer
from typing import Optional, List, Annotated
from enum import Enum
import rich
from rich.console import Console
from rich.table import Table

# Configure context settings for help options
context_settings = {
    "help_option_names": ["--help", "-h"],
}

# Create app with no_args_is_help=True to show help on empty calls
app = typer.Typer(
    context_settings=context_settings,
    no_args_is_help=True,
    help="SkogCLI - A demonstration of Typer capabilities"
)

# Create a console for rich output
console = Console()

# Create an enum for command choices
class Format(str, Enum):
    JSON = "json"
    TEXT = "text"
    TABLE = "table"

@app.command()
def hello(name: Optional[str] = typer.Argument(None, help="Name to greet")):
    """
    Say hello to someone or the world.
    """
    if name:
        typer.echo(f"Hello {name}!")
    else:
        typer.echo("Hello World!")

@app.command()
def version():
    """
    Show the current version of the application.
    """
    typer.echo("SkogCLI v0.1.0")

# Create a subcommand group
examples_app = typer.Typer(help="Example commands demonstrating Typer features", no_args_is_help=True)
app.add_typer(examples_app, name="examples")

@examples_app.command("basic")
def examples_basic(
    name: str = typer.Argument(..., help="Your name"),
    count: int = typer.Option(1, "--count", "-c", help="Number of greetings"),
    formal: bool = typer.Option(False, "--formal", "-f", help="Use formal greeting"),
):
    """Basic command with arguments and options."""
    greeting = "Hello" if not formal else "Greetings"
    for _ in range(count):
        typer.echo(f"{greeting}, {name}!")

@examples_app.command("choices")
def examples_choices(
    format: Format = typer.Option(Format.TEXT, case_sensitive=False, help="Output format"),
    items: List[str] = typer.Argument(..., help="Items to display"),
):
    """Command with enum choices and list arguments."""
    if format == Format.JSON:
        import json
        typer.echo(json.dumps({"items": items}))
    elif format == Format.TABLE:
        table = Table(title="Items")
        table.add_column("Index")
        table.add_column("Value")
        for i, item in enumerate(items):
            table.add_row(str(i), item)
        console.print(table)
    else:  # TEXT
        for i, item in enumerate(items):
            typer.echo(f"{i}: {item}")

@examples_app.command("callback")
def examples_callback(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    files: Annotated[List[str], typer.Argument(help="Files to process")] = None,
):
    """Command with callback and annotated types."""
    if verbose:
        typer.echo("Verbose mode enabled")
    
    if not files:
        typer.echo("No files provided")
        return
    
    typer.echo(f"Processing {len(files)} files:")
    for file in files:
        typer.echo(f"  - {file}")

def main() -> None:
    app()
