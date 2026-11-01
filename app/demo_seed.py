"""Loads the committed demonstration snapshots so the app can be shown without any SerpAPI call.

    python -m app.demo_seed

The snapshots in demo/snapshots are fictional (invented products, shops and prices) and carry the
`ai_deal_agent_demo` marker, so the API and the frontend always label them as demo data.

- Every snapshot is stored in the price history with its own date, giving a real history to show.
- The newest snapshot of each query is written to the cache, so searching for that query works
  offline. An existing cache file is never overwritten: real cached searches are kept.
- Running it again adds nothing new: observations are unique per product, time and price.
"""

import json
from pathlib import Path

from app.cache_service import get_cache_path, save_cache
from app.price_history import record_observations
from app.product_search import DEMO_MARKER, products_from_serpapi, read_fetched_at
from app.settings import PROJECT_ROOT

DEMO_SNAPSHOT_DIR = PROJECT_ROOT / "demo" / "snapshots"


def load_snapshots(snapshot_dir: Path | None = None) -> list[dict]:
    """Reads the demo snapshots, oldest first. Files without the demo marker are refused."""
    snapshot_dir = snapshot_dir or DEMO_SNAPSHOT_DIR
    snapshots = []

    for path in sorted(snapshot_dir.glob("*.json")):
        with open(path, encoding="utf-8") as file:
            data = json.load(file)

        fetched_at = read_fetched_at(data)

        if data.get(DEMO_MARKER) is not True or fetched_at is None:
            raise ValueError(f"{path.name} is not a dated demo snapshot.")

        snapshots.append(
            {
                "query": data["search_parameters"]["q"],
                "fetched_at": fetched_at,
                "data": data,
            }
        )

    return sorted(snapshots, key=lambda snapshot: snapshot["fetched_at"])


def seed_demo_data(snapshot_dir: Path | None = None, db_path: Path | str | None = None) -> dict:
    snapshots = load_snapshots(snapshot_dir)
    newest_by_query: dict[str, dict] = {}

    for snapshot in snapshots:
        record_observations(
            products_from_serpapi(snapshot["data"]),
            fetched_at=snapshot["fetched_at"],
            origin="demo",
            query=snapshot["query"],
            db_path=db_path,
        )
        newest_by_query[snapshot["query"]] = snapshot

    cache_written = []
    cache_kept = []

    for query, snapshot in newest_by_query.items():
        if get_cache_path(query).exists():
            cache_kept.append(query)
        else:
            save_cache(query, snapshot["data"])
            cache_written.append(query)

    return {
        "snapshots": len(snapshots),
        "queries": list(newest_by_query),
        "cache_written": cache_written,
        "cache_kept": cache_kept,
    }


def main() -> None:
    result = seed_demo_data()

    print(f"Loaded {result['snapshots']} demo snapshots into the price history.")

    for query in result["cache_written"]:
        print(f"  cache written: {query}")

    for query in result["cache_kept"]:
        print(f"  cache kept (already existed, not overwritten): {query}")


if __name__ == "__main__":
    main()
