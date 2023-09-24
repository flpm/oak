import calendar
import typer
from rich import print
from collections import defaultdict, Counter

from .utils.file import read_catalogue


def generate_stats(stat_type):
    """
    Generate stats.

    Parameters
    ----------
    stat_type : str
        The type of stats to generate.
    """

    catalogue = read_catalogue()
    print(f"Books in catalogue: {len(catalogue)} books.")
    print(f"Books by source:")
    source_counter = Counter()
    attribute_counters = defaultdict(Counter)
    for book_id, book_types in catalogue.items():
        for book_type, book in book_types.items():
            if book_type == "audiobook_sample":
                source = f"{book['source']} sample"
            else:
                source = book["source"]
            source_counter[source] += 1
            attribute_counters[source].update(
                [key for key, value in book.items() if value]
            )
    for value, count in source_counter.items():
        print(f"  - {value}: {count}")
    if stat_type == "attributes":
        print(f"Attributes by source:")
        all_counters = set()
        for c in attribute_counters.values():
            all_counters = all_counters.union(c.keys())
        for attribute in sorted(all_counters):
            print(f"  - {attribute}: ", end="")
            for source, counter in attribute_counters.items():
                if source == "Audible sample":
                    continue
                if attribute in counter:
                    print(f"{source} ({counter[attribute]})", end="; ")
            print("")
    elif stat_type == "format":
        print(f"Books by format:")
        format_counter = Counter()
        for book_id, book_types in catalogue.items():
            for book_type, book in book_types.items():
                format_counter[book["format"]] += 1
        for value, count in format_counter.items():
            print(f"  - {value if value else 'Unknown'}: {count}")

    elif stat_type == "language":
        print(f"Books by language:")
        language_counter = Counter()
        for book_id, book_types in catalogue.items():
            for book_type, book in book_types.items():
                language_counter.update(book.get("language", ["Unknownn"]))
        for value, count in language_counter.items():
            print(f"  - {value if value else 'Unknown'}: {count}")
    elif stat_type == "authors":
        print(f"Top authors:")
        author_counter = Counter()
        for book_id, book_types in catalogue.items():
            for book_type, book in book_types.items():
                author_counter.update(book.get("authors", ["Unknownn"]))
        for value, count in author_counter.most_common(10):
            print(f"  - {value if value else 'Unknown'}: {count}")

    elif stat_type == "orders":
        print(f"Orders:")
        orders_counter = Counter()
        for book_id, book_types in catalogue.items():
            for book_type, book in book_types.items():
                if book.get("order"):
                    orders_counter["Books with order data"] += 1
        for value, count in orders_counter.most_common(10):
            print(f"  - {value if value else 'Unknown'}: {count}")

    elif stat_type == "date":
        print(f"Purchase dates:")
        year_counter = Counter()
        purchase_date_counter = Counter()
        for book_id, book_types in catalogue.items():
            for book_type, book in book_types.items():
                if purchase_date := book.get("purchase_date"):
                    purchase_date_counter[f"{book_type} with purchase_date"] += 1
                    year = purchase_date[:4]
                    year_counter[year] += 1

        for value, count in sorted(year_counter.most_common(), reverse=True):
            print(f"  - {value if value else 'Unknown'}: {count}")
        for value, count in purchase_date_counter.most_common():
            print(f"  - {value if value else 'Unknown'}: {count}")
        print(f"Listening dates:")
        year_counter = Counter()
        listening_date_counter = Counter()
        for book_id, book_types in catalogue.items():
            for book_type, book in book_types.items():
                if listening_date := book.get("listening_date"):
                    listening_date_counter[f"{book_type} with listening_date"] += 1
                    year = listening_date[:4]
                    year_counter[year] += 1

        for value, count in sorted(year_counter.most_common(10), reverse=True):
            print(f"  - {value if value else 'Unknown'}: {count}")
        for value, count in listening_date_counter.most_common():
            print(f"  - {value if value else 'Unknown'}: {count}")

    elif stat_type == "city":
        print(f"Locations:")
        purchase_city_counter = Counter()
        location_counter = Counter()
        for book_id, book_types in catalogue.items():
            for book_type, book in book_types.items():
                if purchase_city := book.get("location"):
                    purchase_city_counter[f"{book_type} with purchase location"] += 1
                    location_counter[purchase_city] += 1

        for value, count in sorted(purchase_city_counter.most_common(), reverse=True):
            print(f"  - {value if value else 'Unknown'}: {count}")
        for value, count in location_counter.most_common():
            print(f"  - {value if value else 'Unknown'}: {count}")

    elif stat_type == "timeline":
        print(f"Timeline:")
        timeline = defaultdict(lambda: defaultdict(list))
        for book_id, book_types in catalogue.items():
            for book_type, book in book_types.items():
                if book_type == "audiobook_sample":
                    continue
                date = book.get("purchase_date") or book.get("listening_date")
                if not date:
                    continue
                year, month, _ = date.split("-")
                book["book_type"] = book_type
                timeline[year][month].append(book)

        for year, months in sorted(timeline.items()):
            print(f"  - {year}:")
            for month, books in sorted(months.items()):
                print(f"    - [magenta]{calendar.month_name[int(month)]}[/magenta]:")
                for book in books:
                    print(
                        f"      - [green]{book['book_type']}[/green] [yellow]{book['format']}[/yellow] {book['title']}"
                    )
