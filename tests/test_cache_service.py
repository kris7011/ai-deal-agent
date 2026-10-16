import app.cache_service as cache_service
from app.cache_service import get_cache_path, load_cache, save_cache


def test_get_cache_path_keeps_existing_naming_for_normal_queries():
    # Arrange
    query = "Robotstøvsuger med moppe"

    # Act
    path = get_cache_path(query)

    # Assert
    assert path == cache_service.CACHE_DIR / "robotstøvsuger_med_moppe.json"


def test_get_cache_path_replaces_characters_that_are_invalid_in_file_names():
    # Arrange
    query = 'laptop? "16GB": <ram>|*'

    # Act
    path = get_cache_path(query)

    # Assert
    assert path.name == "laptop___16gb____ram___.json"


def test_get_cache_path_cannot_escape_the_cache_directory():
    # Arrange
    queries = ["../../etc/passwd", "..\\..\\windows\\win.ini", "/absolute/path"]

    for query in queries:
        # Act
        path = get_cache_path(query)

        # Assert
        assert path.parent == cache_service.CACHE_DIR
        assert "/" not in path.name
        assert "\\" not in path.name


def test_get_cache_path_shortens_very_long_queries_without_collisions():
    # Arrange
    long_query = "robotstøvsuger " * 30
    other_long_query = "robotstøvsuger " * 31

    # Act
    path = get_cache_path(long_query)
    other_path = get_cache_path(other_long_query)

    # Assert
    assert len(path.name) <= 125
    assert path != other_path


def test_save_cache_and_load_cache_round_trip_for_query_with_special_characters():
    # Arrange
    query = "høretelefoner: støjreducerende?"
    data = {"shopping_results": [{"title": "Sony WH-1000XM5"}]}

    # Act
    save_cache(query, data)
    loaded = load_cache(query)

    # Assert
    assert loaded == data


def test_load_cache_returns_none_when_query_is_not_cached():
    # Act
    loaded = load_cache("findes ikke")

    # Assert
    assert loaded is None
