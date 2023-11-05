import datetime as dt
from collections import defaultdict
from inspect import cleandoc
from calendar import month_name
from .file import include_book, flat_catalogue

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


def create_condition_list(
    catalogue,
    condition,
    list_data,
    sort_key=None,
    sort_reverse=False,
    max_books=None,
    group_info=None,
    group_sort_key=None,
    group_sort_reverse=False,
    show_group_size=False,
    include_book_titles_header=True,
):
    """
    Create a list of books based on a condition function.

    Parameters
    ----------
    catalogue : dict
        The catalogue
    condition : function
        The condition to apply to each book
    list_data : dict
        The list data.
    sort_key : function, optional
        The sort key to use for the list, by default None
    sort_reverse : bool, optional
        Whether to reverse the sort order, by default False
    max_books : int, optional
        The maximum number of books to include in the list, by default None
    group_info : dict, optional
        The group information, by default None
    group_sort_key : function, optional
        The sort key to use for the groups, by default None
    group_sort_reverse : bool, optional
        Whether to reverse the sort order for the groups, by default False
    show_group_size : bool, optional
        Whether to show the group size, by default False
    include_book_titles_header : bool, optional
        Whether to include the book titles header, by default True

    Returns
    -------
    dict
        The list data
    """
    if not group_info:
        group_info = dict()
    selected_books = defaultdict(list)
    for book_id, book_type, book in flat_catalogue(catalogue):
        if include_book(book) and (group := condition(book_id, book_type, book)):
            if isinstance(group, str):
                selected_books[group].append(book)
            elif isinstance(group, list):
                for element in group:
                    selected_books[element].append(book)
            else:
                selected_books[""].append(book)

    list_data["items"] = list()

    for group, books in selected_books.items():
        if sort_key:
            books.sort(key=sort_key, reverse=sort_reverse)
        if max_books:
            books = books[:max_books]

        description = (
            [
                "Book titles:" if len(books) != 1 else "Book title:",
            ]
            if include_book_titles_header
            else []
        )
        description.extend(
            [
                f"- ({'audio' if book['source'] == 'Audible' else 'paper'}) [{book['title']}](/books/info/{book['book_id']}) by {', '.join(book['authors'])}"
                for book in books
            ]
        )
        item = {
            "name": group_info.get(group, {}).get(
                "name",
                group_info.get("name_function", lambda x: x.lower().replace(" ", "_"))(
                    group
                ),
            ),
            "filename": group_info.get(group, {}).get(
                "filename",
                group_info.get("filename_function", lambda x: None)(group),
            ),
            "group": group,
            "title": [
                group_info.get(group, {}).get(
                    "title", group_info.get("title_function", lambda x: x)(group)
                ),
                group_info.get(group, {}).get(
                    "link", group_info.get("link_function", lambda x: None)(group)
                ),
            ],
            "subtitle": group_info.get(group, {}).get(
                "subtitle", group_info.get("subtitle_function", lambda x: None)(group)
            ),
            "sublist_description": group_info.get(group, {}).get(
                "subtitle",
                group_info.get("sublist_description_function", lambda x: None)(group),
            ),
            "books": [book["book_id"] for book in books],
            "description": "\n".join(description),
        }
        for key, value in group_info.get(group, {}).items():
            item[key] = value

        if exclude_test := group_info.get("exclude_function"):
            if not exclude_test(item):
                list_data["items"].append(item)
        else:
            list_data["items"].append(item)

    if group_sort_key:
        list_data["items"].sort(key=group_sort_key, reverse=group_sort_reverse)

    if show_group_size:
        for item in list_data["items"]:
            item["title"][0] = f"{item['title'][0]} ({len(item['books'])})"

    return list_data
