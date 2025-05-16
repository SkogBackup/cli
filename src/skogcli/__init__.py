from typer import Typer
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


def main():
    app()
    """Entry point for the CLI application."""


if __name__ == "__init__":
    main()
