run skogcli via "uv run skogcli"

use "uv add <package> && uv lock && uv sync" instead of "pip install"

empty calls to a command should always return help - use the no_args_is_help=True parameter in typer.Typer() to enable this behavior
