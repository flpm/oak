"""Import data from the iPhone Bookshelf app."""

import csv
import base64

from bs4 import BeautifulSoup
from collections import defaultdict

from .file import save_cover_image
from .lang import land_code_to_name


def import_from_bookshelf(export_date):
    """Import books from files exported from Bookshelf.

    Parameters
    ----------
    export_date : str
        The date of the export in the format YYYY-MM-DD.

    Returns
    -------
    dict
        A dictionary of books with the ISBN as the key.
    """
    csv_filename = f"./raw/bookshelf/Bookshelf-{export_date}.csv"
    html_filename = f"./raw/bookshelf/Bookshelf-{export_date}.html"
    books = dict()

    # Read the CSV file and reformat the keys
    with open(csv_filename, "r") as fp:
        reader = csv.DictReader(fp)
        for entry in reader:
            book_info = {"source": "Bookshelf"}
            title = entry.get("Title")
            for key, value in entry.items():
                key = key.replace(" ", "_").lower()
                if key not in (
                    "categories",
                    "description",
                    "published_at",
                    "authors",
                    "title",
                    "subtitle",
                    "full_title",
                    "language",
                    "page_count",
                    "isbn",
                    "format",
                    "publisher",
                ):
                    continue
                if key == "categories":
                    value = value.split(",")
                    key = "topics"
                elif key == "authors":
                    value = value.split(",")
                elif key == "published_at":
                    key = "date_published"
                elif key == "description":
                    value = "\n".join(
                        [i.strip() for i in value.split("\n") if i.strip()]
                    )
                elif key == "subtitle":
                    if not value:
                        value = None
                elif key == "isbn":
                    book_info["book_id"] = value
                elif key == "language":
                    value = land_code_to_name(value)
                elif key == "format":
                    value = value.title()
                elif key == "page_count":
                    key = "length"
                    value = f"{value} pages"
                book_info[key] = value
            if "full_title" not in book_info:
                book_info["full_title"] = (
                    f'{book_info["title"]}: {book_info["subtitle"]}'
                    if book_info.get("subtitle")
                    else book_info["title"]
                )
            books[book_info["title"]] = book_info

    # Read the HTML file to extract the embedded cover images
    with open(html_filename, "r") as fp:
        html_doc = fp.read()

    soup = BeautifulSoup(html_doc, "html.parser")
    results = defaultdict(dict)
    for row in soup.find_all("tr"):
        cover_image = cover_type = None
        for cell in row.children:
            if cell.name is None:
                continue
            if "td-image" in cell.get("class"):
                (media_type, data, *_) = cell.img["src"].split(",")
                image_type = media_type.split(";")[0].split("/")[-1]
                if image_type in ("false", "jpeg"):
                    cover_type = "jpg"
                else:
                    cover_type = image_type
                cover_image = data
            if "td-book" in cell.get("class"):
                title = cell.h2.string
                book = books.get(title)
                if book and book.get("isbn"):
                    isbn = book["isbn"]
                else:
                    raise RuntimeError(f"ISBN not found for {title}")
                img_filename = f"{isbn}.{cover_type}"
                decoded_cover = base64.b64decode(cover_image)
                save_cover_image(decoded_cover, img_filename)
                book["cover_filename"] = img_filename
                results[isbn]["book"] = book
    return results
