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
        "rank": "Edit the book ranking",
        "note": "Edit the book note",
        "list": "List all book attributes",
        "set": "Set a book attribute",
        "stat": "Edit the read status",
        "mult": "Edit the multiple reads status",
        "rec": "Edit the recommendation status",
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
    ranking = sorted(
        [book for book in flat_catalogue if book[2].get("ranking") is not None],
        key=lambda x: x[2].get("ranking"),
    )
    print(f"Initial ranking: {len(ranking)} books.")
    for *_, b_book in ranking:
        print(f"Ranking: {b_book.get('ranking')} {b_book.get('title')}")

    orders = read_amazon_orders()

    for book_id, book_type, book in flat_catalogue:
        # Insert her any code to modify the book attributes
        book["read_status"] = book.get("status")
        if book.get("status"):
            del book["status"]
        book["recommendation_status"] = book.get("recommend")
        if book.get("recommend"):
            del book["recommend"]

    total = len(flat_catalogue)
    current_index = 0
    while True:
        book_id, book_type, book = flat_catalogue[current_index]
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
                for *_, b_book in flat_catalogue:
                    b_book.pop("ranking", None)
                for position, (*_, b_book) in enumerate(ranking):
                    print(f"Ranking: {position + 1} {b_book.get('title')}")
                    b_book["ranking"] = position + 1
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

            elif answer == "rank":
                print(f"Current ranking ({len(ranking)} books):")
                for position, (*_, b_book) in enumerate(ranking):
                    print(f"{position + 1} {b_book.get('title', '<missing title>')}")
                if book_id in [b[0] for b in ranking]:
                    if confirm("Remove this book from ranking?", False):
                        ranking = [b for b in ranking if b[0] != book_id]
                rank = Prompt.ask("Enter the ranking for this book (e.g. 1)")
                if rank:
                    try:
                        rank = int(rank)
                        if book_id in [b[0] for b in ranking]:
                            ranking = [b for b in ranking if b[0] != book_id]
                        if rank < 1 or rank > len(ranking) + 2:
                            raise ValueError

                        ranking = [b for b in ranking if b[0] != book_id]
                        if rank > len(ranking):
                            ranking.append((book_id, book_type, book))
                        else:
                            ranking = (
                                ranking[: rank - 1]
                                + [(book_id, book_type, book)]
                                + ranking[rank - 1 :]
                            )
                        print("[green]Update ranking.[/green]")
                    except ValueError:
                        print("[red]Invalid rank[/red]")
                answer = "not rank"

            elif answer == "note":
                current_note = book.get("note")
                if current_note:
                    print("Current note:")
                    print(f"[bold white]{current_note}[/bold white]")
                    if confirm("Remove the note?", False):
                        book.pop("note")
                        print("[red]Deleted note.[/red]")
                note = Prompt.ask("Enter a note for the book (you can enter markdown)")
                if note:
                    book["note"] = note
                    print("[green]Theme set[/green]")
                answer = "not note"

            elif answer == "stat":
                read_options = {
                    "n": "have not started",
                    "r": f"{'read' if book_type == 'book' else 'listened to'}",
                    "p": f"partially {'read' if book_type == 'book' else 'listened to'}",
                    "c": "consulted",
                    "t": f"plan to {'read' if book_type == 'book' else 'listen to'}",
                    "d": "did not finish",
                }
                read_opptions_str = ", ".join(
                    f"{option} for {value}" for option, value in read_options.items()
                )

                status_str = None
                while not status_str:
                    status = Prompt.ask(
                        f"Enter the read status ({read_opptions_str})",
                        choices=list(read_options.keys()),
                        default="S",
                        show_choices=True,
                        show_default=True,
                    ).lower()
                    status_str = read_options.get(status)
                if status_str:
                    book["status"] = status_str
                    print(f"[green]Read status set to {read_options[status]}[/green]")
                # automatically advance to next book
                current_index += 1
                if current_index >= total:
                    current_index = total - 1
                answer = "next"

            elif answer == "list":
                print("\n[bold yellow]Book attributes:[/bold yellow]")
                for attribute, value in book.items():
                    if not value:
                        value = "<blank>"
                    print(f"{attribute}: [bold white]{value}[/bold white]")
                if confirm("Change an attribute?", False):
                    attribute = Prompt.ask("Enter the attribute to set (e.g. language)")
                    if old_value := book.get(attribute):
                        print(
                            f"Current {attribute}: [bold white]{old_value}[/bold white]"
                        )
                    value = Prompt.ask(
                        "Enter the attribute value (e.g. ['English', 'French'])"
                    )
                    if not value and confirm("Set the attribute to None?", False):
                        value = None
                    print(f"New {attribute}: [bold yellow]{value}[/bold yellow]")
                    if confirm("Change the attribute?", False):
                        book[attribute] = value
                        print("[green]Attribute set[/green]")

            elif answer == "mult":
                if confirm("Read this book multiple times?", False):
                    book["multiple_reads"] = True
                else:
                    book.pop("multiple_reads")

            elif answer == "rec":
                if confirm("Do I recommend this book?", True):
                    book["recommend"] = True
                else:
                    if confirm("Do I want to NOT recommend this book?", True):
                        book["recommend"] = False
                    else:
                        book.pop("recommend", None)
