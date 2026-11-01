"""Side-by-side comparison of stored products."""

MIN_PRODUCTS = 2
MAX_PRODUCTS = 4


def build_comparison(histories: list[dict]) -> dict:
    """Combines the price histories of 2-4 products and marks what stands out.

    Highlights are only given when they mean something: the cheapest current price among products
    that have a price, the best rating among rated products, and the product whose current price is
    its own lowest so far. Ties mark every product that shares the best value.
    """
    items = [
        {
            "product": history["product"],
            "summary": history["summary"],
            "highlights": [],
        }
        for history in histories
    ]

    priced = [item for item in items if item["summary"]["latest_price"] is not None]

    if len(priced) > 1:
        cheapest = min(item["summary"]["latest_price"] for item in priced)

        for item in priced:
            if item["summary"]["latest_price"] == cheapest:
                item["highlights"].append("cheapest_now")

    rated = [item for item in items if item["product"]["rating"] is not None]

    if len(rated) > 1:
        best_rating = max(item["product"]["rating"] for item in rated)

        for item in rated:
            if item["product"]["rating"] == best_rating:
                item["highlights"].append("best_rated")

    for item in items:
        if item["summary"]["is_lowest_seen"]:
            item["highlights"].append("lowest_price_seen")

    latest_prices = [item["summary"]["latest_price"] for item in priced]

    return {
        "count": len(items),
        "price_spread": max(latest_prices) - min(latest_prices) if len(latest_prices) > 1 else None,
        "items": items,
    }
