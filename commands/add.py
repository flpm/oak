"""Add books to the library."""

import typer

from .utils.bookshelf import import_from_bookshelf
from .utils.file import read_catalogue, save_catalogue

app = typer.Typer()


@app.command()
def bookshelf(export_date: str):
    """Import books from the iPhone Bookshelf app."""
    catalogue = read_catalogue()
    print(f"Books in catalogue: {len(catalogue)} books.")
    books = import_from_bookshelf(export_date)
    print(f"Found in Bookshelf export: {len(books)} books.")
    print(f"New books added: {len(set(books.keys()) - set(catalogue.keys()))} books.")
    for book_id, book in books.items():
        if book_id in catalogue:
            current_book = catalogue[book_id]
            for key, value in book.items():
                current_book[key] = value
        catalogue[book_id] = book
    save_catalogue(catalogue)


@app.command()
def audible():
    """Import books from the Audible listening history."""
    catalogue = read_catalogue()
    print("Books in catalogue:", len(catalogue))


if __name__ == "__main__":
    app()
