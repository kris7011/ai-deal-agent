from app.feature_matcher import product_matches_feature
from app.models import Product


def create_product(name: str) -> Product:
    return Product(
        name=name,
        price=1000,
        url="",
        image_url=None,
        suction_pa=None,
        has_mop=None,
        has_obstacle_avoidance=None,
        can_handle_rugs=None,
        rating=None,
        source="Test",
    )


def test_product_matches_exact_feature_text():
    # Arrange
    product = create_product("Powerbank with usb-c")

    # Act
    result = product_matches_feature(product, "usb-c")

    # Assert
    assert result is True


def test_product_matches_feature_by_word():
    # Arrange
    product = create_product("Gaming mouse with wireless connection")

    # Act
    result = product_matches_feature(product, "wireless")

    # Assert
    assert result is True


def test_product_does_not_match_unrelated_feature():
    # Arrange
    product = create_product("Basic laptop")

    # Act
    result = product_matches_feature(product, "vandtæt")

    # Assert
    assert result is False


def test_product_matches_feature_case_insensitive():
    # Arrange
    product = create_product("Laptop with USB-C charging")

    # Act
    result = product_matches_feature(product, "usb-c")

    # Assert
    assert result is True

def test_product_matches_danish_feature_with_english_synonym():
    # Arrange
    product = create_product("Wireless gaming mouse")

    # Act
    result = product_matches_feature(product, "trådløs")

    # Assert
    assert result is True


def test_product_matches_waterproof_synonym():
    # Arrange
    product = create_product("Waterproof winter jacket")

    # Act
    result = product_matches_feature(product, "vandtæt")

    # Assert
    assert result is True


def test_product_matches_usb_c_variation():
    # Arrange
    product = create_product("Powerbank with USB C fast charging")

    # Act
    result = product_matches_feature(product, "usb-c")

    # Assert
    assert result is True


def test_product_matches_quiet_synonym():
    # Arrange
    product = create_product("Quiet coffee machine with timer")

    # Act
    result = product_matches_feature(product, "støjsvag")

    # Assert
    assert result is True