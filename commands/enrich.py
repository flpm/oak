"""Enrich books already in the library."""

import typer

from collections import defaultdict

from .utils.audible import enrich_audible
from .utils.bookshelf import import_from_bookshelf
from .utils.file import read_catalogue, save_catalogue
from .utils.merge import merge_books

app = typer.Typer()


@app.command()
def amazon():
    """Enrich books using data from Amazon purchases."""
    print("Enrich books using data from Amazon purchases.")
    # catalogue = defaultdict(dict, read_catalogue())
    # print(f"Books in catalogue: {len(catalogue)} books.")
    # books = import_from_bookshelf(export_date)
    # catalogue, new_books = merge_books(catalogue, books)
    # print(f"Found in Bookshelf export: {len(books)} books.")
    # print(f"Added {new_books} new books.")
    # save_catalogue(catalogue)


@app.command()
def audible():
    """Enrich audiobooks using information from the Audible website."""
    catalogue = defaultdict(dict, read_catalogue())
    print(f"Books in catalogue: {len(catalogue)} books.")
    catalogue, modified_books = enrich_audible(catalogue)
    print(f"Enriched {modified_books} books.")
    save_catalogue(catalogue)


if __name__ == "__main__":
    app()
