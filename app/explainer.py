from app.models import Product
from app.requirements import SearchRequirements
from app.feature_matcher import product_matches_feature


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
        if product_matches_feature(product, feature):
            explanations.append(f"✓ Matcher krav: {feature}")
        else:
            explanations.append(f"? Ikke tydeligt om produktet matcher: {feature}")

    return explanations
