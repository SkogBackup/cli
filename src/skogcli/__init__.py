import typer

# Configure context settings for help options
context_settings = {
    "help_option_names": ["--help", "-h"],
}

# Create app with no_args_is_help=True to show help on empty calls
app = typer.Typer(
    context_settings=context_settings,
    no_args_is_help=True
)

def complete_color(ctx: typer.Context, args: list[str], incomplete: str):
    colors = ["red", "green", "blue", "yellow"]
    return [color for color in colors if color.startswith(incomplete)]

@app.command()
def example(
    color: str = typer.Option(
        None, 
        help="Choose a color", 
        autocompletion=complete_color
    )
):
    """Example command with tab completion."""
    typer.echo(f"You chose: {color}")

def main() -> None:
    app()
