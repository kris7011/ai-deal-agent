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


def test_product_with_high_rating_scores_higher_than_product_without_rating():
    # Arrange
    requirements = SearchRequirements(
        product_type="laptop",
        max_price=None,
        required_features=[],
        raw_query="laptop",
    )

    product_without_rating = Product(
        name="Basic laptop",
        price=5000,
        url="",
        image_url=None,
        suction_pa=None,
        has_mop=None,
        has_obstacle_avoidance=None,
        can_handle_rugs=None,
        rating=None,
        source="Test",
    )

    product_with_rating = Product(
        name="Highly rated laptop",
        price=5000,
        url="",
        image_url=None,
        suction_pa=None,
        has_mop=None,
        has_obstacle_avoidance=None,
        can_handle_rugs=None,
        rating=4.7,
        source="Test",
    )

    # Act
    score_without_rating = calculate_score(product_without_rating, requirements)
    score_with_rating = calculate_score(product_with_rating, requirements)

    # Assert
    assert score_with_rating > score_without_rating


def test_product_matching_required_feature_scores_higher():
    # Arrange
    requirements = SearchRequirements(
        product_type="powerbank",
        max_price=None,
        required_features=["usb-c"],
        raw_query="powerbank med usb-c",
    )

    product_without_feature = Product(
        name="Basic powerbank",
        price=300,
        url="",
        image_url=None,
        suction_pa=None,
        has_mop=None,
        has_obstacle_avoidance=None,
        can_handle_rugs=None,
        rating=None,
        source="Test",
    )

    product_with_feature = Product(
        name="Powerbank with USB-C",
        price=300,
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
    score_without_feature = calculate_score(product_without_feature, requirements)
    score_with_feature = calculate_score(product_with_feature, requirements)

    # Assert
    assert score_with_feature > score_without_feature


def test_score_never_exceeds_100():
    # Arrange
    requirements = SearchRequirements(
        product_type="laptop",
        max_price=8000,
        required_features=["16gb ram", "ssd", "god batteritid"],
        raw_query="laptop med 16gb ram, ssd og god batteritid under 8000 kr",
    )

    product = Product(
        name="Laptop with 16GB RAM SSD and good battery life",
        price=6000,
        url="",
        image_url=None,
        suction_pa=None,
        has_mop=None,
        has_obstacle_avoidance=None,
        can_handle_rugs=None,
        rating=4.8,
        source="Test",
    )

    # Act
    score = calculate_score(product, requirements)

    # Assert
    assert score <= 100
