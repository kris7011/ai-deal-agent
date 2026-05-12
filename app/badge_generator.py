from app.models import Product
from app.requirements import SearchRequirements


def generate_badges(
    product: Product,
    requirements: SearchRequirements,
    score: int,
) -> list[str]:
    badges = []

    if score >= 70:
        badges.append("Stærkt match")
    elif score >= 40:
        badges.append("Muligt match")

    if requirements.max_price is not None and product.price <= requirements.max_price:
        badges.append("Under budget")

    if product.rating is not None and product.rating >= 4.5:
        badges.append("Høj rating")

    for feature in requirements.required_features:
        if _product_matches_feature(product, feature):
            badges.append(f"Matcher: {feature}")

    return badges


def _product_matches_feature(product: Product, feature: str) -> bool:
    searchable_text = f"{product.name} {product.source}".lower()
    feature = feature.lower()

    if feature in searchable_text:
        return True

    feature_words = [word for word in feature.split() if len(word) > 2]

    return any(word in searchable_text for word in feature_words)
