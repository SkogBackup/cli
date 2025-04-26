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

# Import and add the agent subcommand
from .agent import agent_app
app.add_typer(agent_app, name="agent")

@app.command()
def version():
    """Show the current version of SkogCLI."""
    typer.echo("SkogCLI v0.1.0")

# Add a callback to handle explanation display
def show_explanation_callback(ctx: typer.Context):
    """Show explanation for commands if available and no args provided."""
    if ctx.invoked_subcommand is None and hasattr(ctx.command, "callback"):
        callback = ctx.command.callback
        if hasattr(callback, "_explanation") and len(ctx.args) == 0 and len(ctx.params) == 1:
            typer.echo(callback._explanation)
            typer.echo("\nCommand help:")
            ctx.invoke(ctx.command.get_help)
            raise typer.Exit()

@app.callback()
def app_callback(ctx: typer.Context):
    """Main app callback to handle explanation display."""
    # Handle agent.name format at the top level
    if ctx.invoked_subcommand is None and len(ctx.args) > 0:
        arg = ctx.args[0]
        if arg.startswith("agent.") and "." in arg:
            # This is an agent command in the format agent.name
            agent_name = arg.split(".", 1)[1]
            
            # Check if there are remaining arguments
            remaining_args = ctx.args[1:] if len(ctx.args) > 1 else []
            
            if remaining_args and remaining_args[0] == "send" and len(remaining_args) > 1:
                # Call the agent send command
                from .agent import send
                ctx.invoke(send, message=remaining_args[1], agent_name=agent_name)
                raise typer.Exit()
            elif remaining_args and remaining_args[0] == "read":
                # Call the agent read command
                from .agent import read_agent
                ctx.invoke(read_agent, name=agent_name)
                raise typer.Exit()
    
    show_explanation_callback(ctx)

def main():
    """Entry point for the CLI application."""
    app()

if __name__ == "__main__":
    main()
