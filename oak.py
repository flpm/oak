import typer

import commands.add
import commands.enrich
from commands.stats import generate_stats


app = typer.Typer()
app.add_typer(commands.add.app, name="add", short_help="Add books to the library.")
app.add_typer(
    commands.enrich.app,
    name="enrich",
    short_help="Enrich books already in the library.",
)


@app.command()
def tag():
    """Tag books with keywords."""
    print("Tag books.")


@app.command()
def export(target_folder: str = "./output"):
    """Export books as Markdown files."""
    print("Export as markdown to:", target_folder)


@app.command()
def reset():
    """Delete all books in the library."""
    print("Reset library.")


@app.command()
def stats():
    """Show stats about the current catalog."""
    generate_stats()


if __name__ == "__main__":
    app()
