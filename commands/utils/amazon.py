import csv
import json

from collections import Counter, defaultdict
from rich import print

from .editing import confirm_loop
from .books import print_book

filename_list = [
    "./raw/amazon/Retail.OrderHistory.1.csv",
    "./raw/amazon/Retail.OrderHistory.2.csv",
]


def get_city(address):
    """
    Get the city from the shipping address.

    Parameters
    ----------
    address : str
        The shipping address.

    Returns
    -------
    str
        The city.
    """
    for city in ("Paris", "New York", "Barcelona"):
        if city.lower() in address.lower():
            return city
    return None


def prepare_amazon_purchase_data():
    """
    Prepare the Amazon purchase data.

    Returns
    -------
    dict
        The orders by product.
    """
    order_by_product = defaultdict(list)

    results = dict()
    for i, filename in enumerate(filename_list):
        with open(filename, "rt") as fp:
            reader = csv.DictReader(fp)

            for order in reader:
                order_id = order["Order ID"]
                product_name = order["Product Name"]

                order_info = results.get((order_id, product_name), dict())
                for key in (
                    "Order ID",
                    "Product Name",
                    "Quantity",
                    "Order Date",
                    "Ship Date",
                    "Shipping Address",
                    "Currency",
                    "Unit Price",
                    "Product Condition",
                ):
                    new_key = key.replace(" ", "_").lower()
                    order_info[new_key] = order[key]
                order_info["location"] = get_city(order_info["shipping_address"])
                del order_info["shipping_address"]
                results[(order_id, product_name)] = order_info

    for entry in results.values():
        name = entry["product_name"]
        order_by_product[name].append(entry)

    with open("./raw/amazon/amazon_orders.json", "wt") as fp_w:
        json.dump(order_by_product, fp_w)

    return order_by_product


def print_candidates(candidates, current=None, preserve_previous_matches=True):
    """
    Print the candidate orders for a book and ask the user to choose one.

    Parameters
    ----------
    candidates : list
        The list of candidate orders.
    current : str
        The current order ID.
    preserve_previous_matches : bool, optional
        Whether to preserve existing order matches, by default True

    Returns
    -------
    dict
        The chosen order.
    """
    counter = 0
    current_order = dict()
    for c in candidates:
        is_current = False
        if c["order_id"] == current:
            is_current = True
            current_order = c
        print(
            f"{counter}) [green]{c['order_date']}[/green] {c['product_name']} {c['order_id']} [bold yellow]{'current' if is_current else ''}[/bold yellow]"
        )
        counter += 1

    if preserve_previous_matches and current_order:
        return current_order

    res = confirm_loop(
        [str(i) for i in range(len(candidates))] + ["n"],
        "Choose which order to use?",
        default=0,
    )
    if res == "n":
        return None
    return candidates[int(res)]


def select_candidates(orders, book):
    """
    Select the candidate orders for a book.

    Parameters
    ----------
    orders : dict
        The orders by product.
    book : dict
        The book information.

    Returns
    -------
    dict
        The candidate orders.
    """
    candidates = defaultdict(list)
    for name, order_info in orders.items():
        if (
            "shirt" in name.lower()
            or "screen reincarnated" in name.lower()
            or "figurine" in name.lower()
            or "miniatures bundle" in name.lower()
            or "mad libs" in name.lower()
            or "dungeon academy" in name.lower()
            or "starter set" in name.lower()
            or "a search and find adventure" in name.lower()
            or "keeper's screen" in name.lower()
            or "board game" in name.lower()
        ):
            continue

        if name.lower().startswith(book["title"].split(":")[0].lower()[:30]):
            confidence = "strong"
        elif name.lower()[:15] == book["title"].lower()[:15]:
            confidence = "weak"
        else:
            continue

        if not order_info:
            raise RuntimeError("Empty order info in Amazon purrchase history.")

        for order in order_info:
            order_id = order["order_id"]
            candidates[confidence].append(order)

    return candidates


def enrich_amazon_books(catalogue):
    """
    Enrich Amazon books using data from the Amazon purchase history.

    Parameters
    ----------
    catalogue : dict
        The current catalogue.

    Returns
    -------
    dict
        The modified catalogue.
    """
    orders = prepare_amazon_purchase_data()

    book_count = 0
    assigned_order_count = 0
    total = sum([1 for book_types in catalogue.values() if book_types.get("book")])
    for book_types in catalogue.values():
        for book_type, book in book_types.items():
            if book_type != "book":
                continue

            current_order = book.get("order")
            if current_order is None:
                current_order = dict()
            else:
                if "shipping_address" in current_order:
                    del current_order["shipping_address"]

            print_book((book_count, total), book["book_id"], book_type, book)

            candidates = select_candidates(orders, book)

            if strong := candidates.get("strong"):
                if len(strong) == 1:
                    book["order"] = strong[0]
                    print("[green]found a single match[/green]")
                else:
                    strong = sorted(strong, key=lambda x: x["order_date"])
                    book["order"] = print_candidates(
                        strong, current_order.get("order_id")
                    )
            else:
                if weak := candidates.get("weak"):
                    weak = sorted(weak, key=lambda x: x["order_date"])
                    book["order"] = print_candidates(
                        weak, current_order.get("order_id")
                    )
                else:
                    print("[red]no match found[/red]")
                    book["order"] = None

            if book["order"]:
                book["purchase_date"] = book["order"]["ship_date"].split("T")[0]
                book["location"] = book["order"]["location"]
                assigned_order_count += 1
            book_count += 1

    return catalogue, assigned_order_count
