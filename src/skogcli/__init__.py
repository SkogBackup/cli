from typer import Typer, Context, Option, Exit
from .memory import memory_app
from .settings import config_app
from .script import script_app
from .agent import agent_app

"""SkogCLI - A demonstration Typer-based CLI tool for the SkogAI project."""


# Function to add helpall option to subcommands
def add_helpall_to_app(app_instance, app_name):
    @app_instance.callback(invoke_without_command=True)
    def subcommand_callback(
        ctx: Context,
        helpall: bool = Option(
            False, "--helpall", help=f"Show comprehensive documentation for {app_name} commands"
        ),
    ):
        if helpall:
            import subprocess
            # Generate the documentation for this specific command group
            subprocess.run(
                ["typer", f"skogcli.{app_name}", "utils", "docs", 
                 "--name", f"SkogCLI {app_name}"],
                check=True
            )
            raise Exit()

# Create the main Typer app
app = Typer(no_args_is_help=True, name="SkogCLI")
app.add_typer(memory_app, name="memory")
app.add_typer(config_app, name="config")
app.add_typer(script_app, name="script")
app.add_typer(agent_app, name="agent")

# Add helpall option to each subcommand
add_helpall_to_app(memory_app, "memory")
add_helpall_to_app(config_app, "config")
add_helpall_to_app(script_app, "script")
add_helpall_to_app(agent_app, "agent")


@app.callback(invoke_without_command=True)
def callback(
    ctx: Context,
    helpall: bool = Option(
        False, "--helpall", help="Show comprehensive documentation for all commands"
    ),
):
    """SkogCLI - Command line interface for SkogAI."""
    if helpall:
        import subprocess
        import sys
        
        # Generate the documentation for all commands
        subprocess.run(
            ["typer", "skogcli", "utils", "docs", "--name", "SkogCLI"],
            check=True
        )
        
        raise Exit()


@app.command()
def version():
    """Show the version of SkogCLI."""
    import importlib.metadata
    try:
        version = importlib.metadata.version("skogcli")
        print(f"SkogCLI version {version}")
    except importlib.metadata.PackageNotFoundError:
        print("SkogCLI version: development")


def main():
    """Entry point for the CLI application."""
    app()


if __name__ == "__init__":
    main()
