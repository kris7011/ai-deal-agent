import logging
import sqlite3
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.settings import get_cors_origins
from app.badge_generator import generate_badges
from app.comparison import MAX_PRODUCTS, MIN_PRODUCTS, build_comparison
from app.explainer import generate_explanation
from app.freshness import describe_freshness
from app.price_history import get_product_history, get_summaries, product_key, record_observations
from app.product_search import SearchServiceError, search_products
from app.requirements_parser import parse_requirements
from app.scorer import calculate_score
from app.saved_searches import delete_saved_search, load_saved_searches, save_search

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    allow_live_search: bool = False


class SaveSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    result_count: int = Field(ge=0)
    best_score: int = Field(ge=0, le=100)


@app.get("/")
def root() -> dict:
    return {"message": "AI Deal Agent API is running"}


@app.post("/api/search")
def search(request: SearchRequest) -> dict:
    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Skriv hvad du leder efter først.",
        )

    requirements = parse_requirements(query)

    try:
        search_result = search_products(
            query,
            allow_live_search=request.allow_live_search,
        )

        products = search_result.products
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
    except SearchServiceError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        )

    product_ids, summaries = _record_price_history(query, search_result)

    scored_products = []

    for product in products:
        score = calculate_score(product, requirements)
        product_id = product_ids.get(product_key(product))

        scored_products.append(
            {
                "product": product,
                "product_id": product_id,
                "price_history": summaries.get(product_id),
                "score": score,
                "badges": generate_badges(product, requirements, score),
                "explanations": generate_explanation(product, requirements),
            }
        )

    scored_products.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return {
        "query": query,
        "count": len(scored_products),
        "used_cache": search_result.used_cache,
        "data_source": describe_freshness(search_result.fetched_at, search_result.origin),
        "requirements": {
            "product_type": requirements.product_type,
            "max_price": requirements.max_price,
            "required_features": requirements.required_features,
        },
        "products": scored_products[:10],
    }


def _record_price_history(query: str, search_result) -> tuple[dict[str, int], dict[int, dict]]:
    """Stores the observed prices. The search still answers if the history database fails."""
    try:
        product_ids = record_observations(
            search_result.products,
            fetched_at=search_result.fetched_at,
            origin=search_result.origin,
            query=query,
        )

        return product_ids, get_summaries(sorted(set(product_ids.values())))
    except sqlite3.Error:
        logger.exception("Price history could not be stored")
        return {}, {}


@app.get("/api/products/compare")
def compare_products(ids: Annotated[list[int], Query()]) -> dict:
    unique_ids = list(dict.fromkeys(ids))

    if not MIN_PRODUCTS <= len(unique_ids) <= MAX_PRODUCTS:
        raise HTTPException(
            status_code=400,
            detail=f"Vælg mellem {MIN_PRODUCTS} og {MAX_PRODUCTS} forskellige produkter at sammenligne.",
        )

    histories = [get_product_history(product_id) for product_id in unique_ids]
    missing = [product_id for product_id, history in zip(unique_ids, histories) if history is None]

    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Produkter blev ikke fundet: {', '.join(str(product_id) for product_id in missing)}.",
        )

    return build_comparison(histories)


@app.get("/api/products/{product_id}/price-history")
def product_price_history(product_id: int) -> dict:
    history = get_product_history(product_id)

    if history is None:
        raise HTTPException(status_code=404, detail="Produktet blev ikke fundet.")

    return history


@app.get("/api/saved-searches")
def get_saved_searches() -> dict:
    saved_searches = load_saved_searches()

    return {
        "count": len(saved_searches),
        "saved_searches": saved_searches,
    }


@app.post("/api/saved-searches")
def create_saved_search(request: SaveSearchRequest) -> dict:
    requirements = parse_requirements(request.query)

    saved_search = save_search(
        query=request.query,
        requirements=requirements,
        result_count=request.result_count,
        best_score=request.best_score,
    )

    return {
        "saved_search": saved_search,
    }


@app.delete("/api/saved-searches/{saved_search_id}")
def remove_saved_search(saved_search_id: str) -> dict:
    deleted = delete_saved_search(saved_search_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Saved search not found.",
        )

    return {
        "deleted": True,
        "id": saved_search_id,
    }
