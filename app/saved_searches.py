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

    saved_searches = load_saved_searches(path)
    saved_searches.append(saved_search)

    path.parent.mkdir(exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(saved_searches, file, indent=2, ensure_ascii=False)

    return saved_search
