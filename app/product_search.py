import os
import requests
from dotenv import load_dotenv

from app.models import Product
from app.cache_service import load_cache, save_cache


def search_products(query: str) -> list[Product]:
    load_dotenv()

    api_key = os.getenv("SERPAPI_API_KEY")
    allow_live_search = os.getenv("ALLOW_LIVE_SEARCH", "false").lower() == "true"

    if not api_key:
        raise ValueError("SERPAPI_API_KEY is missing from .env")

    cached_data = load_cache(query)

    if cached_data is not None:
        data = cached_data
    else:
        if not allow_live_search:
            raise ValueError(
                "No cached result found and live search is disabled. "
                "Set ALLOW_LIVE_SEARCH=true in .env to allow a new SerpAPI call."
            )

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

    return products


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
