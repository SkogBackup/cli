from typer import Typer, Context, Option, Exit
from .memory import memory_app
from .settings import config_app
from .script import script_app
from .agent import agent_app

"""SkogCLI - A demonstration Typer-based CLI tool for the SkogAI project."""


# Create the main Typer app
app = Typer(no_args_is_help=True, name="SkogCLI")
app.add_typer(memory_app, name="memory")
app.add_typer(config_app, name="config")
app.add_typer(script_app, name="script")
app.add_typer(agent_app, name="agent")


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
        
        # Generate the documentation and pipe it directly to stdout
        subprocess.run(
            ["typer", "skogcli", "utils", "docs", "--name", "SkogCLI"],
            check=True
        )
        
        raise Exit()


def main():
    """Entry point for the CLI application."""
    app()


if __name__ == "__init__":
    main()
