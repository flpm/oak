"""Add books to the library."""

import typer

from collections import defaultdict

from .utils.audible import import_from_audible
from .utils.bookshelf import import_from_bookshelf
from .utils.file import read_catalogue, save_catalogue

app = typer.Typer()


def merge_books(catalogue, books):
    new_books = 0
    for book_id, book_info in books.items():
        for book_type, book in book_info.items():
            if book_id in catalogue:
                if book_type in catalogue[book_id]:
                    current_book = catalogue[book_id][book_type]
                    for key, value in book.items():
                        current_book[key] = value
                else:
                    catalogue[book_id][book_type] = book
            else:
                catalogue[book_id][book_type] = book
                new_books += 1
    return catalogue, new_books


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
