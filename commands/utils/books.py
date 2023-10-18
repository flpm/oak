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
    if book.get("signed"):
        signature_details = book.get("signature_details", "the author")
        print(f"[bold yellow]This book is signed by {signature_details}.[/bold yellow]")
    if book.get("first_edition"):
        first_edition_details = book.get("first_edition_details", "")
        print(
            f"[bold yellow]This book is a first {first_edition_details} edition.[/bold yellow]"
        )
    for show_key in ("purchase_date", "listening_date", "location"):
        if not book.get("type") == "audiobook" and show_key == "listening_date":
            continue
        print(
            "{}: [bold white]{}[/bold white]".format(
                show_key, book.get(show_key, f"<missing {show_key}>")
            )
        )
    if book.get("order"):
        order_info_string = [
            f"{key}: [bold white]{value}[/bold white]"
            for key, value in book["order"].items()
            if key in ("order_date", "product_name")
        ]
    elif book.get("type") == "book":
        order_info_string = "[bold white]<missing order information>[/bold white]"
        print(f"order: {order_info_string}")
    if topics := book.get("topics"):
        print(f"topics: {topics}")
    if book.get("theme"):
        print(f"theme: [bold white]{book['theme']}[/bold white]")
    if book.get("status"):
        rec_status = book.get("recommend")
        recommendation = "."
        if rec_status:
            recommendation = " and I [bold white]recommend[/bold white] it."
        elif rec_status is False:
            recommendation = " and I [bold white]do not recommend[/bold white] it."

        print(
            f"status: I [bold white]{book['status']}[/bold white] this {book_type}{' multiple times' if book.get('multiple_reads') else ''}"
            f"{recommendation}"
        )
    print("---")
