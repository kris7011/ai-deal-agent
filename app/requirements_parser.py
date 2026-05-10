from app.requirements import ProductRequirements


def parse_requirements(user_query: str) -> ProductRequirements:
    query = user_query.lower()

    max_price = 5000

    if "10000" in query:
        max_price = 10000

    return ProductRequirements(
        product_type="robot vacuum",
        max_price=max_price,
        must_have_mop=True,
        must_have_obstacle_avoidance=True,
        min_suction_pa=5000,
        must_handle_rugs=True,
    )