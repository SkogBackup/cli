import typer
from typing import Optional

# Configure context settings for help options
context_settings = {
    "help_option_names": ["--help", "-h"],
}

# Create app with no_args_is_help=True to show help on empty calls
app = typer.Typer(
    context_settings=context_settings,
    no_args_is_help=True
)

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

def main() -> None:
    app()
