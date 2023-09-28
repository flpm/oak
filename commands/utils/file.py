"""
Convert the export files from the Bookshelf IOS app into a JSON file for archiving.
"""
import json
import yaml

work_catalogue_filename = "./work/catalogue.json"
output_cover_folder = "./output/covers"
output_list_folder = "./output/lists"
amazon_orders_filename = "./raw/amazon/amazon_orders.json"


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
        json.dump(catalogue, file)


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
    frontmatter, description = content.split("---\n")[1:]
    book = yaml.load(frontmatter, Loader=yaml.FullLoader)
    book["description"] = description
    return book


def write_markdown(
    data, filename, output_folder, top_attributes=None, override_do_not_update=False
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
            data_to_write[key] = data[key]
    for key, value in current_data.items():
        if key not in top_attributes:
            data_to_write[key] = value
    for key, value in data.items():
        if key not in top_attributes and key not in do_not_update:
            data_to_write[key] = value

    frontmatter = {
        key: value for key, value in data_to_write.items() if key != "description"
    }
    yaml_frontmatter = yaml.dump(frontmatter, sort_keys=False)
    with open(full_filename, "w") as fp:
        fp.write("---\n")
        fp.write(yaml_frontmatter)
        fp.write("---\n")
        fp.write(data_to_write.get("description", "No description available"))
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
    """
    top_attributes = ["name", "title", "description", "items"]
    if not filename:
        filename = f"{book_list['name'].lower().replace(' ', '_')}.md"
    write_markdown(
        book_list, filename, list_output_folder, top_attributes, override_do_not_update
    )
