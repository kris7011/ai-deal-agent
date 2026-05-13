import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.requirements import SearchRequirements

DEFAULT_STORAGE_PATH = Path("data/saved_searches.json")


def load_saved_searches(
    storage_path: Path | str = DEFAULT_STORAGE_PATH,
) -> list[dict]:
    path = Path(storage_path)

    if not path.exists():
        return []

    with open(path, encoding="utf-8") as file:
        return json.load(file)


def save_search(
    query: str,
    requirements: SearchRequirements,
    result_count: int,
    best_score: int,
    storage_path: Path | str = DEFAULT_STORAGE_PATH,
) -> dict:
    path = Path(storage_path)

    saved_searches = load_saved_searches(path)

    normalized_query = _normalize_query(query)

    for saved_search in saved_searches:
        existing_query = saved_search.get("query", "")

        if _normalize_query(existing_query) == normalized_query:
            return saved_search

    saved_search = {
        "id": str(uuid4()),
        "query": query,
        "product_type": requirements.product_type,
        "max_price": requirements.max_price,
        "required_features": requirements.required_features,
        "result_count": result_count,
        "best_score": best_score,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    saved_searches.append(saved_search)

    path.parent.mkdir(exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(saved_searches, file, indent=2, ensure_ascii=False)

    return saved_search


def delete_saved_search(
    saved_search_id: str,
    storage_path: Path | str = DEFAULT_STORAGE_PATH,
) -> bool:
    path = Path(storage_path)

    saved_searches = load_saved_searches(path)

    updated_saved_searches = [
        saved_search
        for saved_search in saved_searches
        if saved_search.get("id") != saved_search_id
    ]

    if len(updated_saved_searches) == len(saved_searches):
        return False

    path.parent.mkdir(exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(updated_saved_searches, file, indent=2, ensure_ascii=False)

    return True


def _normalize_query(query: str) -> str:
    return " ".join(query.lower().split())
