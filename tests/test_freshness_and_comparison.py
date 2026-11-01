from datetime import datetime, timedelta, timezone

import pytest

from app.comparison import build_comparison
from app.freshness import describe_freshness

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("age", "status"),
    [
        (timedelta(hours=2), "fresh"),
        (timedelta(hours=23, minutes=59), "fresh"),
        (timedelta(hours=24), "aging"),
        (timedelta(days=6, hours=23), "aging"),
        (timedelta(days=7), "stale"),
    ],
)
def test_freshness_status_depends_on_the_age_of_the_data(age, status):
    freshness = describe_freshness(NOW - age, "cache", now=NOW)

    assert freshness["status"] == status
    assert freshness["age_hours"] == round(age.total_seconds() / 3600, 1)


def test_freshness_names_the_origin_and_the_fetch_time():
    freshness = describe_freshness(datetime(2026, 10, 31, 9, 30, tzinfo=timezone.utc), "demo", now=NOW)

    assert freshness["origin"] == "demo"
    assert freshness["origin_label"] == "Demodata (fiktive priser)"
    assert freshness["fetched_at"] == "2026-10-31T09:30:00Z"
    assert freshness["status_label"] == "Ældre"


def entry(product_id: int, latest_price: int | None, rating: float | None, is_lowest_seen: bool = False) -> dict:
    return {
        "product": {"id": product_id, "name": f"Product {product_id}", "rating": rating},
        "summary": {"latest_price": latest_price, "is_lowest_seen": is_lowest_seen},
    }


def test_comparison_marks_the_cheapest_and_best_rated_products():
    comparison = build_comparison(
        [
            entry(1, 4499, 4.6, is_lowest_seen=True),
            entry(2, 3299, 4.3),
            entry(3, 6799, 4.8),
        ]
    )

    highlights = {item["product"]["id"]: item["highlights"] for item in comparison["items"]}

    assert comparison["count"] == 3
    assert comparison["price_spread"] == 6799 - 3299
    assert highlights == {
        1: ["lowest_price_seen"],
        2: ["cheapest_now"],
        3: ["best_rated"],
    }


def test_comparison_marks_ties_and_ignores_missing_values():
    comparison = build_comparison(
        [
            entry(1, 2999, None),
            entry(2, 2999, 4.0),
            entry(3, None, None),
        ]
    )

    highlights = {item["product"]["id"]: item["highlights"] for item in comparison["items"]}

    # Only one product has a rating, so "best rated" says nothing and is not given.
    assert highlights == {1: ["cheapest_now"], 2: ["cheapest_now"], 3: []}
    assert comparison["price_spread"] == 0
