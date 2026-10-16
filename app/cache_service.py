import hashlib
import json
import logging
import re
from pathlib import Path

from app.settings import PROJECT_ROOT

logger = logging.getLogger(__name__)

CACHE_DIR = PROJECT_ROOT / "cache"

# Characters kept in the human-readable part of a cache file name: letters (including æ, ø
# and å), digits, underscore and hyphen. The readable part is only a label; uniqueness comes
# from the hash of the normalized query.
_SLUG_UNSAFE_CHARACTERS = re.compile(r"[^\w-]+")

_MAX_SLUG_LENGTH = 60

_KEY_HASH_LENGTH = 16

# File names written before cache keys contained a hash: lowercased, spaces and "/" replaced
# with underscores. Only names consisting of these characters are considered for fallback.
_SAFE_LEGACY_NAME = re.compile(r"^[\w.,+-]+$")


def normalize_query(query: str) -> str:
    """Case- and whitespace-insensitive form of a query, used to derive the cache key."""
    return " ".join(query.lower().split())


def get_cache_key(query: str) -> str:
    """Stable, deterministic cache key: a readable slug plus a SHA-256 prefix of the normalized query.

    Different queries such as "laptop/16GB" and "laptop?16GB" get different keys because the hash
    is computed from the full normalized text, not from the sanitized file name.
    """
    normalized = normalize_query(query)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:_KEY_HASH_LENGTH]
    slug = _SLUG_UNSAFE_CHARACTERS.sub("_", normalized).strip("_")[:_MAX_SLUG_LENGTH].rstrip("_")

    return f"{slug}-{digest}" if slug else digest


def get_cache_path(query: str) -> Path:
    return CACHE_DIR / f"{get_cache_key(query)}.json"


def load_cache(query: str) -> dict | None:
    cache_path = get_cache_path(query)

    if cache_path.exists():
        return _read_json(cache_path)

    return _load_legacy_cache(query)


def save_cache(query: str, data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_path = get_cache_path(query)

    with open(cache_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def _read_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def _get_legacy_cache_path(query: str) -> Path | None:
    legacy_name = query.lower().replace(" ", "_").replace("/", "_")

    if not _SAFE_LEGACY_NAME.match(legacy_name) or legacy_name.startswith("."):
        return None

    return CACHE_DIR / f"{legacy_name}.json"


def _load_legacy_cache(query: str) -> dict | None:
    """Reads a cache file written with the old naming scheme, but only when it provably belongs to the query.

    The old scheme mapped different queries ("a b", "a_b", "a/b") to the same file, so the file name
    alone is not trusted. SerpAPI responses record the original query in search_parameters.q; the
    file is used only when that query normalizes to the same text. It is then saved under the new key.
    """
    legacy_path = _get_legacy_cache_path(query)

    if legacy_path is None or not legacy_path.exists():
        return None

    try:
        data = _read_json(legacy_path)
    except (OSError, ValueError):
        logger.warning("Ignoring unreadable legacy cache file %s", legacy_path.name)
        return None

    search_parameters = data.get("search_parameters") if isinstance(data, dict) else None
    cached_query = search_parameters.get("q") if isinstance(search_parameters, dict) else None

    if not isinstance(cached_query, str) or normalize_query(cached_query) != normalize_query(query):
        logger.info("Ignoring legacy cache file %s because it belongs to another query", legacy_path.name)
        return None

    save_cache(query, data)

    return data
