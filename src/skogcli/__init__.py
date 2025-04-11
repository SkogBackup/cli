import typer
from typing import Optional, List, Annotated
from enum import Enum
import rich
from rich.console import Console
from rich.table import Table
from .decorators import with_explanation

# Configure context settings for help options
context_settings = {
    "help_option_names": ["--help", "-h"],
}

# Create a callback to handle explanations
def show_explanation_callback(ctx: typer.Context):
    """Show explanation for commands if available and no args provided."""
    # Only run for commands, not the main app
    if ctx.invoked_subcommand is None and hasattr(ctx.command, "callback"):
        callback = ctx.command.callback
        if hasattr(callback, "_explanation") and len(ctx.args) == 0 and len(ctx.params) == 1:
            # Only show explanation when no arguments are provided (just the ctx)
            typer.echo(callback._explanation)
            typer.echo("\nCommand help:")
            ctx.invoke(ctx.command.get_help)
            raise typer.Exit()

# Create app with no_args_is_help=True to show help on empty calls
app = typer.Typer(
    context_settings=context_settings,
    no_args_is_help=True,
    help="SkogCLI - A demonstration of Typer capabilities"
)

# Add the callback to the app
@app.callback()
def app_callback(ctx: typer.Context):
    """SkogCLI - A demonstration of Typer capabilities."""
    show_explanation_callback(ctx)

# Create a console for rich output
console = Console()

# Create an enum for command choices
class Format(str, Enum):
    JSON = "json"
    TEXT = "text"
    TABLE = "table"

@app.command()
@with_explanation("A simple greeting command that says hello to a name you provide or to the world.")
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
examples_app = typer.Typer(
    help="Example commands demonstrating Typer features", 
    no_args_is_help=True
)

# Add the callback to the examples app
@examples_app.callback()
def examples_callback(ctx: typer.Context):
    """Example commands demonstrating Typer features."""
    show_explanation_callback(ctx)

app.add_typer(examples_app, name="examples")

@examples_app.command("basic")
@with_explanation("A basic example showing how to use arguments and options in a Typer command.")
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

@app.command()
@with_explanation("Configure application settings. Use --show to view current settings, --set and --value to modify them, or --reset to restore defaults.")
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    set_key: str = typer.Option(None, "--set", help="Set a configuration key"),
    value: str = typer.Option(None, "--value", help="Value for the key to set"),
    reset: bool = typer.Option(False, "--reset", help="Reset configuration to defaults"),
):
    """
    Manage application configuration.
    
    This command allows viewing and modifying the application configuration.
    """
    if reset:
        typer.echo("Configuration reset to defaults")
        return
        
    if show:
        # Display configuration in a table
        table = Table(title="Configuration")
        table.add_column("Key")
        table.add_column("Value")
        
        # Example configuration values
        config_values = {
            "api_url": "https://api.example.com",
            "timeout": "30",
            "debug": "False",
            "theme": "dark"
        }
        
        for key, val in config_values.items():
            table.add_row(key, val)
            
        console.print(table)
        return
        
    if set_key and value:
        typer.echo(f"Setting {set_key}={value}")
        return
    
    # If no options provided, show help
    typer.echo("Use --show to view configuration or --set/--value to modify it")

def main() -> None:
    app()
