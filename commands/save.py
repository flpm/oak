import json
from collections import defaultdict

from .utils.file import save_attributes, read_attributes, read_catalogue, save_catalogue


attributes_storage_file = "./raw/attributes.json"


def save_attributes_file():
    """Save current attribute states so it can be used to enrich the data later on."""
    save_attributes()
    print(f"- saved attribute information to {attributes_storage_file}")


def load_attributes():
    """
    Load attribute information from the storage file.

    This is used to enrich the data with the information that was previously saved.
    """
    catalogue = read_catalogue()
    attributes = read_attributes()
    for book_id, book_types in catalogue.items():
        for book_type, book in book_types.items():
            if book_id in attributes and book_type in attributes[book_id]:
                for key, value in attributes[book_id][book_type].items():
                    book[key] = value
    save_catalogue(catalogue)
    print(f"- loaded attribute information from {attributes_storage_file}")
