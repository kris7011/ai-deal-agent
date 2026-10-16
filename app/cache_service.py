import hashlib
import json
import re
from pathlib import Path

from app.settings import PROJECT_ROOT

CACHE_DIR = PROJECT_ROOT / "cache"

# Letters (including æ, ø and å), digits, underscore and a few harmless punctuation characters.
# Everything else, including path separators and characters that are invalid in Windows
# file names (such as ? : * " < > |), is replaced with an underscore.
_UNSAFE_FILENAME_CHARACTER = re.compile(r"[^\w.,+-]")

_MAX_FILENAME_LENGTH = 120


def get_cache_path(query: str) -> Path:
    # Lowercase with spaces as underscores, as before, so existing cache files are still found.
    safe_name = _UNSAFE_FILENAME_CHARACTER.sub("_", query.lower().replace(" ", "_"))

    if len(safe_name) > _MAX_FILENAME_LENGTH:
        query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()[:12]
        safe_name = f"{safe_name[:_MAX_FILENAME_LENGTH - 13]}_{query_hash}"

    return CACHE_DIR / f"{safe_name}.json"


def load_cache(query: str) -> dict | None:
    cache_path = get_cache_path(query)

    if not cache_path.exists():
        return None

    with open(cache_path, encoding="utf-8") as file:
        return json.load(file)


def save_cache(query: str, data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_path = get_cache_path(query)

    with open(cache_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
