import typer

from collections import defaultdict

import commands.add
import commands.enrich
import commands.edit

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
def edit():
    """Edit books in the library."""
    commands.edit.run_edit_loop()


@app.command()
def export(target_folder: str = "./output"):
    """Export books as Markdown files."""
    print("Export as markdown to:", target_folder)


@app.command()
def reset():
    """Delete all books in the library."""
    print("Reset library.")


@app.command()
def stats(stats_type: str = "attributes"):
    """Show stats about the current catalog."""
    generate_stats(stats_type)


if __name__ == "__main__":
    app()
