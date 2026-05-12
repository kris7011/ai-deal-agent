from app.models import Product
from app.requirements import SearchRequirements
from app.scorer import calculate_score


def test_product_under_budget_scores_higher_than_over_budget_product():
    # Arrange
    requirements = SearchRequirements(
        product_type="laptop",
        max_price=8000,
        required_features=[],
        raw_query="laptop under 8000 kr",
    )

    cheap_product = Product(
        name="Lenovo laptop",
        price=6000,
        url="",
        image_url=None,
        suction_pa=None,
        has_mop=None,
        has_obstacle_avoidance=None,
        can_handle_rugs=None,
        rating=None,
        source="Test",
    )

    expensive_product = Product(
        name="Expensive laptop",
        price=12000,
        url="",
        image_url=None,
        suction_pa=None,
        has_mop=None,
        has_obstacle_avoidance=None,
        can_handle_rugs=None,
        rating=None,
        source="Test",
    )

    # Act
    cheap_score = calculate_score(cheap_product, requirements)
    expensive_score = calculate_score(expensive_product, requirements)

    # Assert
    assert cheap_score > expensive_score
