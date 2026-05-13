from app.requirements import SearchRequirements
from app.saved_searches import delete_saved_search, load_saved_searches, save_search


def test_load_saved_searches_returns_empty_list_when_file_does_not_exist(tmp_path):
    # Arrange
    storage_path = tmp_path / "saved_searches.json"

    # Act
    saved_searches = load_saved_searches(storage_path)

    # Assert
    assert saved_searches == []


def test_save_search_creates_file_and_stores_search(tmp_path):
    # Arrange
    storage_path = tmp_path / "saved_searches.json"

    requirements = SearchRequirements(
        product_type="laptop til programmering",
        max_price=8000,
        required_features=["16gb ram"],
        raw_query="laptop til programmering med 16GB RAM under 8000 kr",
    )

    # Act
    save_search(
        query=requirements.raw_query,
        requirements=requirements,
        result_count=40,
        best_score=75,
        storage_path=storage_path,
    )

    saved_searches = load_saved_searches(storage_path)

    # Assert
    assert len(saved_searches) == 1

    saved_search = saved_searches[0]

    assert "id" in saved_search
    assert saved_search["id"]
    assert saved_search["query"] == requirements.raw_query
    assert saved_search["product_type"] == "laptop til programmering"
    assert saved_search["max_price"] == 8000
    assert saved_search["required_features"] == ["16gb ram"]
    assert saved_search["result_count"] == 40
    assert saved_search["best_score"] == 75
    assert "created_at" in saved_search


def test_save_search_appends_to_existing_file(tmp_path):
    # Arrange
    storage_path = tmp_path / "saved_searches.json"

    first_requirements = SearchRequirements(
        product_type="laptop",
        max_price=8000,
        required_features=["16gb ram"],
        raw_query="laptop med 16GB RAM under 8000 kr",
    )

    second_requirements = SearchRequirements(
        product_type="powerbank",
        max_price=None,
        required_features=["usb-c"],
        raw_query="powerbank med usb-c",
    )

    # Act
    save_search(
        query=first_requirements.raw_query,
        requirements=first_requirements,
        result_count=10,
        best_score=80,
        storage_path=storage_path,
    )

    save_search(
        query=second_requirements.raw_query,
        requirements=second_requirements,
        result_count=5,
        best_score=65,
        storage_path=storage_path,
    )

    saved_searches = load_saved_searches(storage_path)

    # Assert
    assert len(saved_searches) == 2
    assert saved_searches[0]["query"] == first_requirements.raw_query
    assert saved_searches[1]["query"] == second_requirements.raw_query


def test_save_search_creates_unique_ids(tmp_path):
    # Arrange
    storage_path = tmp_path / "saved_searches.json"

    requirements = SearchRequirements(
        product_type="laptop",
        max_price=8000,
        required_features=["16gb ram"],
        raw_query="laptop med 16GB RAM under 8000 kr",
    )

    # Act
    save_search(
        query=requirements.raw_query,
        requirements=requirements,
        result_count=10,
        best_score=80,
        storage_path=storage_path,
    )

    save_search(
        query=requirements.raw_query,
        requirements=requirements,
        result_count=10,
        best_score=80,
        storage_path=storage_path,
    )

    saved_searches = load_saved_searches(storage_path)

    # Assert
    assert len(saved_searches) == 2
    assert saved_searches[0]["id"] != saved_searches[1]["id"]

def test_delete_saved_search_removes_existing_search(tmp_path):
    # Arrange
    storage_path = tmp_path / "saved_searches.json"

    requirements = SearchRequirements(
        product_type="laptop",
        max_price=8000,
        required_features=["16gb ram"],
        raw_query="laptop med 16GB RAM under 8000 kr",
    )

    saved_search = save_search(
        query=requirements.raw_query,
        requirements=requirements,
        result_count=10,
        best_score=80,
        storage_path=storage_path,
    )

    # Act
    deleted = delete_saved_search(
        saved_search_id=saved_search["id"],
        storage_path=storage_path,
    )

    saved_searches = load_saved_searches(storage_path)

    # Assert
    assert deleted is True
    assert saved_searches == []


def test_delete_saved_search_returns_false_when_id_does_not_exist(tmp_path):
    # Arrange
    storage_path = tmp_path / "saved_searches.json"

    requirements = SearchRequirements(
        product_type="laptop",
        max_price=8000,
        required_features=["16gb ram"],
        raw_query="laptop med 16GB RAM under 8000 kr",
    )

    save_search(
        query=requirements.raw_query,
        requirements=requirements,
        result_count=10,
        best_score=80,
        storage_path=storage_path,
    )

    # Act
    deleted = delete_saved_search(
        saved_search_id="does-not-exist",
        storage_path=storage_path,
    )

    saved_searches = load_saved_searches(storage_path)

    # Assert
    assert deleted is False
    assert len(saved_searches) == 1