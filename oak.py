import typer
import shutil
from collections import defaultdict

import commands.add
import commands.enrich
import commands.edit
import commands.export
import commands.sync
import commands.reset
import commands.save
import commands.make

from commands.stats import generate_stats


app = typer.Typer(pretty_exceptions_show_locals=False)
app.add_typer(commands.add.app, name="add", short_help="Add books to the library.")
app.add_typer(
    commands.enrich.app,
    name="enrich",
    short_help="Enrich books already in the library.",
)


@app.command()
def reset():
    """Reset the library."""
    commands.reset.reset_library()


@app.command()
def save():
    """Save current attribute states so it can be used to enrich the data later on."""
    commands.save.save_attributes()


@app.command()
def load():
    """Load current attribute states from save file."""
    commands.save.load_attributes()


@app.command()
def make(export_date: str, ask: bool = False):
    """Save current attribute states so it can be used to enrich the data later on."""
    commands.make.make_catalogue(export_date, quiet=not ask)


@app.command()
def sync():
    """Sync books folders."""
    commands.sync.sync_folders(
        "./output/books", "../flpm.github.io/bookshelf/books", "books"
    )
    commands.sync.sync_folders(
        "./output/lists", "../flpm.github.io/bookshelf/lists", "lists"
    )
    shutil.copytree(
        "./output/covers",
        "../flpm.github.io/bookshelf/covers",
        dirs_exist_ok=True,
    )


@app.command()
def edit():
    """Edit books in the library."""
    commands.edit.run_edit_loop()


@app.command()
def export(target_folder: str = "./output"):
    """Export books as Markdown files."""
    commands.export.export_markdown(target_folder)


@app.command()
def stats(stats_type: str = "attributes"):
    """Show stats about the current catalog."""
    generate_stats(stats_type)


if __name__ == "__main__":
    app()
