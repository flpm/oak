import csv
from collections import defaultdict, Counter

from .audible_html import (
    get_book_detail_html,
    get_content_format,
    get_topics,
    find_book_details,
    get_cover_image,
)


def add_audible_purchase_date(audiobooks):
    """
    Add the purchase date for each audiobook.

    Parameters
    ----------
    audiobooks : dict
        A dictionary of audiobooks with the ASIN as the key.

    Returns
    -------
    dict
        The modified dictionary of audiobooks.
    """

    audible_purchase_history = "./raw/audible/data/Audible.PurchaseHistory.csv"

    with open(audible_purchase_history) as fp:
        audible_purchases = csv.DictReader(fp)
        for entry in audible_purchases:
            asin = entry["Asin"]
            if asin not in audiobooks:
                continue
            book = audiobooks[asin].get("audiobook")
            if book:
                book["purchase_date"] = entry["OrderFulfillDate"].split("T")[0]

    return audiobooks


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
                book["book_id"] = asin
                book["type"] = book_type
                book["full_title"] = book["full_title"].replace(" (Unabridged)", "")
                title_parts = book["full_title"].split(": ")
                if len(title_parts) == 2:
                    book["title"] = title_parts[0].strip()
                    book["subtitle"] = title_parts[1].strip()
                elif len(title_parts) > 2:
                    book["title"] = ": ".join(title_parts[0:-1]).strip()
                    book["subtitle"] = title_parts[-1].strip()
                else:
                    book["title"] = book["full_title"].strip()
                    book["subtitle"] = None
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

    audiobooks = add_audible_purchase_date(audiobooks)
    for asin, book_info in audiobooks.items():
        for book_type, book in book_info.items():
            book["listening"]["duration"] = round(
                book["listening"]["duration"] / 1000, ndigits=0
            )
            book["listening_date"] = book["listening"]["first_time"].split("T")[0]

    return audiobooks


def enrich_audible(catalogue):
    """
    Enrich audiobooks using data from the Audible website.

    Parameters
    ----------
    catalogue : dict
        The current catalogue.

    Returns
    -------
    dict
        The modified catalogue.
    """

    # Get details for each book
    book_count = 0
    errors = Counter()
    for book_types in catalogue.values():
        for book in book_types.values():
            if book["source"] != "Audible":
                continue

            book_count += 1
            soup, errors = get_book_detail_html(book, errors)
            if not soup:
                continue

            book["format"] = get_content_format(soup) or book["format"]
            book["topics"] = get_topics(soup)

            try:
                for key, value in find_book_details(soup).items():
                    book[key] = value
                    if key == "duration" and (
                        not "length" in book
                        or not book["length"]
                        or book["length"] == "0"
                        or book["length"] == value / 1000
                    ):
                        book["length"] = value
            except RuntimeError as e:
                errors["Books missing details"] += 1

            book["cover_filename"], errors = get_cover_image(book, soup, errors)
            if not book["cover_filename"]:
                errors["Books missing cover"] += 1

            print(".", end="", flush=True)
    print("")

    print(f"Error summary:")
    for error, count in errors.items():
        print(f"  - {error}: {count}")

    return catalogue, book_count
