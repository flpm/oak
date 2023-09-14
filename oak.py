import typer

import commands.add


app = typer.Typer()
app.add_typer(commands.add.app, name="add", short_help="Add books to the library.")


@app.command()
def enrich(data_source: str):
    """Enrich current books with data from a source."""
    if data_source not in ["amazon"]:
        typer.echo(f"Unsupported data source: {data_source}")
        raise typer.Exit(code=1)
    print("Enrich books using data from source:", data_source)


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
    print("Show stats.")


if __name__ == "__main__":
    app()
