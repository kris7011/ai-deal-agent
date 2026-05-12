import re

from app.requirements import SearchRequirements


def parse_requirements(user_query: str) -> SearchRequirements:
    query = user_query.strip()
    lower_query = query.lower()

    return SearchRequirements(
        product_type=_parse_product_type(lower_query),
        max_price=_parse_max_price(lower_query),
        required_features=_parse_required_features(lower_query),
        raw_query=query,
    )


def _parse_product_type(query: str) -> str:
    separators = [" med ", " under ", " maks ", " max ", " op til "]

    product_type = query

    for separator in separators:
        if separator in product_type:
            product_type = product_type.split(separator)[0]

    return product_type.strip()


def _parse_max_price(query: str) -> int | None:
    match = re.search(r"(?:max|maks|under|op til)\s*(\d{3,6})", query)

    if not match:
        return None

    return int(match.group(1))


def _parse_required_features(query: str) -> list[str]:
    if " med " not in query:
        return []

    feature_text = query.split(" med ", 1)[1]

    price_words = [" max ", " maks ", " under ", " op til "]

    for price_word in price_words:
        if price_word in feature_text:
            feature_text = feature_text.split(price_word, 1)[0]

    parts = re.split(r",| og ", feature_text)

    return [part.strip() for part in parts if part.strip()]
