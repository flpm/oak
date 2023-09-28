from collections import defaultdict


def include_book(book):
    return book.get("authors") and book.get("title") and book.get("cover_filename")


def make_list(catalogue, list_data, include_audiobook_samples=False, index=False):
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
    list_data["index"] = dict()
    if index:
        description = list()
        for attribute_value, books in sorted(ordered_data.items(), key=lambda x: x[0]):
            included = [book for book in books if include_book(book)]
            sublist_name = f"{list_data.get('index_title_preposition', 'about')} {attribute_value.title()}"
            sublist_address = sublist_name.replace(" ", "_").lower()
            description.append(
                f"- [{attribute_value}](/books/{sublist_address}) ({len(included)})"
            )
            list_data["index"][attribute_value] = {
                "name": sublist_name,
                "title": f"Books {list_data.get('index_title_preposition', 'about')} {attribute_value.title()}",
                "subtitle": (
                    f"There {'are' if len(included) != 1 else 'is'} {len(included)} "
                    f"book{'s' if len(included) != 1 else ''} {list_data.get('index_title_preposition', 'about')} {attribute_value.title()}"
                ),
                "description": "",
                "items": [
                    {
                        "title": None,
                        "books": [
                            book["book_id"]
                            for book in sorted(included, key=lambda x: x["title"])
                        ],
                    }
                ],
            }
        list_data["description"] = (
            "\n"
            + "\n".join(description)
            + "\n\nGo back to the [Bookshelf project](/books)."
        )
    else:
        for attribute_value, books in sorted(ordered_data.items(), key=lambda x: x[0]):
            included = [book for book in books if include_book(book)]
            list_data["items"].append(
                {
                    "title": f"{attribute_value} ({len(included)})",
                    "books": [
                        book["book_id"]
                        for book in sorted(included, key=lambda x: x["title"])
                    ],
                }
            )
    return list_data


def create_language_list(catalogue, index=False):
    list_data = {
        "name": "languages",
        "title": "Index by language",
        "items": list(),
        "description": "Go back to the [Bookshelf project](/books) or consult the index by [subject](/books/subjects).",
        "attribute": "language",
        "attribute_type": "list",
        "index_title_preposition": "in",
    }
    return make_list(catalogue, list_data, index=index)


def create_theme_list(catalogue, index=False):
    list_data = {
        "name": "subjects",
        "title": "Index by subject",
        "items": list(),
        "description": "Go back to the [Bookshelf project](/books) or consult the index by [language](/books/languages).",
        "attribute": "theme",
        "attribute_type": "str",
        "index_title_preposition": "about",
    }
    return make_list(catalogue, list_data, index=index)
