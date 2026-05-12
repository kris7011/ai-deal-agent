import os
import requests
from dotenv import load_dotenv
from dataclasses import dataclass
from app.models import Product
from app.cache_service import load_cache, save_cache


@dataclass
class ProductSearchResult:
    products: list[Product]
    used_cache: bool


def search_products(query: str, allow_live_search: bool = False) -> ProductSearchResult:
    load_dotenv(override=True)

    live_search_enabled = os.getenv("ALLOW_LIVE_SEARCH", "false").lower() == "true"

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

        if not live_search_enabled:
            raise ValueError(
                "Live-søgning er slået fra i .env. Sæt ALLOW_LIVE_SEARCH=true for at tillade nye SerpAPI-kald."
            )

        api_key = os.getenv("SERPAPI_API_KEY")

        if not api_key:
            raise ValueError("SERPAPI_API_KEY is missing from .env")

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

    return ProductSearchResult(
        products=products,
        used_cache=used_cache,
    )


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
