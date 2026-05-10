import json
from pathlib import Path


CACHE_DIR = Path("cache")


def get_cache_path(query: str) -> Path:
    safe_name = (
        query.lower()
        .replace(" ", "_")
        .replace("/", "_")
    )

    return CACHE_DIR / f"{safe_name}.json"


def load_cache(query: str) -> dict | None:
    cache_path = get_cache_path(query)

    if not cache_path.exists():
        return None

    with open(cache_path, encoding="utf-8") as file:
        return json.load(file)


def save_cache(query: str, data: dict) -> None:
    CACHE_DIR.mkdir(exist_ok=True)

    cache_path = get_cache_path(query)

    with open(cache_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)