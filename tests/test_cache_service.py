import json

import pytest

import app.cache_service as cache_service
from app.cache_service import get_cache_key, get_cache_path, load_cache, save_cache


def write_legacy_cache_file(name: str, data: dict) -> None:
    cache_service.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (cache_service.CACHE_DIR / f"{name}.json").write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )


def serpapi_response(query: str, title: str) -> dict:
    return {
        "search_parameters": {"engine": "google_shopping", "q": query},
        "shopping_results": [{"title": title}],
    }


def test_cache_key_is_stable_and_readable():
    # The key must never change between runs or Python versions, or existing caches are lost.
    assert get_cache_key("Robotstøvsuger med moppe") == "robotstøvsuger_med_moppe-e393725d9d5c75d7"


@pytest.mark.parametrize(
    "queries",
    [
        ["laptop/16GB", "laptop?16GB", "laptop 16GB", "laptop_16GB", "laptop:16GB", "laptop\\16GB"],
        ["a b", "a_b", "a/b"],
    ],
)
def test_different_queries_never_share_a_cache_file(queries):
    paths = {get_cache_path(query) for query in queries}

    assert len(paths) == len(queries)


def test_cache_key_ignores_case_and_repeated_whitespace():
    assert get_cache_key("  Laptop   16GB ") == get_cache_key("laptop 16gb")


def test_cache_path_stays_inside_the_cache_directory():
    for query in ["../../etc/passwd", "..\\..\\windows\\win.ini", "/absolute/path", "???", ""]:
        path = get_cache_path(query)

        assert path.parent == cache_service.CACHE_DIR
        assert "/" not in path.name
        assert "\\" not in path.name
        assert not path.name.startswith(".")


def test_cache_file_names_have_a_bounded_length():
    assert len(get_cache_path("robotstøvsuger " * 50).name) <= 60 + 1 + 16 + len(".json")


def test_colliding_queries_keep_separate_cached_data():
    # Arrange
    save_cache("laptop/16GB", {"shopping_results": [{"title": "slash"}]})
    save_cache("laptop?16GB", {"shopping_results": [{"title": "question mark"}]})

    # Act / Assert
    assert load_cache("laptop/16GB")["shopping_results"][0]["title"] == "slash"
    assert load_cache("laptop?16GB")["shopping_results"][0]["title"] == "question mark"


def test_load_cache_returns_none_when_query_is_not_cached():
    assert load_cache("findes ikke") is None


def test_legacy_cache_file_is_used_when_it_belongs_to_the_query_and_is_migrated():
    # Arrange: a file written by the old naming scheme (lowercase, spaces as underscores)
    query = "Robotstøvsuger med moppe"
    write_legacy_cache_file("robotstøvsuger_med_moppe", serpapi_response(query, "Roborock S8"))

    # Act
    loaded = load_cache(query)

    # Assert
    assert loaded["shopping_results"][0]["title"] == "Roborock S8"
    assert get_cache_path(query).exists()


def test_legacy_cache_file_from_a_colliding_query_is_ignored():
    # Arrange: the old scheme wrote "laptop_16gb.json" for "laptop 16GB", "laptop_16GB" and "laptop/16GB"
    write_legacy_cache_file("laptop_16gb", serpapi_response("laptop/16GB", "Wrong product"))

    # Act / Assert
    assert load_cache("laptop 16GB") is None
    assert load_cache("laptop_16GB") is None
    assert load_cache("laptop/16GB")["shopping_results"][0]["title"] == "Wrong product"


def test_legacy_cache_file_without_recorded_query_is_ignored():
    # Without search_parameters.q there is no way to prove which query produced the file.
    write_legacy_cache_file("dreame_l10", {"shopping_results": [{"title": "Dreame L10"}]})

    assert load_cache("dreame l10") is None


def test_legacy_lookup_is_skipped_for_names_that_could_escape_the_cache_directory():
    # Arrange: a JSON file outside the cache folder that an unsafe legacy name would point to
    outside = cache_service.CACHE_DIR.parent / "secret.json"
    outside.parent.mkdir(parents=True, exist_ok=True)
    outside.write_text(json.dumps(serpapi_response("..\\secret", "secret")), encoding="utf-8")

    # Act / Assert
    assert load_cache("..\\secret") is None


def test_unreadable_legacy_cache_file_is_ignored():
    cache_service.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (cache_service.CACHE_DIR / "broken.json").write_text("{not json", encoding="utf-8")

    assert load_cache("broken") is None
