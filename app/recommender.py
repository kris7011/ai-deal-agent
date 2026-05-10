from app.models import Product
from app.requirements import ProductRequirements
from app.scorer import calculate_score


def recommend_best_product(
    products: list[Product],
    requirements: ProductRequirements
) -> Product | None:
    if not products:
        return None

    return max(products, key=lambda product: calculate_score(product, requirements))