import datetime as dt
from typer import confirm
from rich import print
from rich.prompt import Prompt

from .books import print_book
from .file import save_catalogue, read_amazon_orders
from .orders import search_orders, choose_order


def book_action(
    loop_position,
    book_type,
    book_id,
    book,
    more_actions=None,
    prompt="Choose action",
    default="next",
):
    """
    Print a book summary and wait for user input.

    Parameters
    ----------
    loop_position : tuple
        The book information for the current position in the loop.
    book_type : str
        The type of book.
    book_id : str
        The book ID.
    book : dict
        The book information.
    more_actions : dict, optional
        Additional actions to add to the default actions, by default None
    prompt : str, optional
        The prompt to show the user, by default "Choose action"
    default : str, optional
        The default action, by default "next"

    Returns
    -------
    str
        The action chosen by the user.
    """
    if more_actions is None:
        more_actions = dict()
    basic_actions = {
        "next": "Next book",
        "prev": "Previous book",
        "go": "Go to book (by number)",
        "find": "Find book (by title)",
        "save": "Save",
        "quit": "Quit",
    }
    book_actions = {
        "date": "Edit book purchase date",
        "city": "Edit book purchase city",
        "order": "Delete order from the book",
        "theme": "Edit the book theme",
        "rename": "Rename theme",
        "find theme": "Find a book by theme",
        "top shelf": "Add top shelf attributes",
    }
    actions = {**basic_actions, **book_actions, **more_actions}
    valid_options = actions.keys()
    if default and default not in valid_options:
        default = "next"

    print_book(loop_position, book_type, book_id, book)
    option = Prompt.ask(
        prompt,
        choices=valid_options,
        default=default,
        show_choices=True,
        show_default=True,
    )
    return option


def confirm_loop(valid_options=("y", "n"), prompt="Are you sure?", default="n"):
    """
    Ask the user to confirm an action.

    Parameters
    ----------
    valid_options : tuple, optional
        The valid options, by default ("y", "n")
    prompt : str, optional
        The prompt to show the user, by default "Are you sure?"
    default : str, optional
        The default option, by default "n"

    Returns
    -------
    str
        The option chosen by the user.
    """
    option = Prompt.ask(prompt, choices=valid_options, default=default)
    return option


def edit_loop(catalogue):
    """
    Handles the interactive loop to edit the book attributes.

    Parameters
    ----------
    catalogue : dict
        The current catalogue.

    Returns
    -------
    dict
        The modified catalogue.
    """
    flat_catalogue = sorted(
        [
            (book_id, book_type, book)
            for book_id, book_info in catalogue.items()
            for book_type, book in book_info.items()
            if book_type != "audiobook_sample"
        ],
        key=lambda x: x[2].get(
            "purchase_date", x[2].get("listening_date", "9999-99-99")
        ),
    )

    orders = read_amazon_orders()

    total = len(flat_catalogue)
    current_index = 0
    while True:
        book_id, book_type, book = flat_catalogue[current_index]
        print(book.get("title", "<missing title>"))
        answer = None
        while answer not in ("next", "prev", "go", "find"):
            answer = book_action(
                (current_index, total),
                book_id,
                book_type,
                book,
            )
            print(f"selected: [red]{answer}[/red]")
            if answer == "quit":
                if confirm("Are you sure you want to quit?", False):
                    return catalogue
                answer = "not quit"

            elif answer == "next":
                current_index += 1
                if current_index >= total:
                    current_index = total - 1

            elif answer == "prev":
                current_index -= 1
                if current_index < 0:
                    current_index = 0

            elif answer == "go":
                while True:
                    try:
                        backup_current_index = current_index
                        current_index = (
                            int(
                                Prompt.ask(
                                    "Enter book number", default=current_index + 1
                                )
                            )
                            - 1
                        )
                    except ValueError:
                        print("[red]Invalid book number[/red]")
                    else:
                        if current_index < 0 or current_index >= total:
                            print("[red]Invalid book number[/red]")
                            current_index = backup_current_index
                        else:
                            break

            elif answer == "find":
                while True:
                    try:
                        search_term = Prompt.ask("Enter search term")
                    except ValueError:
                        print("Invalid search term")
                    else:
                        break
                for i, (*_, book) in enumerate(flat_catalogue):
                    if i <= current_index:
                        continue
                    book_title = book.get("title", "<missing title>")
                    if search_term.lower() in book_title.lower():
                        print(f"Found book: {i} {book_title}")
                        # print(flat_catalogue[i][2])
                        current_index = i
                        break
                else:
                    print("[red]Book not found[/red]")
                    break

            elif answer == "save":
                save_catalogue(catalogue)
                print("[green]Catalogue saved[/green]")

            elif answer == "date":
                new_date = Prompt.ask("Enter new purchase date (YYYY-MM-DD)")
                try:
                    new_date = (
                        dt.datetime.strptime(new_date, "%Y-%m-%d").date().isoformat()
                    )
                except ValueError:
                    print("[red]Invalid date[/red]")
                else:
                    book["purchase_date"] = new_date

            elif answer == "city":
                location = Prompt.ask("Enter the city of purchase (e.g. Paris)")
                if location:
                    book["location"] = location
                    print("[geen]Location set[/geen]")

            elif answer == "order":
                answer = "not order"
                if book.get("order"):
                    print(f"Order information:")
                    for key, value in book.get("order", {}).items():
                        print(f"  - {key}: {value}")
                if confirm("Remove the order information?", False):
                    book.pop("order")
                    print("[red]Deleted order information.[/red]")
                order_keyword = Prompt.ask("Enter keyword to search orders")
                if order_keyword:
                    candidates = search_orders(order_keyword, orders)
                    selected = choose_order(candidates, book.get("order"))
                    if selected:
                        book["order"] = selected
                        print("[green]Added order information.[/green]")

            elif answer == "theme":
                current_theme = book.get("theme")
                if current_theme:
                    print(f"Current theme: {current_theme}")
                    if confirm("Remove the theme?", False):
                        book.pop("theme")
                        print("[red]Deleted theme.[/red]")
                theme = Prompt.ask("Enter a theme for the book (e.g. history)")
                if theme:
                    book["theme"] = theme
                    print("[green]Theme set[/green]")

            elif answer == "rename":
                if confirm("Rename a theme?", False):
                    old_theme = Prompt.ask("Enter the old theme name")
                    if old_theme:
                        new_theme = Prompt.ask("Enter the new theme name")
                        if new_theme:
                            rename_count = 0
                            for book_id, book_type, book in flat_catalogue:
                                if book.get("theme") == old_theme:
                                    book["theme"] = new_theme
                                    rename_count += 1
                            if rename_count > 0:
                                print(f"[green]Renamed {rename_count} books.[/green]")
                answer = "not rename"

            elif answer == "find theme":
                while True:
                    try:
                        search_term = Prompt.ask("Enter theme search term")
                    except ValueError:
                        print("Invalid search term")
                    else:
                        break
                for i, (*_, book) in enumerate(flat_catalogue):
                    if i <= current_index:
                        continue
                    book_theme = book.get("theme", "")
                    book_title = book.get("title", "<missing title>")
                    if search_term.lower() in book_theme.lower():
                        print(f"Found book: {i} {book_title}")
                        current_index = i
                        break
                else:
                    print("[red]Book not found[/red]")
                    break

            elif answer == "top shelf":
                if confirm("Edit top shelf attributes", False):
                    if confirm("Is this book signed?", False):
                        book["signed"] = True
                        if signature_details := Prompt.ask(
                            "Signed by? (e.g. the author)"
                        ):
                            book["signature_details"] = signature_details
                    else:
                        book.pop("signed", None)
                        book.pop("signature_details", None)
                    if confirm("Is this a first edition?", False):
                        book["first_edition"] = True
                        if first_edition_details := Prompt.ask(
                            "Enter first edition details (e.g. british)"
                        ):
                            book["first_edition_details"] = first_edition_details
                    else:
                        book.pop("first_edition", None)
                        book.pop("first_edition_details", None)
                answer = "not top shelf"
