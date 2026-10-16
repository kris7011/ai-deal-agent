import pytest
import requests

import app.product_search as product_search
from app.cache_service import load_cache, save_cache
from app.product_search import SearchServiceError, _parse_price, search_products
from tests.conftest import shopping_result


class FakeResponse:
    def __init__(self, data, status_code: int = 200):
        self._data = data
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self):
        return self._data


def enable_live_search(monkeypatch) -> None:
    monkeypatch.setenv("ALLOW_LIVE_SEARCH", "true")
    monkeypatch.setenv("SERPAPI_API_KEY", "test-key-not-real")


@pytest.mark.parametrize(
    ("price_text", "expected"),
    [
        ("4.999,00 kr.", 4999),
        ("1.299 kr", 1299),
        ("349,95 kr.", 349),
        ("kr 2.000", 2000),
        (None, 0),
        ("", 0),
        ("Se pris", 0),
    ],
)
def test_parse_price_handles_danish_price_formats(price_text, expected):
    assert _parse_price(price_text) == expected


def test_search_products_uses_cache_without_calling_serpapi():
    # Arrange
    save_cache("robotstøvsuger", {"shopping_results": [shopping_result("Roborock S8", "4.999,00 kr.", 4.6)]})

    # Act
    result = search_products("robotstøvsuger")

    # Assert
    assert result.used_cache is True
    assert [product.name for product in result.products] == ["Roborock S8"]
    assert result.products[0].price == 4999
    assert result.products[0].rating == 4.6
    assert result.products[0].url.startswith("https://www.google.com/shopping/product/")


def test_search_products_requires_explicit_live_search_when_not_cached():
    with pytest.raises(ValueError, match="Live-søgning er ikke valgt"):
        search_products("ikke cachet")


def test_search_products_respects_disabled_live_search_in_environment():
    with pytest.raises(ValueError, match="ALLOW_LIVE_SEARCH"):
        search_products("ikke cachet", allow_live_search=True)


def test_search_products_requires_api_key_for_live_search(monkeypatch):
    # Arrange
    monkeypatch.setenv("ALLOW_LIVE_SEARCH", "true")

    # Act / Assert
    with pytest.raises(ValueError, match="SERPAPI_API_KEY"):
        search_products("ikke cachet", allow_live_search=True)


def test_live_search_calls_serpapi_once_and_caches_the_response(monkeypatch):
    # Arrange
    enable_live_search(monkeypatch)
    calls = []

    def fake_get(url, params, timeout):
        calls.append(params)
        return FakeResponse({"shopping_results": [shopping_result("Dreame L10", "3.499 kr.")]})

    monkeypatch.setattr(product_search.requests, "get", fake_get)

    # Act
    first = search_products("dreame", allow_live_search=True)
    second = search_products("dreame", allow_live_search=True)

    # Assert
    assert first.used_cache is False
    assert second.used_cache is True
    assert len(calls) == 1
    assert calls[0]["engine"] == "google_shopping"
    assert calls[0]["gl"] == "dk"
    assert load_cache("dreame") is not None


def test_live_search_raises_search_service_error_on_network_failure(monkeypatch):
    # Arrange
    enable_live_search(monkeypatch)

    def fake_get(url, params, timeout):
        raise requests.Timeout("timed out")

    monkeypatch.setattr(product_search.requests, "get", fake_get)

    # Act / Assert
    with pytest.raises(SearchServiceError):
        search_products("dreame", allow_live_search=True)

    assert load_cache("dreame") is None


def test_live_search_raises_search_service_error_on_http_error(monkeypatch):
    # Arrange
    enable_live_search(monkeypatch)
    monkeypatch.setattr(
        product_search.requests,
        "get",
        lambda url, params, timeout: FakeResponse({"error": "Invalid API key."}, status_code=401),
    )

    # Act / Assert
    with pytest.raises(SearchServiceError):
        search_products("dreame", allow_live_search=True)


def test_live_search_does_not_cache_serpapi_error_payloads(monkeypatch):
    # Arrange
    enable_live_search(monkeypatch)
    monkeypatch.setattr(
        product_search.requests,
        "get",
        lambda url, params, timeout: FakeResponse({"error": "Your account has run out of searches."}),
    )

    # Act / Assert
    with pytest.raises(SearchServiceError):
        search_products("dreame", allow_live_search=True)

    assert load_cache("dreame") is None
