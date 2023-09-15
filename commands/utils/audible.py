import csv
from collections import defaultdict

from .file import read_catalogue, save_catalogue


def import_from_audible():
    """
    Import books from the Audible listening history.

    Returns
    -------
    dict
        A dictionary of books with the ASIN as the key.
    """

    book_key_map = {
        "Title": "full_title",
        "Asin": "asin",
        "BookLength": "length",
        "AudioType": "type",
        "AsinOwned": "owned",
    }

    audible_listening_history = "./raw/audible/data/Audible.Listening.csv"
    audiobooks = defaultdict(dict)

    with open(audible_listening_history) as fp:
        audible_history = csv.DictReader(fp)
        for entry in audible_history:
            asin = entry["Asin"]
            title = entry["Title"]
            book_type = entry["AudioType"]
            if book_type == "FullTitle":
                book_type = "audiobook"
            elif book_type == "CatalogSample":
                book_type = "audiobook_sample"
            elif not book_type:
                book_type = "audiobook"
            else:
                raise ValueError(f"Undefined book type for {title}")

            book = audiobooks[asin].get(book_type, dict())
            if not book:
                book = {
                    book_key_map[k]: v for k, v in entry.items() if k in book_key_map
                }
                title_parts = book["full_title"].split(": ")
                if len(title_parts) == 2:
                    book["title"] = title_parts[0].strip()
                    book["subtitle"] = title_parts[1].strip()
                else:
                    book["title"] = book["full_title"].strip()
                    book["subtitle"] = None
                book["type"] = book_type
                book["format"] = "Audiobook"
                book["listening"] = {"duration": 0}
                book["link"] = f"https://www.audible.com/pd/{asin}"
                book["source"] = "Audible"
                audiobooks[asin][book_type] = book

            if book["listening"].get("first_time"):
                book["listening"]["first_time"] = min(
                    entry["StartDate"], book["listening"]["first_time"]
                )
            else:
                book["listening"]["first_time"] = entry["StartDate"]
            if book["listening"].get("last_time"):
                book["listening"]["last_time"] = max(
                    entry["EndDate"], book["listening"]["last_time"]
                )
            else:
                book["listening"]["last_time"] = entry["EndDate"]

            book["listening"]["duration"] += int(entry["EventDuration"])

    for asin, book_info in audiobooks.items():
        for book_type, book in book_info.items():
            book["listening"]["duration"] = round(
                book["listening"]["duration"] / 1000, ndigits=0
            )

    return audiobooks
