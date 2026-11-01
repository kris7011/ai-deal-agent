import json
from contextlib import closing

import pytest

from app.cache_service import get_cache_path, load_cache, save_cache
from app.demo_seed import DEMO_SNAPSHOT_DIR, load_snapshots, seed_demo_data
from app.price_history import connect, get_product_history
from app.product_search import search_products

ROBOT_QUERY = "robotstøvsuger med moppe og høj sugeevne"


def test_committed_snapshots_are_marked_dated_and_fictional():
    snapshots = load_snapshots()

    assert len(snapshots) == 8
    assert {snapshot["query"] for snapshot in snapshots} == {
        ROBOT_QUERY,
        "laptop til programmering med 16GB RAM under 8000 kr",
    }

    for snapshot in snapshots:
        data = snapshot["data"]
        assert data["ai_deal_agent_demo"] is True
        assert "Fictional" in data["demo_notice"]
        assert all(item["product_link"].startswith("https://example.com/") for item in data["shopping_results"])


def test_seeding_builds_history_and_makes_the_query_searchable_offline():
    result = seed_demo_data()

    assert result["snapshots"] == 8
    assert sorted(result["cache_written"]) == sorted(result["queries"])

    search = search_products(ROBOT_QUERY)

    assert search.origin == "demo"
    assert search.fetched_at.isoformat() == "2026-10-31T09:30:00+00:00"


def test_seeding_twice_adds_no_duplicate_history():
    seed_demo_data()
    seed_demo_data()

    # demo-rv-001 is listed in all four snapshots.
    with closing(connect()) as connection:
        product_id = connection.execute(
            "SELECT id FROM products WHERE product_key = 'id:demo-rv-001'"
        ).fetchone()["id"]

    history = get_product_history(product_id)

    assert history["product"]["name"].startswith("Nordvac R5 Mop Pro")
    assert [observation["price"] for observation in history["observations"]] == [4999, 4799, 4799, 4499]
    assert {observation["origin"] for observation in history["observations"]} == {"demo"}


def test_seeding_never_overwrites_an_existing_cache_file():
    real_response = {"shopping_results": [], "search_metadata": {"created_at": "2026-10-30 08:00:00 UTC"}}
    save_cache(ROBOT_QUERY, real_response)

    result = seed_demo_data()

    assert ROBOT_QUERY in result["cache_kept"]
    assert load_cache(ROBOT_QUERY) == real_response


def test_a_snapshot_without_the_demo_marker_is_refused(tmp_path):
    (tmp_path / "real.json").write_text(
        json.dumps({"search_metadata": {"created_at": "2026-10-30 08:00:00 UTC"}, "search_parameters": {"q": "x"}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_snapshots(tmp_path)

    assert not get_cache_path("x").exists()


def test_snapshot_directory_is_inside_the_repository():
    assert DEMO_SNAPSHOT_DIR.is_dir()
