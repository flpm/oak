import typer

from collections import defaultdict

import commands.add
import commands.enrich
import commands.edit
import commands.export
import commands.sync

from commands.stats import generate_stats


app = typer.Typer(pretty_exceptions_show_locals=False)
app.add_typer(commands.add.app, name="add", short_help="Add books to the library.")
app.add_typer(
    commands.enrich.app,
    name="enrich",
    short_help="Enrich books already in the library.",
)


@app.command()
def sync():
    """Sync books folders."""
    commands.sync.sync_folders(
        "./output/books", "../flpm.github.io/bookshelf/books", "books"
    )
    commands.sync.sync_folders(
        "./output/lists", "../flpm.github.io/bookshelf/lists", "lists"
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
