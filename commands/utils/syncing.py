### Sync command utils ###

import os
from collections import defaultdict

from rich import print

from .file import read_markdown, write_markdown_book, write_markdown_list


def load_lists_from_folder(folder):
    """
    Load lists from a folder.

    Parameters
    ----------
    folder : str
        The folder to load lists from.

    Returns
    -------
    dict
        The lists in the folder.
    """
    result = dict()
    for filename in os.listdir(folder):
        if filename.endswith(".md"):
            list_data = read_markdown(f"{folder}/{filename}")
            list_id = filename[:-3]
            result[list_id] = list_data
    return result


def load_books_from_folder(folder):
    """
    Load books from a folder.

    Parameters
    ----------
    folder : str
        The folder to load books from.

    Returns
    -------
    dict
        The books in the folder.
    """
    result = dict()
    for filename in os.listdir(folder):
        if filename.endswith(".md"):
            book = read_markdown(f"{folder}/{filename}")
            book_id = filename[:-3]
            book_type = book["type"]
            result[book_id] = book
    return result


def compare_folders(source_folder, dest_folder, item_type="books"):
    """
    Compare two folders.

    Parameters
    ----------
    source_folder : str
        The first folder.
    dest_folder : str
        The second folder.
    type : str, optional
        The type of files to compare, by default "book"

    Returns
    -------
    dict
        A dictionary of books that are in one folder but not the other.
    """
    result = defaultdict(list)

    if item_type == "books":
        source_folder = load_books_from_folder(source_folder)
        dest_folder = load_books_from_folder(dest_folder)
    elif item_type == "lists":
        source_folder = load_lists_from_folder(source_folder)
        dest_folder = load_lists_from_folder(dest_folder)
    else:
        raise ValueError(f"Unknown type: {item_type}")

    print(f"  - source folder: {len(source_folder)} {item_type}.")
    print(f"  - dest folder: {len(dest_folder)} {item_type}.")

    for item_key, item in source_folder.items():
        if item_key not in dest_folder:
            result["add"].append((item_key, item))
        else:
            result["update"].append((item_key, item))
    for item_key, item in dest_folder.items():
        if item_key not in source_folder:
            result["delete"].append((item_key, item))
            print(
                f"  - [bold yellow]{item.get('title', item_key)}[/bold yellow] is in dest but not source."
            )
    return result


def delete_files(delete_list, output_folder):
    """
    Delete files for books that are in the output_folder but not in the list.

    Parameters
    ----------
    delete_list : list
        List of books to delete.
    output_folder : str
        The folder to delete files from.

    Returns
    -------
    int
        The number of files deleted.
    """
    removed = 0
    for item_id, *_ in delete_list:
        filename = f"{output_folder}/{item_id}.md"
        removed += 1
        os.remove(filename)
    return removed


def add_files(add_list, output_foler, item_type="books"):
    """
    Add files for books that are in the list but not in the output_folder.

    Parameters
    ----------
    add_list : dict
        The list of books to add to the folder.
    output_folder : str
        The folder to create files in.

    Returns
    -------
    int
        The number of files created.
    """
    return update_files(add_list, output_foler, item_type=item_type)


def update_files(update_list, output_foler, item_type="books"):
    """
    Update files for books that are in the list and in the output_folder.

    Parameters
    ----------
    update_list : dict
        The list of books to update in the folder.
    output_folder : str
        The folder to update files in.
    item_type : str, optional
        The type of files to update, by default "books"

    Returns
    -------
    int
        The number of files updated.
    """
    count = 0
    for item_id, item in update_list:
        filename = f"{output_foler}/{item_id}.md"
        count += 1
        if item_type == "books":
            write_markdown_book(item, f"{item_id}.md", output_foler)
        if item_type == "lists":
            write_markdown_list(item, f"{item_id}.md", output_foler)

    return count
