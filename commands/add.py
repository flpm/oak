"""Add books to the library."""

import typer

from collections import defaultdict

from .utils.audible import import_from_audible
from .utils.bookshelf import import_from_bookshelf
from .utils.file import read_catalogue, save_catalogue
from .utils.merge import merge_books

app = typer.Typer()


@app.command()
def bookshelf(export_date: str):
    """Import books from the iPhone Bookshelf app."""
    catalogue = defaultdict(dict, read_catalogue())
    print(f"Books in catalogue: {len(catalogue)} books.")
    books = import_from_bookshelf(export_date)
    catalogue, new_books = merge_books(catalogue, books)
    print(f"Found in Bookshelf export: {len(books)} books.")
    print(f"Added {new_books} new books.")
    save_catalogue(catalogue)


@app.command()
def audible():
    """Import books from the Audible listening history."""
    catalogue = defaultdict(dict, read_catalogue())
    print(f"Books in catalogue: {len(catalogue)} books.")
    books = import_from_audible()
    catalogue, new_books = merge_books(catalogue, books)
    print(f"Found in Audible listening history: {len(books)} books.")
    print(f"Added {new_books} new books.")
    save_catalogue(catalogue)


if __name__ == "__main__":
    app()
