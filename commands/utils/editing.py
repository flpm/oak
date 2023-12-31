import datetime as dt
from collections import defaultdict
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
        "delete": "Mark book as deleted",
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
        "origin": "Edit the book origin",
        "inspired_by": "Edit the book that this one was inspired by",
        "note": "Edit the book note",
        "list": "List all book attributes",
        "set": "Set a book attribute",
        "stat": "Edit the read status",
        "mult": "Edit the multiple reads status",
        "rec": "Edit the recommendation status",
        "blank": "Find the next book with a blank attribute",
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
        pass

    title_dict = defaultdict(list)
    for book_id, book_type, book in flat_catalogue:
        if book_title := book.get("title"):
            title_dict[book_title].append((book, book_id, book_type))

    c = 0
    for entry in title_dict.values():
        if len(entry) == 2:
            book_1, id_1, type_1 = entry[0]
            book_2, id_2, type_2 = entry[1]
            if type_1 != type_2:
                record = {
                    type_1: id_1,
                    type_2: id_2,
                }
                book_1["multiple_formats"] = record
                book_2["multiple_formats"] = record
            c += 1
    print(f"Found {c//2} books with multiple formats.")

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

            elif answer in ("origin", "inspired_by"):
                current_origin = book.get(answer, dict())
                if current_origin:
                    print(f"Current origin: {current_origin}")
                    if confirm(f"Remove the {answer}?", False):
                        book.pop(answer)
                        print(f"[red]Deleted {answer}.[/red]")
                else:
                    option = None
                    while option not in ("book", "web", "note", "done"):
                        option = Prompt.ask(
                            "Edit origin information",
                            choices=[
                                "book",
                                "web",
                                "gift",
                                "email",
                                "recommendation",
                                "bookstore",
                                "found",
                                "note",
                            ],
                            default="note",
                            show_choices=True,
                            show_default=True,
                        )
                        if value := Prompt.ask(f"Enter the {option} detail"):
                            if option == "book":
                                list_of_titles = [
                                    (b_id, b_type, b["title"])
                                    for b_id, b_type, b in flat_catalogue
                                    if value in b.get("title", "").lower()
                                ]
                                print(f"Found {len(list_of_titles)} books.")
                                for entry in list_of_titles:
                                    print(f"({entry[1]}) {entry[2]}")
                                    if confirm("Is this the book?", False):
                                        value = entry
                                        break
                                else:
                                    print("[red]Book not found[/red]")
                                    continue
                            elif option == "web":
                                if link_title := Prompt.ask(
                                    "Enter the title of the web page"
                                ):
                                    if source := Prompt.ask(
                                        "Enter the source of the link"
                                    ):
                                        value = (link_title, value, source)
                                    else:
                                        value = (link_title, value, None)
                                else:
                                    value = (value, value)
                            elif option == "gift":
                                reason = Prompt.ask("What was the occasion?") or None
                                value = (value, reason)
                            else:
                                additional_detail = (
                                    Prompt.ask("Additional detail?") or None
                                )
                                value = (value, additional_detail)

                            current_origin[option] = value
                            print(f"[green]Book {answer} set[/green]: {value}")
                            option = "done"
                            book[answer] = current_origin
                answer = "not origin"

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
                if not book.get("read_status"):
                    book["read_status"] = {}

                if confirm("Have you started reading this book?", False):
                    book["read_status"]["start"] = True
                elif book["read_status"].get("start"):
                    book["read_status"].pop("start")

                if confirm("Have you finished this book?", False):
                    book["read_status"]["finish"] = True
                elif book["read_status"].get("finish"):
                    book["read_status"].pop("finish")

                if confirm("Multiple times?", False):
                    book["read_status"]["multiple"] = True
                elif book["read_status"].get("multiple"):
                    book["read_status"].pop("multiple")

                if confirm("Like?", False):
                    book["read_status"]["like"] = True
                elif book["read_status"].get("like"):
                    book["read_status"].pop("like")

                if confirm("Dislike?", False):
                    book["read_status"]["dislike"] = True
                elif book["read_status"].get("dislike"):
                    book["read_status"].pop("dislike")

                if confirm("Do you plan to read this book?", False):
                    book["read_status"]["plan"] = True
                elif book["read_status"].get("plan"):
                    book["read_status"].pop("plan")

                if confirm("Do you recommend this book?", False):
                    book["read_status"]["recommend"] = True
                elif book["read_status"].get("recommend"):
                    book["read_status"].pop("recommend")

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

            elif answer == "blank":
                while True:
                    try:
                        attribute_name = Prompt.ask(
                            "Enter attribute name to find the next book with a blank value"
                        )
                    except ValueError:
                        print("Invalid attribute name")
                    else:
                        break
                for i, (*_, book) in enumerate(flat_catalogue):
                    if i <= current_index:
                        continue
                    if not book.get(attribute_name):
                        print(f"Found book: {i} {book.get('title')}")
                        current_index = i
                        break
                else:
                    print("[red]Book not found[/red]")
                    break

            elif answer == "delete":
                deleted_now = book.get("deleted", False)
                if not deleted_now and confirm("Delete this book?", False):
                    book["deleted"] = True
                    print("[red]Book deleted[/red]")
                elif deleted_now and confirm("Restore this book?", False):
                    book.pop("deleted")
                    print("[green]Book restored[/green]")
