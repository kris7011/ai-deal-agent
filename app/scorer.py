from app.models import Product
from app.requirements import ProductRequirements


def calculate_score(product: Product, requirements: ProductRequirements) -> int:
    score = 0

    if product.price <= requirements.max_price:
        score += 25

    if product.has_mop == requirements.must_have_mop:
        score += 15

    if product.has_obstacle_avoidance == requirements.must_have_obstacle_avoidance:
        score += 20

    if product.suction_pa is not None and product.suction_pa >= requirements.min_suction_pa:
        score += 20

    if product.can_handle_rugs == requirements.must_handle_rugs:
        score += 10

    if product.rating is not None and product.rating >= 4.0:
        score += 10

    return score