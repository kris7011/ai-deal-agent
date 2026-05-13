from app.models import Product


def product_matches_feature(product: Product, feature: str) -> bool:
    searchable_text = f"{product.name} {product.source}".lower()
    feature = feature.lower()

    if feature in searchable_text:
        return True

    feature_words = [word for word in feature.split() if len(word) > 2]

    return any(word in searchable_text for word in feature_words)
