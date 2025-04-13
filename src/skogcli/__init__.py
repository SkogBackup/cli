"""SkogCLI - A demonstration Typer-based CLI tool for the SkogAI project."""

import typer
from typing import Optional

# Create the main Typer app
app = typer.Typer(no_args_is_help=True)

# Import and add the memory subcommand
from .memory import memory_app
app.add_typer(memory_app, name="memory")

# Import and add the config subcommand
from .settings import config_app
app.add_typer(config_app, name="config")

@app.command()
def hello(name: str = "World"):
    """Say hello to someone."""
    typer.echo(f"Hello {name}!")

@app.command()
def version():
    """Show the current version of SkogCLI."""
    typer.echo("SkogCLI v0.1.0")

def main():
    """Entry point for the CLI application."""
    app()

if __name__ == "__main__":
    main()
