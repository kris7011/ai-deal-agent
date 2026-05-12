from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.badge_generator import generate_badges
from app.explainer import generate_explanation
from app.product_search import search_products
from app.requirements_parser import parse_requirements
from app.scorer import calculate_score

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    allow_live_search: bool = False


@app.get("/")
def root() -> dict:
    return {"message": "AI Deal Agent API is running"}


@app.post("/api/search")
def search(request: SearchRequest) -> dict:
    requirements = parse_requirements(request.query)

    try:
        search_result = search_products(
            request.query,
            allow_live_search=request.allow_live_search,
        )

        products = search_result.products
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    scored_products = []

    for product in products:
        score = calculate_score(product, requirements)

        scored_products.append(
            {
                "product": product,
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
        "query": request.query,
        "count": len(scored_products),
        "used_cache": search_result.used_cache,
        "requirements": {
            "product_type": requirements.product_type,
            "max_price": requirements.max_price,
            "required_features": requirements.required_features,
        },
        "products": scored_products[:10],
    }
