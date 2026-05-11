from fastapi import FastAPI
from pydantic import BaseModel

from app.explainer import generate_explanation
from app.product_enricher import enrich_products
from app.product_search import search_products
from app.requirements_parser import parse_requirements
from app.scorer import calculate_score

app = FastAPI()


class SearchRequest(BaseModel):
    query: str


@app.get("/")
def root() -> dict:
    return {"message": "AI Deal Agent API is running"}


@app.post("/api/search")
def search(request: SearchRequest) -> dict:
    requirements = parse_requirements(request.query)

    products = search_products(request.query)
    enriched_products = enrich_products(products)

    scored_products = [
        {
            "product": product,
            "score": calculate_score(product, requirements),
            "explanations": generate_explanation(product, requirements),
        }
        for product in enriched_products
    ]

    scored_products.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return {
        "query": request.query,
        "count": len(scored_products),
        "products": scored_products[:10],
    }
