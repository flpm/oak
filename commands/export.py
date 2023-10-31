"""Export book catalogue to Markdown files"""

import os
from rich import print
from .utils.file import (
    read_catalogue,
    write_markdown_book,
    write_markdown_list,
    include_book,
)
from .utils.exporting import (
    create_language_list,
    create_theme_list,
    create_author_list,
    create_recent_list,
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

    lang_list = create_language_list(catalogue)
    print(f"  - languages index")
    write_markdown_list(
        lang_list,
        list_output_folder=list_output_folder,
        include_items=False,
    )
    for sublist_data in lang_list["index"].values():
        print(f"    - {sublist_data['name']}")
        write_markdown_list(
            sublist_data,
            list_output_folder=list_output_folder,
            include_items=True,
        )

    theme_list = create_theme_list(catalogue)
    write_markdown_list(
        theme_list,
        list_output_folder=list_output_folder,
        include_items=False,
    )
    print(f"  - subjects")
    for sublist_data in theme_list["index"].values():
        print(f"    - {sublist_data['name']}")
        if (
            sublist_data["items"]
            and len(sublist_data["items"]) > 0
            and len(sublist_data["items"][0]["books"]) > 0
        ):
            write_markdown_list(
                sublist_data,
                list_output_folder=list_output_folder,
                include_items=True,
            )

    author_list = create_author_list(catalogue)
    write_markdown_list(
        author_list,
        list_output_folder=list_output_folder,
        include_items=False,
    )

    recent_list = create_recent_list(catalogue)
    write_markdown_list(
        recent_list,
        list_output_folder=list_output_folder,
        include_items=True,
    )

    recent_list = create_recent_list(catalogue, number_of_books=None)
    write_markdown_list(
        recent_list,
        list_output_folder=list_output_folder,
        include_items=True,
    )
