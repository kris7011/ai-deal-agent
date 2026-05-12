from app.requirements_parser import parse_requirements


def test_parse_robot_vacuum_with_features():
    # Arrange
    query = "robotstøvsuger med moppe og høj sugeevne"

    # Act
    requirements = parse_requirements(query)

    # Assert
    assert requirements.product_type == "robotstøvsuger"
    assert requirements.max_price is None
    assert requirements.required_features == ["moppe", "høj sugeevne"]


def test_parse_laptop_with_feature_and_budget():
    # Arrange
    query = "laptop til programmering med 16GB RAM under 8000 kr"

    # Act
    requirements = parse_requirements(query)

    # Assert
    assert requirements.product_type == "laptop til programmering"
    assert requirements.max_price == 8000
    assert requirements.required_features == ["16gb ram"]


def test_parse_product_with_budget_and_front_feature():
    # Arrange
    query = "vandtæt vinterjakke til herre under 1500 kr"

    # Act
    requirements = parse_requirements(query)

    # Assert
    assert requirements.product_type == "vinterjakke til herre"
    assert requirements.max_price == 1500
    assert requirements.required_features == ["vandtæt"]


def test_parse_empty_feature_list_when_no_requirements_found():
    # Arrange
    query = "gaming mus"

    # Act
    requirements = parse_requirements(query)

    # Assert
    assert requirements.product_type == "gaming mus"
    assert requirements.max_price is None
    assert requirements.required_features == []


def test_parse_wireless_gaming_mouse_with_budget():
    # Arrange
    query = "trådløs gaming mus under 1000 kr"

    # Act
    requirements = parse_requirements(query)

    # Assert
    assert requirements.product_type == "gaming mus"
    assert requirements.max_price == 1000
    assert requirements.required_features == ["trådløs"]


def test_parse_quiet_coffee_machine_with_timer_and_budget():
    # Arrange
    query = "støjsvag kaffemaskine med timer under 1500 kr"

    # Act
    requirements = parse_requirements(query)

    # Assert
    assert requirements.product_type == "kaffemaskine"
    assert requirements.max_price == 1500
    assert requirements.required_features == ["støjsvag", "timer"]


def test_parse_powerful_powerbank_with_usb_c():
    # Arrange
    query = "kraftig powerbank med usb-c"

    # Act
    requirements = parse_requirements(query)

    # Assert
    assert requirements.product_type == "powerbank"
    assert requirements.max_price is None
    assert requirements.required_features == ["kraftig", "usb-c"]
