import datetime as dt
from collections import defaultdict
from inspect import cleandoc
from calendar import month_name
from .file import include_book

include_themes = {
    "archaeology": ["ancient history"],
    "epigraphy": ["ancient history", "archaeology"],
    "typography": ["design"],
    "anxiety": ["psychology"],
    "autism": ["psychology"],
    "software": ["engineering"],
    "ancient history": ["history"],
    "historical novel": ["novel"],
    "math": ["science"],
}

subtitles_by_value = {
    # Themes
    "ancient history": "Books from the beginning of recorded human history to the Early Middle Ages",
    "anthropology": "Books about the study of human behaviour and societies",
    "anxiety": "Books about anxiety and how to deal with it",
    "archaeology": "Books about the study of history through the recovery and analysis of material culture",
    "art history": "Books about the study of art in its historical context",
    "autism": "Books about autism and related topics",
    "biography": "Books about the life of a person",
    "business": "Books about business and related topics",
    "ciphers": "Books about ciphers before modern cryptography",
    "computational design": "Books about graphic design and art created using code",
    "crime Fiction": "Books about fictionale stories involving a crime",
    "data": "Books about data and data analysis",
    "design": "Books about design, including methods, approaches and techniques",
    "drama": "Books about drama, including plays and screenplays",
    "economics": "Books about economics, including game theory and behavioural economics",
    "engineering": "Books about engineering, including software engineering and programming languages",
    "entrepreneurship": "Books about entrepreneurship and related topics",
    "epigraphy": "Books about the study of inscriptions and writing systems",
    "essays": "Books about essays, including collections of essays",
    "fantasy": "Books about fantasy, including fantasy novels",
    "financial markets": "Books about financial markets and related topics",
    "game of go": "Books about the game of go, including problems, strategy and game records",
    "games": "Books about games in general, including puzzles",
    "graphic novels": "Graphic novels, including comics",
    "graphs": "Books about graphs and graph theory",
    "historical novel": "Novels set in the past, including historical fiction",
    "history": "Books about history in general",
    "humor": "Books about humor and comedy",
    "kids": "Books for kids",
    "labyrinths": "Books about labyrinths, including mazes",
    "learning latin": "Books about learning the Latin language",
    "linguistics": "Books about linguistics, including the history of languages",
    "logic": "Books about logic and logical thinking",
    "magic": "Books about magic, including tricks, performance and the history of magic",
    "math": "Books about mathematics in general, including probability and statistics",
    "music": "Books about music and musicians",
    "mythology": "Books about mythology, including the study of myths and the history of myths",
    "new york": "Books about New York City",
    "novel": "Novels, including historical novels",
    "paris": "Books about the city of Paris",
    "personal growth": "Books about personal growth and related topics",
    "philosophy": "Books about philosophy in general, including the history of philosophy",
    "photography": "Books about photography and photographers",
    "poetry": "Books about poetry, including collections of poems",
    "presentation": "Books about presentation skills",
    "psychology": "Books about psychology in general",
    "puzzles": "Books about puzzles and other games",
    "reading": "Books about reading, including critical reading and literature analysis",
    "role-playing games": "Books about tabletop role-playing games",
    "science": "Books about science in general",
    "security": "Books about security, intelligence and risk",
    "software": "Books about software development and programming languages",
    "typography": "Books about typography and type design",
    "visualization": "Books about data and information visualization",
    "writing": "Books about writing, grammar, and style",
}


def make_list(
    catalogue, list_data, include_audiobook_samples=False, make_subsection_links=True
):
    ordered_data = defaultdict(list)
    for book_types in catalogue.values():
        for book_type, book in book_types.items():
            if not include_audiobook_samples and book_type == "audiobook_sample":
                continue
            entry_type = list_data.get("attribute_type", "str")
            entry = book.get(list_data["attribute"], None)
            if entry:
                if entry_type == "str":
                    for alias_entry in include_themes.get(entry, []) + [entry]:
                        ordered_data[alias_entry].append(book)
                elif entry_type == "list":
                    for element in entry:
                        for alias_element in include_themes.get(element, []) + [
                            element
                        ]:
                            ordered_data[alias_element].append(book)
                else:
                    ValueError(f"Unknown attribute type {entry_type}")

    list_data["index"] = dict()
    list_data["items"] = list()
    description = list()
    for attribute_value, books in sorted(ordered_data.items(), key=lambda x: x[0]):
        included = [book for book in books if include_book(book)]
        sublist_name = f"{list_data.get('index_title_preposition', 'about')} {attribute_value.title()}"
        sublist_address = sublist_name.replace(" ", "_").lower()
        if make_subsection_links:
            description.append(
                f"### [{attribute_value if attribute_value else 'Blank'}](/books/{sublist_address}) ({len(included)})"
            )
        else:
            description.append(
                f"### {attribute_value if attribute_value else 'Blank'} ({len(included)})"
            )
        for book in sorted(included, key=lambda x: x["title"]):
            description.append(
                f"- ({'audio' if book['source'] == 'Audible' else 'paper'}) [{book['title']}](/books/info/{book['book_id']}) by {', '.join(book['authors'])}"
            )
        list_data["index"][attribute_value] = {
            "name": sublist_name,
            "title": f"{list_data['attribute'].capitalize()}: {attribute_value.title()}",  # f"Books {list_data.get('index_title_preposition', 'about')} {attribute_value.title()}",
            "subtitle": subtitles_by_value.get(
                attribute_value,
                f"Books {list_data.get('index_title_preposition', 'about')} {attribute_value.title()}",
            ),
            "description": "\n".join(
                [
                    (
                        f"I have {len(included)} "
                        f"book{'s' if len(included) != 1 else ''} {list_data.get('index_title_preposition', 'about')} {attribute_value.title()} "
                        "in my personal library."
                    ),
                    "",
                    "### Titles:",
                ]
                + [
                    f"- ({'audio' if book['source'] == 'Audible' else 'paper'}) [{book['title']}](/books/info/{book['book_id']}) by {', '.join(book['authors'])}"
                    for book in sorted(included, key=lambda x: x["title"])
                ]
            ),
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

    for attribute_value, books in sorted(ordered_data.items(), key=lambda x: x[0]):
        included = [book for book in books if include_book(book)]
        list_data["items"].append(
            {
                "title": [
                    f"{attribute_value} ({len(included)})",
                    f"/books/{sublist_address}",
                ],
                "books": [
                    book["book_id"]
                    for book in sorted(included, key=lambda x: x["title"])
                ],
            }
        )
    return list_data


def create_language_list(catalogue):
    list_data = {
        "name": "languages",
        "title": "Index by language",
        "items": list(),
        "description": "Go back to the [Bookshelf project](/books) or consult the index by [subject](/books/subjects).",
        "attribute": "language",
        "attribute_type": "list",
        "index_title_preposition": "in",
    }
    return make_list(catalogue, list_data)


def create_theme_list(catalogue):
    list_data = {
        "name": "subjects",
        "title": "Index by subject",
        "items": list(),
        "description": "Go back to the [Bookshelf project](/books) or consult the index by [language](/books/languages).",
        "attribute": "theme",
        "attribute_type": "str",
        "index_title_preposition": "about",
    }
    return make_list(catalogue, list_data)


def create_author_list(catalogue):
    list_data = {
        "name": "authors",
        "title": "Index by author",
        "items": list(),
        "description": "Go back to the [Bookshelf project](/books).",
        "attribute": "authors",
        "attribute_type": "list",
        "index_title_preposition": "by",
    }
    return make_list(catalogue, list_data, make_subsection_links=False)


def create_recent_list(catalogue, number_of_books=10):
    if number_of_books is None:
        list_data = {
            "name": "timeline",
            "title": "Book Timeline",
            "subtitle": f"Books ordered by date of acquisition",
            "items": list(),
            "description": "",
            "attribute": "purchase_date",
        }
    else:
        list_data = {
            "name": "recent",
            "title": "Recent acquisitions",
            "subtitle": f"The last {number_of_books} books added to the bookshelf",
            "items": list(),
            "description": "",
            "attribute": "purchase_date",
        }

    ordered_data = list()
    for book_types in catalogue.values():
        for book_type, book in book_types.items():
            if book_type == "audiobook_sample":
                continue
            if not include_book(book):
                continue
            if date := book.get("purchase_date", book.get("list_date", "1900-01-01")):
                date_str = dt.date.fromisoformat(date).strftime("%Y-%m-%d")
                ordered_data.append((date_str, book))
    ordered_data.sort(key=lambda x: x[0], reverse=True)
    recent_description = list()

    if number_of_books is None:
        pass
    else:
        recent_description.append(
            f"### Last {number_of_books} books added to the bookshelf:"
        )
    recent_book_list = list()
    timeline = defaultdict(lambda: defaultdict(list))
    for date, book in ordered_data[:number_of_books]:
        if number_of_books is not None:
            recent_description.append(
                f"- {date} ({book['format']} in {book.get('theme', 'others').title()}) [{book['title']}](/books/info/{book['book_id']}) by {', '.join(book['authors'])}"
            )
        recent_book_list.append(book["book_id"])
        if number_of_books is None:
            year, month, day = date.split("-")
            timeline[year][month].append(book)
    list_data["description"] = "\n".join(recent_description)

    if number_of_books is None:
        for year, months in timeline.items():
            if year == "1900":
                continue
            for month, books in months.items():
                month_description = [
                    "Book title:" if len(books) == 1 else "Book titles:",
                ]
                for book in books:
                    month_description.append(
                        f"- ({book['format']} in {book.get('theme', 'others').title()}) [{book['title']}](/books/info/{book['book_id']}) by {', '.join(book['authors'])}"
                    )
                list_data["items"].append(
                    {
                        "title": [f"{month_name[int(month)]} {year}"],
                        "description": "\n".join(month_description),
                        "books": [book["book_id"] for book in books],
                    }
                )
    else:
        list_data["items"].append(
            {
                "title": None,
                "description": None,
                "books": recent_book_list,
            }
        )
    return list_data
