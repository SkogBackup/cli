run skogcli via "uv run skogcli"

use "uv add <package> && uv lock && uv sync" instead of "pip install"

empty calls to a command should always return help - use the context_settings parameter in typer.Typer() with help_option_names to enable this behavior
