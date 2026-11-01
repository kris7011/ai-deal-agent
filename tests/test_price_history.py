import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

import app.price_history as price_history
from app.models import Product
from app.price_history import (
    get_product_history,
    get_summaries,
    product_key,
    record_observations,
    summarize,
)

OCT_10 = datetime(2026, 10, 10, 9, 0, tzinfo=timezone.utc)
OCT_17 = OCT_10 + timedelta(days=7)
OCT_24 = OCT_17 + timedelta(days=7)
NOW = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)


def product(name: str = "Nordvac R5", price: int = 4999, source: str = "Demo Shop", **extra) -> Product:
    values = {
        "name": name,
        "price": price,
        "url": f"https://example.com/{name}",
        "image_url": None,
        "suction_pa": None,
        "has_mop": None,
        "has_obstacle_avoidance": None,
        "can_handle_rugs": None,
        "rating": 4.5,
        "source": source,
    }
    values.update(extra)
    return Product(**values)


def record(products: list[Product], fetched_at: datetime, origin: str = "cache") -> dict[str, int]:
    return record_observations(products, fetched_at=fetched_at, origin=origin, query="robot", now=NOW)


def test_product_key_prefers_the_external_id_and_otherwise_normalises_name_and_shop():
    assert product_key(product(external_id="abc")) == "id:abc"
    assert product_key(product(name="  Nordvac   R5 ", source="DEMO shop")) == "name:nordvac r5|demo shop"


def test_history_grows_with_new_fetches_and_summarises_the_change():
    record([product(price=4999)], OCT_10)
    record([product(price=4799)], OCT_17)
    ids = record([product(price=4499)], OCT_24)

    history = get_product_history(ids[product_key(product())], now=NOW)

    assert [observation["price"] for observation in history["observations"]] == [4999, 4799, 4499]
    assert history["observations"][0]["observed_at"] == "2026-10-10T09:00:00Z"
    assert history["product"]["first_seen_at"] == "2026-10-10T09:00:00Z"
    assert history["product"]["last_seen_at"] == "2026-10-24T09:00:00Z"

    summary = history["summary"]
    assert summary["observation_count"] == 3
    assert summary["latest_price"] == 4499
    assert summary["lowest_price"] == 4499
    assert summary["highest_price"] == 4999
    assert summary["previous_price"] == 4799
    assert summary["price_change"] == -300
    assert summary["is_lowest_seen"] is True
    assert summary["freshness"]["status"] == "fresh"
    assert summary["freshness"]["origin"] == "cache"


def test_reading_the_same_response_again_does_not_add_history():
    for _ in range(3):
        ids = record([product(price=4999)], OCT_10)

    summary = get_summaries(list(ids.values()), now=NOW)[ids[product_key(product())]]

    assert summary["observation_count"] == 1
    assert summary["is_lowest_seen"] is False


def test_products_without_a_price_are_stored_without_observations():
    ids = record([product(price=0)], OCT_10)

    history = get_product_history(ids[product_key(product())], now=NOW)

    assert history["observations"] == []
    assert history["summary"]["latest_price"] is None
    assert history["summary"]["freshness"] is None


def test_an_older_snapshot_does_not_overwrite_newer_product_details():
    ids = record([product(rating=4.8)], OCT_17)
    record([product(rating=3.0)], OCT_10)

    history = get_product_history(ids[product_key(product())], now=NOW)

    assert history["product"]["rating"] == 4.8
    assert history["product"]["first_seen_at"] == "2026-10-10T09:00:00Z"
    assert history["product"]["last_seen_at"] == "2026-10-17T09:00:00Z"


def test_previous_price_skips_repeated_identical_prices():
    observations = [
        {"price": 3499, "observed_at": "2026-10-10T09:00:00Z", "origin": "demo"},
        {"price": 3299, "observed_at": "2026-10-17T09:00:00Z", "origin": "demo"},
        {"price": 3299, "observed_at": "2026-10-24T09:00:00Z", "origin": "demo"},
    ]

    summary = summarize(observations, now=NOW)

    assert summary["previous_price"] == 3499
    assert summary["price_change"] == -200


def test_unknown_product_has_no_history():
    assert get_product_history(999, now=NOW) is None


def test_an_unknown_origin_is_refused():
    with pytest.raises(ValueError):
        record([product()], OCT_10, origin="guess")


def test_the_database_rejects_non_positive_prices():
    ids = record([product()], OCT_10)

    with sqlite3.connect(price_history.DEFAULT_DB_PATH) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO price_observations (product_id, price, observed_at, recorded_at, origin, query) "
                "VALUES (?, 0, '2026-10-11T00:00:00Z', '2026-10-11T00:00:00Z', 'demo', 'x')",
                (next(iter(ids.values())),),
            )
