"""Export book catalogue to Markdown files"""

from rich import print
from .utils.file import read_catalogue, write_markdown_book, write_markdown_list
from .utils.exporting import create_language_list, create_theme_list


def export_markdown(output_folder):
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
    exported_count = 0
    skipped_count = 0
    catalogue = read_catalogue()
    for book_id, book_info in catalogue.items():
        for book_type, book in book_info.items():
            if book_type == "audiobook_sample":
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
    write_markdown_list(lang_list, list_output_folder=list_output_folder)
    print(f"  - languages")

    print(f"  - subjects")
    write_markdown_list(
        create_theme_list(catalogue), list_output_folder=list_output_folder
    )
