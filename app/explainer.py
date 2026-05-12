from app.models import Product
from app.requirements import SearchRequirements


def generate_explanation(
    product: Product,
    requirements: SearchRequirements,
) -> list[str]:
    explanations = []

    if requirements.max_price is not None:
        if product.price <= requirements.max_price:
            explanations.append(f"✓ Under budget ({product.price} kr.)")
        else:
            explanations.append(f"✗ Over budget ({product.price} kr.)")

    if product.rating is not None:
        explanations.append(f"✓ Rating fundet ({product.rating})")

    for feature in requirements.required_features:
        if _product_matches_feature(product, feature):
            explanations.append(f"✓ Matcher krav: {feature}")
        else:
            explanations.append(f"? Ikke tydeligt om produktet matcher: {feature}")

    return explanations


def _product_matches_feature(product: Product, feature: str) -> bool:
    searchable_text = f"{product.name} {product.source}".lower()
    feature = feature.lower()

    if feature in searchable_text:
        return True

    feature_words = [word for word in feature.split() if len(word) > 2]

    return any(word in searchable_text for word in feature_words)
