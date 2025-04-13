"""SkogCLI - A demonstration Typer-based CLI tool for the SkogAI project."""

import os
import subprocess
import typer
from typing import Optional, List, Callable, Iterable
from pathlib import Path

# Create the main Typer app
app = typer.Typer(no_args_is_help=True)

# Import and add the memory subcommand
from .memory import memory_app
app.add_typer(memory_app, name="memory")

# Import and add the config subcommand
from .settings import config_app
app.add_typer(config_app, name="config")

# Import and add the misc subcommand
from .misc import misc_app
app.add_typer(misc_app, name="misc")

@app.command()
def hello(name: str = "World"):
    """Say hello to someone."""
    typer.echo(f"Hello {name}!")

@app.command()
def version():
    """Show the current version of SkogCLI."""
    typer.echo("SkogCLI v0.1.0")

@app.command()
def edit(
    file: Path = typer.Argument(..., help="Path to the file to edit"),
    editor: Optional[str] = typer.Option(None, "--editor", "-e", help="Specify which editor to use (defaults to $EDITOR)")
):
    """Open a file in your default text editor."""
    # Get the editor from the environment or use the provided one
    editor_cmd = editor or os.environ.get("EDITOR", "vim")
    
    # Check if the file exists
    if not file.exists() and not typer.confirm(f"File {file} does not exist. Create it?"):
        typer.echo("Operation cancelled.")
        return
    
    # Make sure the parent directory exists
    file.parent.mkdir(parents=True, exist_ok=True)
    
    # Open the file in the editor
    try:
        subprocess.run([editor_cmd, str(file)], check=True)
        typer.echo(f"Finished editing {file}")
    except subprocess.CalledProcessError:
        typer.echo(f"Error occurred while editing {file}")
    except FileNotFoundError:
        typer.echo(f"Editor '{editor_cmd}' not found. Set the EDITOR environment variable or use --editor.")

def main():
    """Entry point for the CLI application."""
    app()

def get_completion_script():
    """Generate shell completion script."""
    import click
    shell = os.environ.get("SHELL", "").split("/")[-1]
    if not shell:
        return "echo 'Shell not detected'"
    
    complete_var = f"_{app.info.name.upper()}_COMPLETE"
    
    if shell == "bash":
        return f"{complete_var}=bash_source {app.info.name} > ~/.{app.info.name}-complete.bash"
    elif shell == "zsh":
        return f"{complete_var}=zsh_source {app.info.name} > ~/.{app.info.name}-complete.zsh"
    elif shell == "fish":
        return f"{complete_var}=fish_source {app.info.name} > ~/.config/fish/completions/{app.info.name}.fish"
    else:
        return f"echo 'Shell {shell} not supported for completion'"

@app.command("completion")
def completion(
    shell: str = typer.Option(None, help="Shell to generate completion for (bash, zsh, fish)")
):
    """Generate shell completion script."""
    import click
    
    if shell is None:
        # Try to detect the shell
        detected_shell = os.environ.get("SHELL", "").split("/")[-1]
        if not detected_shell:
            typer.echo("Could not detect shell. Please specify with --shell.")
            raise typer.Exit(1)
        shell = detected_shell
    
    complete_var = f"_{app.info.name.upper()}_COMPLETE"
    
    if shell == "bash":
        script = f"{complete_var}=bash_source {app.info.name}"
        typer.echo(f"# Add this to ~/.bashrc:")
        typer.echo(f"eval \"$({script})\"")
    elif shell == "zsh":
        script = f"{complete_var}=zsh_source {app.info.name}"
        typer.echo(f"# Add this to ~/.zshrc:")
        typer.echo(f"eval \"$({script})\"")
    elif shell == "fish":
        script = f"{complete_var}=fish_source {app.info.name}"
        typer.echo(f"# Add this to ~/.config/fish/config.fish:")
        typer.echo(f"{script} > ~/.config/fish/completions/{app.info.name}.fish")
    else:
        typer.echo(f"Shell {shell} not supported for completion")
        raise typer.Exit(1)

if __name__ == "__main__":
    main()
