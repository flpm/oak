from collections import defaultdict
from rich import print
from rich.prompt import Prompt


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
            candidates[confidence].append(order)

    return candidates


def choose_order(order_list, current_order):
    if current_order is None:
        current_order = dict()
    order_list = sorted(order_list, key=lambda x: x["order_date"])
    print(f"Found {len(order_list)} orders:")
    for index, order in enumerate(order_list):
        print(
            f"[bold white]{index + 1}[/bold white] - "
            f"{order['order_id']} - "
            f"[bold green]{'(current order) - ' if order['order_id'] == current_order.get('order_id') else ''}[/bold green]"
            f"[blue]{order['order_date']}[/blue] - "
            f"[bold yellow]{order['product_name']}[/bold yellow]"
        )
    print("---")
    choice = Prompt.ask(
        "Choose one of the orders above",
        choices=[str(i) for i in range(1, len(order_list) + 1)] + ["n"],
    )
    if choice == "n":
        return None
    return order_list[int(choice) - 1]


def search_orders(order_keyword, orders):
    order_keyword = order_keyword.lower()
    candidates = [
        order
        for order_list in orders.values()
        for order in order_list
        if order_keyword in order["product_name"].lower()
    ]
    return candidates
