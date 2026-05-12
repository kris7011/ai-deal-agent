from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


@app.get("/")
def root() -> dict:
    return {"message": "AI Deal Agent API is running"}


@app.post("/api/search")
def search(request: SearchRequest) -> dict:
    requirements = parse_requirements(request.query)

    try:
        products = search_products(request.query)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    scored_products = [
        {
            "product": product,
            "score": calculate_score(product, requirements),
            "explanations": generate_explanation(product, requirements),
        }
        for product in products
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
