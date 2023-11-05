"""Export book catalogue to Markdown files"""

import datetime as dt
import os
from calendar import month_name
from rich import print
from .utils.file import (
    read_catalogue,
    write_markdown_book,
    write_markdown_list,
    include_book,
)
from .utils.exporting import (
    create_condition_list,
    subtitles_by_value,
)


def export_markdown(output_folder="./output"):
    """
    Export books as Markdown files

    Parameters
    ----------
    output_folder : str
        The folder to export the Markdown files to.
    """

    book_output_folder = f"{output_folder}/books"
    list_output_folder = f"{output_folder}/lists"

    print(f"Exporting books:")
    print(f"  - cleaning up {book_output_folder}")
    for filename in os.listdir(book_output_folder):
        if filename.endswith(".md"):
            os.remove(f"{book_output_folder}/{filename}")
    print(f"  - cleaning up {list_output_folder}")
    for filename in os.listdir(list_output_folder):
        if filename.endswith(".md"):
            os.remove(f"{list_output_folder}/{filename}")

    exported_count = 0
    skipped_count = 0
    catalogue = read_catalogue()
    for book_id, book_info in catalogue.items():
        for book_type, book in book_info.items():
            if book_type == "audiobook_sample":
                continue
            if not include_book(book):
                print(
                    f"  - [bold red]Skipping[/bold red] {book['title']} ({book['book_id']})"
                )
                continue
            filename = f"{book['book_id']}.md"
            exported = write_markdown_book(book, filename, book_output_folder)
            if exported:
                exported_count += 1
            else:
                skipped_count += 1

    if skipped_count:
        print(f"Skipped {skipped_count} books")
    if exported_count:
        print(f"Exported {exported_count} books")

    print(f"Exporting lists:")

    # Write list by languages
    print(f"  - language index")
    write_markdown_list(
        create_condition_list(
            catalogue,
            condition=lambda b_id, b_type, b: b.get("language", []),
            list_data={
                "name": "languages",
                "title": "Index by language",
                "subtitle": "",
                "description": "",
            },
            sort_key=lambda b: b.get("purchase_date", "0000-00-00"),
            sort_reverse=True,
            group_info={
                "name_function": lambda group: f'in_{group.lower().replace(" ", "_")}',
                "exclude_function": lambda item: len(item["books"]) < 1,
                "link_function": lambda group: f"/books/in_{group.lower().replace(' ', '_')}/",
                "subtitle_function": lambda group: f"Books and audiobooks in {group.title()}",
                "title_function": lambda group: f"Language: {group.title()}",
            },
            group_sort_key=lambda item: item["group"],
            show_group_size=True,
            include_book_titles_header=False,
        ),
        list_output_folder=list_output_folder,
        include_items=True,
        make_sublists=True,
        include_covers=False,
        include_covers_in_sublists=True,
        remove_count_from_sublists=True,
    )

    # Write list by themes
    print(f"  - subject index")
    write_markdown_list(
        create_condition_list(
            catalogue,
            condition=lambda b_id, b_type, b: b.get("theme", "").title(),
            list_data={
                "name": "subjects",
                "title": "Index by subject",
                "subtitle": "",
                "description": "",
            },
            sort_key=lambda b: b.get("purchase_date", "0000-00-00"),
            sort_reverse=True,
            group_info={
                "name_function": lambda group: f'about_{group.lower().replace(" ", "_")}',
                "exclude_function": lambda item: len(item["books"]) < 1,
                "link_function": lambda group: f"/books/about_{group.lower().replace(' ', '_')}/",
                "subtitle_function": lambda group: subtitles_by_value.get(
                    group.lower(), None
                ),
            },
            group_sort_key=lambda item: item["group"],
            show_group_size=True,
            include_book_titles_header=False,
        ),
        list_output_folder=list_output_folder,
        include_items=True,
        make_sublists=True,
        include_covers=False,
        include_covers_in_sublists=True,
        remove_count_from_sublists=True,
    )

    # Write list by authors
    print(f"  - authors index")
    write_markdown_list(
        create_condition_list(
            catalogue,
            condition=lambda b_id, b_type, b: b.get("authors", []),
            list_data={
                "name": "authors",
                "title": "Index by author",
                "subtitle": "",
                "description": "",
            },
            sort_key=lambda b: b.get("purchase_date", "0000-00-00"),
            sort_reverse=True,
            group_info={
                "exclude_function": lambda item: len(item["books"]) < 1,
            },
            group_sort_key=lambda item: item["group"],
            show_group_size=True,
            include_book_titles_header=False,
        ),
        list_output_folder=list_output_folder,
        include_items=True,
        include_covers=False,
    )

    # Write lists of books with multiple formats
    print(f"  - multiple formats")
    write_markdown_list(
        create_condition_list(
            catalogue,
            condition=lambda b_id, b_type, b: b.get("multiple_formats")
            and len(b["multiple_formats"]) >= 2
            and b_type == "audiobook",
            list_data={
                "name": "multiple_formats",
                "title": "Multiple formats",
                "subtitle": "Books in paper and audiobook formats",
                "description": "When I really enjoy an audiobook, I often buy the paper version too. This list contains books I own in both formats.",
            },
        ),
        list_output_folder=list_output_folder,
        include_items=True,
    )

    # Condition function for the timeline list
    def condition_for_timeline(book_id, book_type, book):
        if date := book.get("purchase_date", book.get("list_date", "1900-01-01")):
            date_str = dt.date.fromisoformat(date).strftime("%Y-%m-%d")
            return date_str[:7]
        return "1900-01"

    # Create the timeline list
    print(f"  - timeline")
    write_markdown_list(
        create_condition_list(
            catalogue,
            condition=condition_for_timeline,
            list_data={
                "name": "timeline",
                "title": "Book timeline",
                "subtitle": "Books in the order I bought them",
                "description": "",
            },
            sort_key=lambda b: b.get("purchase_date", "0000-00-00"),
            sort_reverse=True,
            max_books=None,
            group_info={
                "title_function": lambda group: f"{month_name[int(group.split('-')[1])]} {group.split('-')[0]}",
                "exclude_function": lambda item: item["group"] == "1900-01",
            },
            group_sort_key=lambda item: item["group"],
            group_sort_reverse=True,
        ),
        list_output_folder=list_output_folder,
        include_items=True,
    )

    # Write lists of most recent books
    print(f"  - recent books")
    write_markdown_list(
        create_condition_list(
            catalogue,
            condition=lambda b_id, b_type, b: True,
            list_data={
                "name": "recent",
                "title": "Recent Books",
                "subtitle": "The most recent books I've added to my library",
                "description": "",
            },
            sort_key=lambda b: b.get("purchase_date", "0000-00-00"),
            sort_reverse=True,
            max_books=8,
        ),
        list_output_folder=list_output_folder,
        include_items=True,
    )

    # Write lists of signed books
    print(f"  - signed books")
    write_markdown_list(
        create_condition_list(
            catalogue,
            condition=lambda b_id, b_type, b: b.get("signed"),
            list_data={
                "name": "signed",
                "title": "Signed Books",
                "subtitle": "Books signed by the author",
                "description": "",
            },
            sort_key=lambda b: b.get("purchase_date", "0000-00-00"),
        ),
        list_output_folder=list_output_folder,
        include_items=True,
    )
