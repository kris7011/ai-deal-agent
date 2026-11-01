import sqlite3
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

import app.api
import app.price_history
import app.product_search as product_search
from app.api import app as api_app
from app.cache_service import save_cache
from app.demo_seed import seed_demo_data
from tests.conftest import shopping_result

ROBOT_QUERY = "robotstøvsuger med moppe og høj sugeevne"
LAPTOP_QUERY = "laptop til programmering med 16GB RAM under 8000 kr"


@pytest.fixture
def client() -> TestClient:
    return TestClient(api_app)


def search(client: TestClient, query: str, **extra) -> dict:
    response = client.post("/api/search", json={"query": query, **extra})
    assert response.status_code == 200, response.text
    return response.json()


def test_search_reports_cached_data_with_its_original_fetch_time(client):
    save_cache(
        "dreame",
        {
            "search_metadata": {"created_at": "2026-10-20 08:00:00 UTC"},
            "shopping_results": [shopping_result("Dreame L10", "3.499 kr.", product_id="p-1")],
        },
    )

    body = search(client, "dreame")

    assert body["data_source"]["origin"] == "cache"
    assert body["data_source"]["fetched_at"] == "2026-10-20T08:00:00Z"
    assert body["data_source"]["status"] in {"aging", "stale"}

    item = body["products"][0]
    assert isinstance(item["product_id"], int)
    assert item["product"]["external_id"] == "p-1"
    assert item["price_history"]["latest_price"] == 3499
    assert item["price_history"]["observation_count"] == 1


def test_repeated_searches_on_the_same_cache_do_not_invent_history(client, monkeypatch):
    save_cache("dreame", {"shopping_results": [shopping_result("Dreame L10", "3.499 kr.")]})
    # Each search happens a day later; only the recording time may change, not the data's age.
    clock = iter(datetime(2026, 11, day, 12, 0, tzinfo=timezone.utc) for day in range(1, 10))
    monkeypatch.setattr(app.price_history, "utc_now", lambda: next(clock))

    for _ in range(3):
        body = search(client, "dreame")

    history = client.get(f"/api/products/{body['products'][0]['product_id']}/price-history").json()
    assert len(history["observations"]) == 1
    assert history["observations"][0]["recorded_at"] == "2026-11-01T12:00:00Z"


def test_live_search_is_recorded_as_live_data(client, monkeypatch):
    monkeypatch.setenv("ALLOW_LIVE_SEARCH", "true")
    monkeypatch.setenv("SERPAPI_API_KEY", "test-key-not-real")
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "search_metadata": {"created_at": "2026-11-01 07:59:00 UTC"},
                "shopping_results": [shopping_result("Dreame L10", "3.299 kr.")],
            }

    def fake_get(url, params, timeout):
        calls.append(params)
        return FakeResponse()

    monkeypatch.setattr(product_search.requests, "get", fake_get)

    live = search(client, "dreame live", allow_live_search=True)
    cached = search(client, "dreame live", allow_live_search=True)

    assert len(calls) == 1
    assert live["data_source"]["origin"] == "live"
    assert live["used_cache"] is False
    assert cached["data_source"]["origin"] == "cache"
    assert cached["data_source"]["fetched_at"] == live["data_source"]["fetched_at"] == "2026-11-01T07:59:00Z"

    history = client.get(f"/api/products/{live['products'][0]['product_id']}/price-history").json()
    assert [observation["origin"] for observation in history["observations"]] == ["live"]


def test_demo_data_is_labelled_as_demo_and_has_a_history(client):
    seed_demo_data()

    body = search(client, ROBOT_QUERY)

    assert body["data_source"]["origin"] == "demo"
    assert body["data_source"]["origin_label"] == "Demodata (fiktive priser)"

    nordvac = next(item for item in body["products"] if item["product"]["name"].startswith("Nordvac R5 Mop Pro"))
    summary = nordvac["price_history"]
    assert summary["observation_count"] == 4
    assert summary["latest_price"] == 4499
    assert summary["highest_price"] == 4999
    assert summary["previous_price"] == 4799
    assert summary["is_lowest_seen"] is True

    history = client.get(f"/api/products/{nordvac['product_id']}/price-history").json()
    assert [observation["observed_at"][:10] for observation in history["observations"]] == [
        "2026-10-10",
        "2026-10-17",
        "2026-10-24",
        "2026-10-31",
    ]


def test_compare_returns_the_selected_products_with_highlights(client):
    seed_demo_data()
    body = search(client, LAPTOP_QUERY)
    ids = {item["product"]["name"]: item["product_id"] for item in body["products"]}

    selected = [
        ids["Kodebog 14 laptop 16GB RAM 512GB SSD"],
        ids["DevBook Air 13 laptop 16GB RAM"],
        ids["Arbejdsbog 15 laptop 8GB RAM"],
    ]
    response = client.get("/api/products/compare", params=[("ids", product_id) for product_id in selected])

    assert response.status_code == 200
    comparison = response.json()
    assert [item["product"]["id"] for item in comparison["items"]] == selected

    highlights = {item["product"]["name"]: item["highlights"] for item in comparison["items"]}
    assert highlights["Arbejdsbog 15 laptop 8GB RAM"] == ["cheapest_now", "lowest_price_seen"]
    assert highlights["DevBook Air 13 laptop 16GB RAM"] == ["best_rated"]
    assert highlights["Kodebog 14 laptop 16GB RAM 512GB SSD"] == ["lowest_price_seen"]
    assert comparison["price_spread"] == 7799 - 3899


@pytest.mark.parametrize("ids", [[1], [1, 1], [1, 2, 3, 4, 5]])
def test_compare_requires_two_to_four_different_products(client, ids):
    seed_demo_data()

    response = client.get("/api/products/compare", params=[("ids", product_id) for product_id in ids])

    assert response.status_code == 400
    assert "mellem 2 og 4" in response.json()["detail"]


def test_compare_reports_unknown_products(client):
    seed_demo_data()

    response = client.get("/api/products/compare", params=[("ids", 1), ("ids", 999)])

    assert response.status_code == 404
    assert "999" in response.json()["detail"]


def test_price_history_of_an_unknown_product_is_not_found(client):
    response = client.get("/api/products/12345/price-history")

    assert response.status_code == 404


def test_search_still_answers_when_the_history_database_fails(client, monkeypatch):
    save_cache("dreame", {"shopping_results": [shopping_result("Dreame L10", "3.499 kr.")]})

    def broken(*args, **kwargs):
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr(app.api, "record_observations", broken)

    body = search(client, "dreame")

    assert body["count"] == 1
    assert body["products"][0]["product_id"] is None
    assert body["products"][0]["price_history"] is None
    assert body["data_source"]["origin"] == "cache"
