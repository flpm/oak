"""
Convert the export files from the Bookshelf IOS app into a JSON file for archiving.
"""
import json
import yaml

work_catalogue_filename = "./work/catalogue.json"
output_cover_folder = "./output/covers"
amazon_orders_filename = "./raw/amazon/amazon_orders.json"


def read_catalogue(file_name=work_catalogue_filename):
    try:
        with open(file_name, "r") as fp:
            result = json.load(fp)
    except FileNotFoundError:
        result = dict()
    return result


def save_catalogue(catalogue, file_name=work_catalogue_filename):
    with open(file_name, "w") as file:
        json.dump(catalogue, file)


def save_cover_image(image_data, file_name):
    with open(f"{output_cover_folder}/{file_name}", "wb") as file:
        file.write(image_data)


def read_amazon_orders():
    with open(amazon_orders_filename, "r") as fp:
        orders = json.load(fp)
    return orders


def export_book_to_markdown(
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
    current_book = read_markdown_book(f"{book_output_folder}/{filename}")
    do_not_update = current_book.get("do_not_update", list())
    if current_book.get("locked", False):
        return False

    top_attributes = ["book_id", "full_title", "title", "subtitle"]
    if override_do_not_update:
        do_not_update = list()

    book_to_write = dict()
    for key in top_attributes:
        if key in do_not_update:
            book_to_write[key] = current_book[key]
        else:
            book_to_write[key] = book[key]
    for key, value in current_book.items():
        if key not in top_attributes:
            book_to_write[key] = value
    for key, value in book.items():
        if key not in top_attributes and key not in do_not_update:
            book_to_write[key] = value

    frontmatter = {
        key: value for key, value in book_to_write.items() if key != "description"
    }
    yaml_frontmatter = yaml.dump(frontmatter, sort_keys=False)
    with open(f"{book_output_folder}/{filename}", "w") as fp:
        fp.write("---\n")
        fp.write(yaml_frontmatter)
        fp.write("---\n")
        fp.write(book_to_write.get("description", "No description available"))
        fp.write("\n")
    return True


def read_markdown_book(filename):
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
    with open(filename, "r") as fp:
        content = fp.read()
    frontmatter, description = content.split("---\n")[1:]
    book = yaml.load(frontmatter, Loader=yaml.FullLoader)
    book["description"] = description
    return book
