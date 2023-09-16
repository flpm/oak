"""
Query the Audible URL for each book and collect additional information.
"""
import json
import os
import re
import requests

from bs4 import BeautifulSoup
from collections import Counter

from .file import save_cover_image
from .lang import land_code_to_name


def make_search_lambda(tag_type, attr_name, attr_value):
    """
    Generate a lambda function  that can be used to search using Beautiful Soup.

    Parameters
    ----------
    tag_type: str
        The name of the tag we are searching for.
    attr_name: str
        The name of the attribute we will be filtering on.
    attr_value: list[str]
        List of values we expect to find in the attribute.

    Returns
    lambda
        A lambda function that can be used to search using Beautiful Soup.
    """
    return (
        lambda tag: tag.name == tag_type
        and tag.get(attr_name)
        and set(attr_value).intersection(set(tag.get(attr_name)))
    )


def get_book_detail_html(book, errors=None):
    """
    Download the HTML for the details page of an audiobook.

    Parameters
    ----------
    book : dict
        Information about the audiobook, extracted from the Audible Listening History.

    Returns
    -------
    BeautifulSoup
        An instance of BeautifulSoup after parsing the HTML code for the book detail page.
    """
    asin = book.get("asin")
    link = book.get("link")
    if errors is None:
        errors = Counter()
    if not link:
        errors["Missing link"] += 1
        return None, errors

    audiobook_detail_filename = f"book_{asin}.html"
    full_audiobook_detail_filename = (
        f"./raw/audible/library/{audiobook_detail_filename}"
    )

    try:
        with open(full_audiobook_detail_filename, "rt") as fp_html:
            html_data = fp_html.read()
            soup = BeautifulSoup(html_data, "html.parser")
    except FileNotFoundError:
        errors["Local HTML file not found"] += 1
        html_data = None

    if html_data is None:
        status_code = book.get("status_code")
        if status_code == 404:
            errors["Link request returned 404"] += 1
            return None, errors
        response = requests.get(book["link"])
        status_code = response.status_code
        # book["status_code"] = status_code

        if status_code == 200:
            html_data = response.content
            soup = BeautifulSoup(html_data, "html.parser")
            with open(full_audiobook_detail_filename, "w") as fp_book_detail:
                fp_book_detail.write(soup.prettify())
        else:
            errors["Skipping book, no local or network data"] += 1
            return None, errors

    return soup, errors


def get_topics(soup):
    """
    Get the topics for this audiobook.

    Parameters
    ----------
    soup : BeautifulSoup
        Instance of BeautifulSoup that parsed the HTML data for the details page.

    Returns
    -------
    list[str]
        The list of topic strings.
    """
    topic_tags_section = soup.find(
        make_search_lambda("div", "class", ["product-topic-tags"])
    )
    topic_tags = topic_tags_section.find_all(
        make_search_lambda("span", "class", ["bc-chip-text"])
    )
    return [item.string.strip() for item in topic_tags]


def get_content_format(soup):
    """
    Get the format of the content of this audiobook (e.g. lectures, unabridged).

    Parameters
    ----------
    soup : BeautifulSoup
        Instance of BeautifulSoup that parsed the HTML data for the details page.

    Returns
    -------
    str
        The format of the content.
    """
    format_li_tag = soup.find(make_search_lambda("li", "class", ["format"]))
    format_string = None
    if format_li_tag:
        format_string = re.sub(
            " +",
            " ",
            format_li_tag.string.replace("\n", "").replace("Unabridged", "").strip(),
        )
        if format_string in ("Non-Traditional"):
            format_string = f"{format_string} Audiobook"
    return format_string


def get_cover_image(book, soup, errors):
    """
    Get the audiobook cover information.

    Parameters
    ----------
    book : dict
        Information about the audiobook, extracted from the Audible Listening History.
    soup : BeautifulSoup
        Instance of BeautifulSoup that parsed the HTML data for the details page.

    Returns
    -------
    str
        URL for the audibook cover image.
    """
    cover_link = cover_filename = None
    search_lambda = (
        lambda tag: tag.name == "img"
        and tag.get("alt")
        and book.get("title")
        and book["title"] in tag.get("alt")
    )
    try:
        cover_img = soup.find_all(search_lambda)[0]
        cover_link = cover_img.get("src")
        cover_filename = f"{book['asin']}.{cover_link.split('/')[-1].split('.')[-1]}"

        if not os.path.isfile(cover_filename):
            response = requests.get(cover_link)
            if response.status_code == 200:
                image_data = response.content
                save_cover_image(image_data, cover_filename)
        else:
            errors["Books cover already exists"] += 1
    except IndexError:
        errors["Error finding cover in HTML"] += 1
        return None, errors
    return cover_filename, errors


def find_book_details(soup):
    """
    Get the audiobook detail information.

    Parameters
    ----------
    soup : BeautifulSoup
        Instance of BeautifulSoup that parsed the HTML data for the details page.

    Returns
    -------
    dict
        A dictionary with the details (e.g. author, narrator, publisher, etc.)
    """
    search_lambda = (
        lambda tag: tag.name == "div"
        and tag.get("id")
        and ("bottom-0" in tag.get("id"))
    )
    divs = soup.find_all(search_lambda)
    try:
        book_data, _ = json.loads(divs[0].script.string)
    except ValueError:
        raise RuntimeError("Cannot find book details.")

    book_details = dict()
    for key in (
        # "bookFormat",
        # "name",
        "description",
        # "abridged",
        "author",
        "readBy",
        "publisher",
        "datePublished",
        "inLanguage",
        # "duration",
        "aggregateRating",
    ):
        value = book_data.get(key)
        if key in ("author", "readBy"):
            if value:
                value = [i["name"] for i in value]
            if key == "readBy":
                key = "narrators"
            if key == "author":
                key = "authors"
        elif key == "datePublished":
            key = "date_published"
        elif key == "inLanguage":
            key = "language"
            if len(value) < 4:
                value = [land_code_to_name(value)]
            else:
                value = [value.capitalize()]
            # if value == "english":
            #     value = "en"
            # elif value == "spanish":
            #     value = "es"
        elif key == "aggregateRating":
            key = "rating"
            if value:
                value = {
                    "rating": float(value["ratingValue"]),
                    "count": int(value["ratingCount"]),
                }
            else:
                value = {}
        elif key == "description":
            value = re.sub(r" *\<p\>", "", value)
            value = re.sub(r" *\<\/p\>", "\n", value)
            value = re.sub(r"\<\/?[^\>]*\>", "", value)
            value = [i.strip() for i in value.split("\n") if i.strip()]
        book_details[key] = value
    return book_details
