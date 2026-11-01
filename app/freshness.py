from datetime import datetime, timedelta, timezone

# How old product data may be before it is no longer called fresh. Shop prices change often,
# so anything older than a day is shown as aging and anything older than a week as stale.
FRESH_FOR = timedelta(hours=24)
STALE_AFTER = timedelta(days=7)

ORIGIN_LABELS = {
    "live": "Live fra SerpAPI",
    "cache": "Fra cache",
    "demo": "Demodata (fiktive priser)",
}

STATUS_LABELS = {
    "fresh": "Frisk",
    "aging": "Ældre",
    "stale": "Forældet",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def describe_freshness(fetched_at: datetime, origin: str, now: datetime | None = None) -> dict:
    """Says where product data came from, when it was fetched from the source and how old it is."""
    now = now or utc_now()
    age = max(now - fetched_at, timedelta(0))

    if age < FRESH_FOR:
        status = "fresh"
    elif age < STALE_AFTER:
        status = "aging"
    else:
        status = "stale"

    return {
        "origin": origin,
        "origin_label": ORIGIN_LABELS.get(origin, origin),
        "fetched_at": to_iso(fetched_at),
        "age_hours": round(age.total_seconds() / 3600, 1),
        "status": status,
        "status_label": STATUS_LABELS[status],
    }


def to_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
