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
            book_info = {"source": "Bookshelf", "owned": True}
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
                    value = [i.title() if i.isupper() else i for i in value.split(",")]
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
                    if not value or value == "ebook":
                        value = "Paperback"
                    value = value.title()
                elif key == "page_count":
                    key = "length"
                    value = f"{value} pages"
                book_info[key] = value
            if "full_title" not in book_info:
                original_title = book_info["title"]
                title_parts = book_info["title"].split(": ")
                if len(title_parts) == 2:
                    book_info["title"] = title_parts[0].strip()
                    book_info["subtitle"] = title_parts[1].strip()
                elif len(title_parts) > 2:
                    book_info["title"] = ": ".join(title_parts[0:-1]).strip()
                    book_info["subtitle"] = title_parts[-1].strip()
                if book_info["title"].isupper():
                    book_info["title"] = book_info["title"].title()
                if book_info["subtitle"] and book_info["subtitle"].isupper():
                    book_info["subtitle"] = book_info["subtitle"].title()
                book_info["full_title"] = (
                    f'{book_info["title"]}: {book_info["subtitle"]}'
                    if book_info.get("subtitle")
                    else book_info["title"]
                )
            book_info["type"] = "book"
            books[original_title] = book_info

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
                if book:
                    if book.get("book_id"):
                        isbn = book["book_id"]
                    else:
                        print(f"ISBN not found for {title}")
                else:
                    print(f"Book not found in catalog: {title}")
                    continue
                img_filename = f"{isbn}.{cover_type}"
                decoded_cover = base64.b64decode(cover_image)
                save_cover_image(decoded_cover, img_filename)
                book["cover_filename"] = img_filename
                results[isbn]["book"] = book

    # Some special corrections for errors in the Bookshelf data

    results["9788420482279"]["book"]["language"] = [
        "Spanish"
    ]  # Fix incorrect language in "Que me Quieres Amor"
    results["9783931141967"]["book"]["language"] = [
        "English"
    ]  # Fix incorrect language in "Francesca Woodman"
    results["9788501053145"]["book"]["language"] = [
        "Portuguese"
    ]  # Fix incorrect language in "Suor"

    # Harmonize Tolkien name spellings
    for book_types in results.values():
        for book_id, book in book_types.items():
            for author in book["authors"]:
                if author in ("J.R.R. Tolkien", "J R R Tolkien"):
                    book["authors"].remove(author)
                    book["authors"].append("J. R. R. Tolkien")

    # Fix author in Relentless
    results["9780981912189"]["book"]["authors"] = ["Go Game Guru"]

    # Fix authors in Graded Go Problems for Dan Players
    results["9784906574629"]["book"]["authors"] = ["Masaru Aoki"]
    results["9784906574629"]["book"]["publisher"] = "Kiseido Publishing Company"
    results["9784906574612"]["book"]["authors"] = ["Masaru Aoki"]
    results["9784906574612"]["book"]["publisher"] = "Kiseido Publishing Company"

    return results
