"""Export book catalogue to Markdown files"""

from rich import print
from .utils.file import read_catalogue, export_book_to_markdown, read_markdown_book


def export_markdown(output_folder):
    """
    Export books as Markdown files

    Parameters
    ----------
    output_folder : str
        The folder to export the Markdown files to.
    """

    book_output_folder = f"{output_folder}/books"

    print(f"Exporting books to {book_output_folder}")
    exported_count = 0
    skipped_count = 0
    catalogue = read_catalogue()
    for book_id, book_info in catalogue.items():
        for book_type, book in book_info.items():
            if book_type == "audiobook_sample":
                continue
            filename = f"{book['book_id']}.md"
            exported = export_book_to_markdown(book, filename, book_output_folder)
            if exported:
                exported_count += 1
            else:
                skipped_count += 1

    if skipped_count:
        print(f"Skipped {skipped_count} books")
    if exported_count:
        print(f"Exported {exported_count} books")
