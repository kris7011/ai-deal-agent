import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"

# Load .env from the project root once at startup. Variables that are already set in the
# environment take precedence, so CI and tests can control configuration without a local
# .env overriding them (for example re-enabling paid live searches).
load_dotenv(PROJECT_ROOT / ".env")


def get_cors_origins() -> list[str]:
    origins = os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)

    return [origin.strip() for origin in origins.split(",") if origin.strip()]


def is_live_search_enabled() -> bool:
    return os.getenv("ALLOW_LIVE_SEARCH", "false").strip().lower() == "true"


def get_serpapi_api_key() -> str | None:
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()

    return api_key or None
