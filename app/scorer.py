from app.models import Product
from app.requirements import SearchRequirements
from app.feature_matcher import product_matches_feature


def calculate_score(product: Product, requirements: SearchRequirements) -> int:
    score = 0

    score += _calculate_price_score(product, requirements)
    score += _calculate_rating_score(product)
    score += _calculate_feature_score(product, requirements)

    return min(score, 100)


def _calculate_price_score(product: Product, requirements: SearchRequirements) -> int:
    if requirements.max_price is None:
        return 10

    if product.price <= 0:
        return 0

    if product.price <= requirements.max_price:
        return 30

    return 0


def _calculate_rating_score(product: Product) -> int:
    if product.rating is None:
        return 0

    if product.rating >= 4.5:
        return 15

    if product.rating >= 4.0:
        return 10

    return 0


def _calculate_feature_score(
    product: Product,
    requirements: SearchRequirements,
) -> int:
    if not requirements.required_features:
        return 40

    matched_features = 0

    for feature in requirements.required_features:
        if product_matches_feature(product, feature):
            matched_features += 1

    return int((matched_features / len(requirements.required_features)) * 55)
