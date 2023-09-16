import typer
from collections import defaultdict, Counter

from .utils.file import read_catalogue


def generate_stats():
    """Generate stats."""

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
    print(f"Books by format:")
    format_counter = Counter()
    for book_id, book_types in catalogue.items():
        for book_type, book in book_types.items():
            format_counter[book["format"]] += 1
    for value, count in format_counter.items():
        print(f"  - {value if value else 'Unknown'}: {count}")
    print(f"Books by language:")
    language_counter = Counter()
    for book_id, book_types in catalogue.items():
        for book_type, book in book_types.items():
            language_counter.update(book.get("language", ["Unknownn"]))
    for value, count in language_counter.items():
        print(f"  - {value if value else 'Unknown'}: {count}")
    print(f"Top authors:")
    author_counter = Counter()
    for book_id, book_types in catalogue.items():
        for book_type, book in book_types.items():
            author_counter.update(book.get("authors", ["Unknownn"]))
    for value, count in author_counter.most_common(10):
        print(f"  - {value if value else 'Unknown'}: {count}")
