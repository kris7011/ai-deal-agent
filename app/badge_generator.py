from app.models import Product
from app.requirements import SearchRequirements
from app.feature_matcher import product_matches_feature


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
        if product_matches_feature(product, feature):
            badges.append(f"Matcher: {feature}")

    return badges
