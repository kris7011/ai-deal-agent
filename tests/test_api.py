import pytest
from fastapi.testclient import TestClient

import app.product_search as product_search
from app.api import app
from app.cache_service import save_cache
from tests.conftest import shopping_result


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def cached_robot_vacuums() -> str:
    query = "robotstøvsuger med moppe under 5000 kr"
    save_cache(
        query,
        {
            "shopping_results": [
                shopping_result("Basic robotstøvsuger", "1.999 kr.", 3.9),
                shopping_result("Roborock S8 robotstøvsuger med moppe", "4.799,00 kr.", 4.7),
                shopping_result("Premium robotstøvsuger med moppe", "7.999 kr.", 4.8),
                shopping_result("Ukendt pris robotstøvsuger med moppe", None, None),
            ]
            + [shopping_result(f"Ekstra robotstøvsuger {index}", "2.500 kr.") for index in range(10)]
        },
    )
    return query


def test_root_reports_that_the_api_is_running(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "AI Deal Agent API is running"}


def test_search_returns_scored_products_sorted_by_score(client, cached_robot_vacuums):
    # Act
    response = client.post("/api/search", json={"query": cached_robot_vacuums})

    # Assert
    assert response.status_code == 200
    body = response.json()

    assert body["used_cache"] is True
    assert body["count"] == 14
    assert len(body["products"]) == 10
    assert body["requirements"]["max_price"] == 5000
    assert "moppe" in body["requirements"]["required_features"]

    scores = [item["score"] for item in body["products"]]
    assert scores == sorted(scores, reverse=True)

    best = body["products"][0]
    assert best["product"]["name"] == "Roborock S8 robotstøvsuger med moppe"
    assert "Under budget" in best["badges"]
    assert "Matcher: moppe" in best["badges"]


def test_search_does_not_mark_products_with_unknown_price_as_under_budget(client, cached_robot_vacuums):
    # Act
    body = client.post("/api/search", json={"query": cached_robot_vacuums}).json()

    # Assert
    unknown_price = next(
        item for item in body["products"] if item["product"]["name"].startswith("Ukendt pris")
    )
    assert "Under budget" not in unknown_price["badges"]
    assert "? Pris ukendt" in unknown_price["explanations"]


def test_search_trims_the_query_before_looking_up_the_cache(client, cached_robot_vacuums):
    response = client.post("/api/search", json={"query": f"  {cached_robot_vacuums}  "})

    assert response.status_code == 200
    assert response.json()["query"] == cached_robot_vacuums


def test_search_rejects_empty_query(client):
    response = client.post("/api/search", json={"query": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Skriv hvad du leder efter først."


def test_search_without_cache_and_without_live_search_returns_400(client):
    response = client.post("/api/search", json={"query": "ikke cachet"})

    assert response.status_code == 400
    assert "Live-søgning er ikke valgt" in response.json()["detail"]


def test_search_with_live_search_disabled_in_environment_returns_400(client):
    response = client.post("/api/search", json={"query": "ikke cachet", "allow_live_search": True})

    assert response.status_code == 400
    assert "ALLOW_LIVE_SEARCH" in response.json()["detail"]


def test_search_returns_502_when_serpapi_fails(client, monkeypatch):
    # Arrange
    monkeypatch.setenv("ALLOW_LIVE_SEARCH", "true")
    monkeypatch.setenv("SERPAPI_API_KEY", "test-key-not-real")

    def failing_get(url, params, timeout):
        raise product_search.requests.ConnectionError("connection refused")

    monkeypatch.setattr(product_search.requests, "get", failing_get)

    # Act
    response = client.post("/api/search", json={"query": "ny søgning", "allow_live_search": True})

    # Assert
    assert response.status_code == 502
    assert response.json()["detail"] == "Produktsøgningen hos SerpAPI fejlede. Prøv igen senere."
    assert "test-key-not-real" not in response.text


def test_saved_search_lifecycle_create_list_deduplicate_and_delete(client):
    # Create
    created = client.post(
        "/api/saved-searches",
        json={"query": "Laptop til programmering under 8000 kr", "result_count": 12, "best_score": 85},
    )
    assert created.status_code == 200
    saved_search = created.json()["saved_search"]
    assert saved_search["max_price"] == 8000

    # Saving the same query again (different casing and spacing) returns the existing entry
    duplicate = client.post(
        "/api/saved-searches",
        json={"query": "  laptop til   programmering under 8000 kr ", "result_count": 1, "best_score": 1},
    )
    assert duplicate.json()["saved_search"]["id"] == saved_search["id"]

    # List
    listed = client.get("/api/saved-searches").json()
    assert listed["count"] == 1

    # Delete
    deleted = client.delete(f"/api/saved-searches/{saved_search['id']}")
    assert deleted.status_code == 200
    assert client.get("/api/saved-searches").json()["count"] == 0


def test_delete_unknown_saved_search_returns_404(client):
    response = client.delete("/api/saved-searches/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Saved search not found."


@pytest.mark.parametrize(
    "payload",
    [
        {"query": "", "result_count": 1, "best_score": 50},
        {"query": "laptop", "result_count": -1, "best_score": 50},
        {"query": "laptop", "result_count": 1, "best_score": 101},
    ],
)
def test_create_saved_search_validates_input(client, payload):
    response = client.post("/api/saved-searches", json=payload)

    assert response.status_code == 422
