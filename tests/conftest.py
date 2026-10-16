import pytest
import requests

import app.cache_service
import app.saved_searches


@pytest.fixture(autouse=True)
def isolate_tests(monkeypatch, tmp_path):
    """Keep every test offline, free of charge and away from the real cache and data folders."""

    def block_network(*args, **kwargs):
        raise AssertionError("Network access is disabled in tests. Mock the SerpAPI call instead.")

    # requests.get/post all go through Session.request, so this blocks any real HTTP call.
    monkeypatch.setattr(requests.sessions.Session, "request", block_network)

    # Real environment variables (or a local .env) must never enable paid live searches in tests.
    monkeypatch.setenv("ALLOW_LIVE_SEARCH", "false")
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)

    monkeypatch.setattr(app.cache_service, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(app.saved_searches, "DEFAULT_STORAGE_PATH", tmp_path / "data" / "saved_searches.json")


def shopping_result(title: str, price: str | None, rating: float | None = None, **extra) -> dict:
    """Builds one item shaped like SerpAPI's Google Shopping `shopping_results` entries."""
    item = {
        "title": title,
        "price": price,
        "rating": rating,
        "thumbnail": f"https://example.com/{title.replace(' ', '-').lower()}.jpg",
        "product_link": f"https://www.google.com/shopping/product/{abs(hash(title))}",
        "source": "Test Shop",
    }
    item.update(extra)
    return item
