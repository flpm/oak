from collections import defaultdict


def make_list(catalogue, list_data, include_audiobook_samples=False):
    ordered_data = defaultdict(list)
    for book_types in catalogue.values():
        for book_type, book in book_types.items():
            if not include_audiobook_samples and book_type == "audiobook_sample":
                continue
            entry_type = list_data.get("attribute_type", "str")
            entry = book.get(list_data["attribute"], None)
            if entry:
                if entry_type == "str":
                    ordered_data[entry].append(book)
                elif entry_type == "list":
                    for element in entry:
                        ordered_data[element].append(book)
                else:
                    ValueError(f"Unknown attribute type {entry_type}")
    for attribute_value, books in sorted(ordered_data.items(), key=lambda x: x[0]):
        list_data["items"].append(
            {
                "title": f"{attribute_value} ({len(books)})",
                "books": [
                    book["book_id"] for book in sorted(books, key=lambda x: x["title"])
                ],
            }
        )
    return list_data


def create_language_list(catalogue):
    list_data = {
        "name": "languages",
        "title": "Books by language",
        "items": list(),
        "description": "Books by language",
        "attribute": "language",
        "attribute_type": "list",
    }
    return make_list(catalogue, list_data)


def create_theme_list(catalogue):
    list_data = {
        "name": "subjects",
        "title": "Books by subject",
        "items": list(),
        "description": "Books by subject",
        "attribute": "theme",
        "attribute_type": "str",
    }
    return make_list(catalogue, list_data)
