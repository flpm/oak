from collections import defaultdict
from bs4 import BeautifulSoup


def convert_downloaded_html(
    number_of_pages=3, location="./raw/audible/library/audible_saved/"
):
    """
    Convert the downloaded HTML files from Audible to a readable HTML file.

    Parameters
    ----------
    number_of_pages : int
        Number of pages to convert.
    location : str
        Location of the downloaded HTML files.

    Returns
    -------
    list
        List of filenames of the converted HTML files.

    """
    html_filenames = [
        f"{location}/My Library Audible.com-{i + 1}.html"
        for i in range(number_of_pages)
    ]
    result = list()
    for i, filename in enumerate(html_filenames):
        with open(filename, "r") as fp:
            html_doc = fp.read()
        soup = BeautifulSoup(html_doc, "html.parser")
        pretty_name = f"./raw/audible/library/my_library_{i + 1}.html"
        with open(pretty_name, "w") as fp_w:
            fp_w.write(soup.prettify())
            result.append((pretty_name, filename))

    return result


def import_from_audible_library():
    """
    Import books from the saved HTML Audible library.

    Returns
    -------
    dict
        Dictionary of books in the same format as the catalogue.
    """
    print("Importing books from Audible library.")
    audiobooks = defaultdict(dict)
    for i, (filename, html_filename) in enumerate(convert_downloaded_html()):
        print(f"- working on part {i + 1}")
        with open(filename, "r") as fp:
            html_doc = fp.read()
        soup = BeautifulSoup(html_doc, "html.parser")

        is_cover = (
            lambda tag: tag.name == "img"
            and tag.get("class")
            and ("bc-pub-block" in tag.get("class"))
        )
        is_book_row = lambda tag: tag.get("class") and (
            "adbl-library-content-row" in tag.get("class")
        )

        rows = soup.find_all(is_book_row)
        print(f"    - found {len(rows)} entries")
        for row in rows:
            info = dict()

            for key, class_value in (
                ("full_title", "bc-size-headline3"),
                ("author", "authorLabel"),
                ("narrator", "narratorLabel"),
            ):
                search_lambda = (
                    lambda tag: tag.name == "span"
                    and tag.get("class")
                    and (class_value in tag.get("class"))
                )

                if key == "full_title":
                    title_span = row.find_all(search_lambda)[0]
                    raw_value = title_span.string.strip()
                    if not raw_value:
                        print("    - no title found, skipping")
                        break
                    if raw_value == "Your First Listen":
                        break

                    if title_href := title_span.parent.get("href"):
                        link = title_href.split("?")[0]
                    else:
                        print(f"    - no link found for {raw_value}, skipping")
                        break
                    asin = link.split("/")[-1]
                    info["book_id"] = asin
                    info["asin"] = asin

                    info["link"] = link
                    if ":" in raw_value:
                        (title, *subtitle) = raw_value.split(":")
                        info["title"] = title
                        info["subtitle"] = ":".join(subtitle).strip()
                    else:
                        info["title"] = raw_value
                else:
                    raw_value = row.find_all(search_lambda)
                    if not raw_value:
                        raise RuntimeError("{key} lambda returned zero results")
                    if raw_value:
                        raw_value = raw_value[0].a.string.strip()
                    else:
                        print(info)
                        raise RuntimeError(f"Missing {key}")
                info[key] = raw_value

            if not info:
                continue

            cover_img = row.find_all(is_cover)[0]
            info["cover_url"] = cover_img.get("src")
            cover_filename = info["cover_url"].split("/")[-1]

            folder = html_filename.split(".html")[0] + "_files"
            img_filename = f"{info['book_id']}.jpg"
            info["cover_filename"] = img_filename
            with open(f"{folder}/{cover_filename}", "rb") as f_img_source:
                with open(
                    f"./output/test_covers/{img_filename}", "wb"
                ) as f_img_destination:
                    f_img_destination.write(f_img_source.read())

            info["source"] = "Audible"
            info["type"] = "audiobook"
            info["format"] = "audiobook"
            audiobooks[asin]["audiobook"] = info

    print(f"Found {len(audiobooks)} books in Audible library.")
    return audiobooks
