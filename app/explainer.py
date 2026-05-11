from app.models import Product
from app.requirements import ProductRequirements


def generate_explanation(
    product: Product,
    requirements: ProductRequirements,
) -> list[str]:

    explanations = []

    if product.price <= requirements.max_price:
        explanations.append(
            f"✓ Under budget ({product.price} kr.)"
        )
    else:
        explanations.append(
            f"✗ Over budget ({product.price} kr.)"
        )

    if product.has_mop:
        explanations.append(
            "✓ Har moppefunktion"
        )

    if product.has_obstacle_avoidance:
        explanations.append(
            "✓ Har undgåelse af forhindringer"
        )
    else:
        explanations.append(
            "✗ Ingen tydelig undgåelse af forhindringer fundet"
        )

    if product.suction_pa:
        explanations.append(
            f"✓ Sugeevne fundet ({product.suction_pa} Pa)"
        )

    if product.can_handle_rugs:
        explanations.append(
            "✓ Ser ud til at kunne klare tæpper/måtter"
        )

    return explanations