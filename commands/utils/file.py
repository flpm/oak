"""
Convert the export files from the Bookshelf IOS app into a JSON file for archiving.
"""
import datetime as dt
import json
import yaml
import os
import shutil
from collections import defaultdict

work_catalogue_filename = "./work/catalogue.json"
backup_catalogue_filename = f"./backup/{dt.date.today().isoformat()}_catalogue.json"
output_folder = "./output"
output_cover_folder = "./output/covers"
output_list_folder = "./output/lists"
output_book_folder = "./output/books"
amazon_orders_filename = "./raw/amazon/amazon_orders.json"


def reset_catalogue():
    """
    Reset the catalogue to an empty dictionary.
    """
    print(f"Saving backup of catalogue to {backup_catalogue_filename}")
    try:
        shutil.copyfile(work_catalogue_filename, backup_catalogue_filename)
    except FileNotFoundError:
        pass
    shutil.rmtree(output_folder)
    os.mkdir(output_folder)
    os.mkdir(output_cover_folder)
    os.mkdir(output_list_folder)
    os.mkdir(output_book_folder)
    save_catalogue(dict())


def read_catalogue(file_name=work_catalogue_filename):
    """
    Read the catalogue from a JSON file.

    Parameters
    ----------
    file_name : str, optional
        The filename to read the catalogue from, by default work_catalogue_filename

    Returns
    -------
    dict
        The catalogue.
    """
    try:
        with open(file_name, "r") as fp:
            result = json.load(fp)
    except FileNotFoundError:
        result = dict()
    return result


def save_catalogue(catalogue, filename=work_catalogue_filename):
    """
    Save the catalogue to a JSON file.

    Parameters
    ----------
    catalogue : dict
        The catalogue to save.
    file_name : str, optional
        The filename to save the catalogue to, by default work_catalogue_filename
    """
    with open(filename, "w") as file:
        json.dump(catalogue, file, indent=2, separators=(",", ": "))


def save_cover_image(image_data, filename):
    """
    Save a cover image to the output folder.

    Parameters
    ----------
    image_data : bytes
        The image data to save.
    file_name : str
        The filename to save the image as.
    """
    with open(f"{output_cover_folder}/{filename}", "wb") as file:
        file.write(image_data)


def read_amazon_orders():
    """
    Read orders from Amazon.

    Returns
    -------
    dict
        A dictionary of orders, with product names as keys.
    """
    with open(amazon_orders_filename, "r") as fp:
        orders = json.load(fp)
    return orders


def read_markdown(filename):
    """
    Read a book from a markdown file.

    Parameters
    ----------
    filename : str
        The filename of the markdown file to read.

    Returns
    -------
    dict
        The book.
    """
    try:
        with open(filename, "r") as fp:
            content = fp.read()
    except FileNotFoundError:
        return dict()
    frontmatter, *description = content.split("---\n")[1:]
    description = "---\n".join(description)
    book = yaml.load(frontmatter, Loader=yaml.FullLoader)
    book["description"] = description
    return book


def write_markdown(
    data,
    filename,
    output_folder,
    top_attributes=None,
    override_do_not_update=False,
    include_items=True,
):
    """
    Write a book or a book list to a markdown file.

    Parameters
    ----------
    data : dict
        The book or book list to write.
    filename : str
        The filename to write the book or book list to.
    ouput_folder : str
        The folder to write the book or book list to.
    top_attributes : list, optional
        The attributes to write first in the front matter, by default None
    override_do_not_update : bool, optional
        Whether to override the do_not_update list, by default False
    include_items : bool, optional
        Whether to include the items in the list, by default True
    """
    if not top_attributes:
        top_attributes = list()
    full_filename = f"{output_folder}/{filename}"
    current_data = read_markdown(full_filename)
    do_not_update = current_data.get("do_not_update", list())
    if current_data.get("locked", False):
        return False

    if override_do_not_update:
        do_not_update = list()

    data_to_write = dict()
    for key in top_attributes:
        if key in do_not_update:
            data_to_write[key] = current_data[key]
        else:
            if data_value := data.get(key):
                data_to_write[key] = data_value

    for key, value in current_data.items():
        if key not in top_attributes:
            data_to_write[key] = value
    for key, value in data.items():
        if key not in top_attributes and key not in do_not_update:
            data_to_write[key] = value

    if not include_items:
        data_to_write.pop("items", None)

    frontmatter = {
        key: value for key, value in data_to_write.items() if key != "description"
    }
    yaml_frontmatter = yaml.dump(frontmatter, sort_keys=False)
    with open(full_filename, "w") as fp:
        fp.write("---\n")
        fp.write(yaml_frontmatter)
        fp.write("---\n")
        fp.write(data_to_write.get("description", ""))
        fp.write("\n")
    return True


def write_markdown_book(
    book, filename, book_output_folder, override_do_not_update=False
):
    """
    Export a book to markdown.

    Parameters
    ----------
    book : dict
        The book to export.
    output_folder : str
        The folder to export the book to.
    do_not_update : list, optional
        A list of keys to not update if they already exist in Markdown, by default None
    """
    top_attributes = ["book_id", "full_title", "title", "subtitle"]
    write_markdown(
        book, filename, book_output_folder, top_attributes, override_do_not_update
    )


def write_markdown_list(
    book_list,
    filename=None,
    list_output_folder=output_list_folder,
    override_do_not_update=False,
    include_items=True,
    make_sublists=False,
    include_covers=True,
    include_covers_in_sublists=True,
    remove_count_from_sublists=False,
):
    """
    Write a list of books to a markdown file.

    Parameters
    ----------
    book_list : list
        The list of books to write.
    description : str
        The description of the list.
    filename : str, optional
        A filename to write the list to instead of the one derived from the list name, by default None
    list_output_folder : str, optional
        The folder to write the list to, by default output_list_folder
    override_do_not_update : bool, optional
        Whether to override the do_not_update list, by default False
    include_index : bool, optional
        Whether to include an index of the list, by default False
    include_items : bool, optional
        Whether to include the items in the list, by default True
    make_sublists : bool, optional
        Whether to make sublists for the items in the list, by default False
    include_covers : bool, optional
        Whether to include covers in the list, by default True
    include_covers_in_sublists : bool, optional
        Whether to include covers in the sublists, by default True
    remove_count_from_sublists : bool, optional
        Whether to remove the count from the sublist titles, by default False
    """
    top_attributes = [
        "name",
        "title",
        "subtitle",
        "description",
    ]
    if not filename:
        filename = f"{book_list['name'].lower().replace(' ', '_')}.md"

    saved_books = dict()
    if not include_covers:
        print("removing books")
        for item in book_list["items"]:
            saved_books[item["name"]] = item["books"]
            item["books"] = list()

    write_markdown(
        book_list,
        filename,
        list_output_folder,
        top_attributes,
        override_do_not_update,
        include_items,
    )
    if make_sublists:
        if not include_covers and include_covers_in_sublists:
            for item in book_list["items"]:
                item["books"] = saved_books[item["name"]]
        for sublist_data in book_list["items"]:
            print(f"    - {sublist_data['name']}")
            if sublist_data["books"] and len(sublist_data["books"]) > 0:
                sublist_data["items"] = [
                    {
                        "name": sublist_data["name"],
                        "title": None,
                        "books": sublist_data["books"],
                        "description": sublist_data["description"],
                    }
                ]
                sublist_data["title"] = sublist_data["title"][0]
                if remove_count_from_sublists:
                    sublist_data["title"] = sublist_data["title"].split("(")[0].strip()
                sublist_data["description"] = sublist_data["sublist_description"]
                write_markdown_list(
                    sublist_data,
                    list_output_folder=list_output_folder,
                    include_items=True,
                )


def include_book(book):
    return (
        not book.get("deleted")
        and book.get("authors")
        and book.get("title")
        and book.get("cover_filename")
        and book.get("type") != "audiobook_sample"
        and book.get("theme") != "kids"
    )


def flat_catalogue(catalogue):
    """
    Flatten the catalogue into a list of books.

    Parameters
    ----------
    catalogue : dict
        The catalogue.

    Returns
    -------
    list
        A list of books.
    """
    books = list()
    for book_id, book_types in catalogue.items():
        for book_type, book in book_types.items():
            if include_book(book):
                books.append((book_id, book_type, book))
    return books


def save_attributes(args=None, attributes_storage_file="./raw/attributes.json"):
    """Save current attribute states so it can be used to enrich the data later on."""

    attributes_to_save = (
        "order",
        "theme",
        "purchase_date",
        "location",
        "listening_date",
        "read_status",
        "locked",
        "do_not_update",
        "deleted",
    )

    if args is not None:
        attributes_to_save = args

    catalogue = read_catalogue()
    current_attributes = read_attributes(attributes_storage_file)
    results = defaultdict(dict)
    for book_id, book_types in catalogue.items():
        for book_type, book in book_types.items():
            record = current_attributes.get(book_id, dict()).get(book_type, dict())
            # record = dict()
            for attribute in attributes_to_save:
                if value := book.get(attribute):
                    record[attribute] = value
            if record:
                results[book_id][book_type] = record

    with open(attributes_storage_file, "w") as f:
        json.dump(results, f, indent=2, separators=(",", ": "), sort_keys=True)


def read_attributes(attributes_storage_file="./raw/attributes.json"):
    """
    Load attribute information from the storage file.

    This is used to enrich the data with the information that was previously saved.
    """
    catalogue = read_catalogue()
    try:
        with open(attributes_storage_file, "r") as f:
            attributes = json.load(f)
    except FileNotFoundError:
        attributes = dict()
    for book_id, book_types in catalogue.items():
        for book_type, book in book_types.items():
            if book_id in attributes and book_type in attributes[book_id]:
                for key, value in attributes[book_id][book_type].items():
                    book[key] = value
    return attributes
