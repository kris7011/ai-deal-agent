"""Price history stored in SQLite.

Every search stores the prices it saw as observations. An observation is dated with the time the
data was fetched from the source, not the time it was read from the cache, and the same product,
time and price is stored only once. Re-reading a cached response therefore never invents history:
the history only grows when genuinely new data arrives (a live search or newly seeded data).
"""

import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from app.freshness import describe_freshness, parse_iso, to_iso, utc_now
from app.models import Product
from app.settings import PROJECT_ROOT

DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "price_history.sqlite3"

ORIGINS = ("live", "cache", "demo")

SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    product_key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL,
    image_url TEXT,
    rating REAL,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);

CREATE TABLE price_observations (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price INTEGER NOT NULL CHECK (price > 0),
    currency TEXT NOT NULL DEFAULT 'DKK',
    observed_at TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    origin TEXT NOT NULL CHECK (origin IN ('live', 'cache', 'demo')),
    query TEXT NOT NULL,
    UNIQUE (product_id, observed_at, price)
);

CREATE INDEX ix_price_observations_product_time ON price_observations (product_id, observed_at);
"""


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    _migrate(connection)

    return connection


def _migrate(connection: sqlite3.Connection) -> None:
    version = connection.execute("PRAGMA user_version").fetchone()[0]

    if version < 1:
        with connection:
            connection.executescript(_SCHEMA)
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def product_key(product: Product) -> str:
    """Identifies the same offer across searches: SerpAPI's product id when known, else name and shop."""
    if product.external_id:
        return f"id:{product.external_id}"

    return f"name:{normalize_text(product.name)}|{normalize_text(product.source)}"


def record_observations(
    products: list[Product],
    fetched_at: datetime,
    origin: str,
    query: str,
    now: datetime | None = None,
    db_path: Path | str | None = None,
) -> dict[str, int]:
    """Stores the products and their prices; returns the database id for each product key.

    Products without a known price are stored (so they can be compared) but get no observation.
    """
    if origin not in ORIGINS:
        raise ValueError(f"Unknown data origin '{origin}'.")

    observed_at = to_iso(fetched_at)
    recorded_at = to_iso(now or utc_now())
    product_ids: dict[str, int] = {}

    with closing(connect(db_path)) as connection, connection:
        for product in products:
            key = product_key(product)

            connection.execute(
                """
                INSERT INTO products (product_key, name, source, url, image_url, rating, first_seen_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (product_key) DO UPDATE SET
                    name = CASE WHEN excluded.last_seen_at >= last_seen_at THEN excluded.name ELSE name END,
                    url = CASE WHEN excluded.last_seen_at >= last_seen_at THEN excluded.url ELSE url END,
                    image_url = CASE WHEN excluded.last_seen_at >= last_seen_at THEN excluded.image_url ELSE image_url END,
                    rating = CASE WHEN excluded.last_seen_at >= last_seen_at THEN excluded.rating ELSE rating END,
                    first_seen_at = MIN(first_seen_at, excluded.first_seen_at),
                    last_seen_at = MAX(last_seen_at, excluded.last_seen_at)
                """,
                (key, product.name, product.source, product.url, product.image_url, product.rating,
                 observed_at, observed_at),
            )

            product_id = connection.execute(
                "SELECT id FROM products WHERE product_key = ?", (key,)
            ).fetchone()["id"]
            product_ids[key] = product_id

            if product.price > 0:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO price_observations
                        (product_id, price, observed_at, recorded_at, origin, query)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (product_id, product.price, observed_at, recorded_at, origin, query),
                )

    return product_ids


def get_summaries(
    product_ids: list[int],
    now: datetime | None = None,
    db_path: Path | str | None = None,
) -> dict[int, dict]:
    """Price history summary per product id; products without observations get an empty summary."""
    if not product_ids:
        return {}

    with closing(connect(db_path)) as connection:
        observations = _load_observations(connection, product_ids)

    return {
        product_id: summarize(observations.get(product_id, []), now)
        for product_id in product_ids
    }


def get_product_history(
    product_id: int,
    now: datetime | None = None,
    db_path: Path | str | None = None,
) -> dict | None:
    with closing(connect(db_path)) as connection:
        product = connection.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()

        if product is None:
            return None

        observations = _load_observations(connection, [product_id]).get(product_id, [])

    return {
        "product": _product_to_dict(product),
        "observations": observations,
        "summary": summarize(observations, now),
    }


def summarize(observations: list[dict], now: datetime | None = None) -> dict:
    """Summarises observations that are ordered from oldest to newest."""
    if not observations:
        return {
            "observation_count": 0,
            "latest_price": None,
            "latest_observed_at": None,
            "first_observed_at": None,
            "lowest_price": None,
            "highest_price": None,
            "previous_price": None,
            "price_change": None,
            "is_lowest_seen": False,
            "freshness": None,
        }

    latest = observations[-1]
    prices = [observation["price"] for observation in observations]

    # The previous price is the last observed price that differs from today's price, so repeated
    # identical observations do not hide a real change.
    previous_price = next(
        (observation["price"] for observation in reversed(observations[:-1])
         if observation["price"] != latest["price"]),
        None,
    )

    return {
        "observation_count": len(observations),
        "latest_price": latest["price"],
        "latest_observed_at": latest["observed_at"],
        "first_observed_at": observations[0]["observed_at"],
        "lowest_price": min(prices),
        "highest_price": max(prices),
        "previous_price": previous_price,
        "price_change": latest["price"] - previous_price if previous_price is not None else None,
        "is_lowest_seen": len(set(prices)) > 1 and latest["price"] == min(prices),
        "freshness": describe_freshness(parse_iso(latest["observed_at"]), latest["origin"], now),
    }


def _load_observations(connection: sqlite3.Connection, product_ids: list[int]) -> dict[int, list[dict]]:
    placeholders = ",".join("?" for _ in product_ids)
    rows = connection.execute(
        f"""
        SELECT product_id, price, currency, observed_at, recorded_at, origin, query
        FROM price_observations
        WHERE product_id IN ({placeholders})
        ORDER BY observed_at, id
        """,
        product_ids,
    ).fetchall()

    observations: dict[int, list[dict]] = {}

    for row in rows:
        observation = dict(row)
        product_id = observation.pop("product_id")
        observations.setdefault(product_id, []).append(observation)

    return observations


def _product_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "source": row["source"],
        "url": row["url"],
        "image_url": row["image_url"],
        "rating": row["rating"],
        "first_seen_at": row["first_seen_at"],
        "last_seen_at": row["last_seen_at"],
    }
