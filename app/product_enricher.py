from app.models import Product


def enrich_product(product: Product) -> Product:
    name = product.name.lower()

    has_mop = product.has_mop
    has_obstacle_avoidance = product.has_obstacle_avoidance
    can_handle_rugs = product.can_handle_rugs
    suction_pa = product.suction_pa

    if has_mop is None:
        has_mop = _contains_any(name, ["mop", "moppe", "mopping", "vask"])

    if has_obstacle_avoidance is None:
        has_obstacle_avoidance = _contains_any(
            name,
            [
                "obstacle",
                "avoidance",
                "forhindring",
                "forhindringer",
                "ai",
                "camera",
                "kamera",
                "3d",
            ],
        )

    if can_handle_rugs is None:
        can_handle_rugs = _contains_any(
            name,
            ["carpet", "rug", "tæppe", "måtte", "måtter"]
        )

    if suction_pa is None:
        suction_pa = _extract_suction_pa(name)

    return Product(
        name=product.name,
        price=product.price,
        url=product.url,
        suction_pa=suction_pa,
        has_mop=has_mop,
        has_obstacle_avoidance=has_obstacle_avoidance,
        can_handle_rugs=can_handle_rugs,
        rating=product.rating,
        source=product.source,
    )


def enrich_products(products: list[Product]) -> list[Product]:
    return [enrich_product(product) for product in products]


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _extract_suction_pa(text: str) -> int | None:
    words = text.replace(",", ".").split()

    for index, word in enumerate(words):
        if "pa" in word:
            number = word.replace("pa", "").replace(".", "")

            if number.isdigit():
                return int(number)

        if word.isdigit() and index + 1 < len(words):
            next_word = words[index + 1]

            if "pa" in next_word:
                return int(word)

    return None