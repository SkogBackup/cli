import typer

app = typer.Typer()

def complete_color(ctx: typer.Context, args: list[str], incomplete: str):
    colors = ["red", "green", "blue", "yellow"]
    return [color for color in colors if color.startswith(incomplete)]

@app.command()
def example(
    color: str = typer.Option(
        ..., 
        help="Choose a color", 
        autocompletion=complete_color
    )
):
    """Example command with tab completion."""
    typer.echo(f"You chose: {color}")

def main() -> None:
    app()
