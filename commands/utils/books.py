from rich import print


def print_book(loop_position, bookd_id, book_type, book):
    """
    Print a book summary.

    Parameters
    ----------
    loop_position : tuple
        The book information for the current position in the loop.
    book_id : str
        The book ID.
    book_type : str
        The type of book.
    book : dict
        The book information.

    """
    print("\n")
    print("---")
    print(
        (
            f"[bold white]{loop_position[0] + 1}[/bold white] of [bold white]{loop_position[1]}[/bold white] - "
            f"[bold yellow]{book_type}[/bold yellow] - "
            f"[bold white]{book.get('title', '<missing title>')}[/bold white] "
            f"({book.get('source', '<missing source>')}) - {book.get('authors', '<missing authors>')}"
        )
    )
    print("---")
    description_summary = book.get("description", "<no description>").split("/n")[0]
    print(f"[bright_black]{description_summary}[/bright_black]")
    print("---")
    for show_key in ("purchase_date", "location"):
        print(
            "{}: [bold white]{}[/bold white]".format(
                show_key, book.get(show_key, f"<missing {show_key}>")
            )
        )
    print("---")
