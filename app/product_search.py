import logging
from dataclasses import dataclass

import requests

from app.cache_service import load_cache, save_cache
from app.models import Product
from app.settings import get_serpapi_api_key, is_live_search_enabled

logger = logging.getLogger(__name__)


class SearchServiceError(Exception):
    """Raised when the external product search service (SerpAPI) fails or returns an error."""


@dataclass
class ProductSearchResult:
    products: list[Product]
    used_cache: bool


def search_products(query: str, allow_live_search: bool = False) -> ProductSearchResult:
    cached_data = load_cache(query)
    used_cache = False

    if cached_data is not None:
        data = cached_data
        used_cache = True
    else:
        if not allow_live_search:
            raise ValueError(
                "Ingen cache fundet for denne søgning. Live-søgning er ikke valgt."
            )

        if not is_live_search_enabled():
            raise ValueError(
                "Live-søgning er slået fra i .env. Sæt ALLOW_LIVE_SEARCH=true for at tillade nye SerpAPI-kald."
            )

        api_key = get_serpapi_api_key()

        if not api_key:
            raise ValueError("SERPAPI_API_KEY is missing from .env")

        data = _fetch_from_serpapi(query, api_key)
        save_cache(query, data)

    shopping_results = data.get("shopping_results", [])

    products = []

    for item in shopping_results:
        product = Product(
            name=item.get("title", "Unknown product"),
            price=_parse_price(item.get("price")),
            url=_get_product_url(item),
            image_url=item.get("thumbnail"),
            suction_pa=None,
            has_mop=None,
            has_obstacle_avoidance=None,
            can_handle_rugs=None,
            rating=item.get("rating"),
            source=item.get("source", "Google Shopping"),
        )

        products.append(product)

    return ProductSearchResult(
        products=products,
        used_cache=used_cache,
    )


def _fetch_from_serpapi(query: str, api_key: str) -> dict:
    try:
        response = requests.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google_shopping",
                "q": query,
                "api_key": api_key,
                "gl": "dk",
                "hl": "da",
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as error:
        # Log the type only: request exceptions can contain the URL including the API key.
        logger.warning("SerpAPI request failed: %s", type(error).__name__)
        raise SearchServiceError(
            "Produktsøgningen hos SerpAPI fejlede. Prøv igen senere."
        ) from error

    if not isinstance(data, dict) or "error" in data:
        logger.warning("SerpAPI returned an error response")
        raise SearchServiceError("SerpAPI returnerede en fejl. Prøv igen senere.")

    return data


def _parse_price(price_text: str | None) -> int:
    if not price_text:
        return 0

    cleaned = (
        price_text.replace("kr.", "")
        .replace("kr", "")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )

    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def _get_product_url(item: dict) -> str:
    return (
        item.get("link")
        or item.get("product_link")
        or item.get("serpapi_product_api")
        or ""
    )
