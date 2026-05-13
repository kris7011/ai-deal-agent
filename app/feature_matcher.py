from app.models import Product

FEATURE_SYNONYMS = {
    "trådløs": [
        "trådløs",
        "wireless",
        "cordless",
    ],
    "vandtæt": [
        "vandtæt",
        "waterproof",
        "water resistant",
        "water-resistant",
    ],
    "støjsvag": [
        "støjsvag",
        "quiet",
        "silent",
        "low noise",
    ],
    "usb-c": [
        "usb-c",
        "usb c",
        "usbc",
        "type-c",
        "type c",
    ],
    "høj sugeevne": [
        "høj sugeevne",
        "high suction",
        "strong suction",
        "suction",
        "pa",
    ],
}


def product_matches_feature(product: Product, feature: str) -> bool:
    searchable_text = _normalize_text(f"{product.name} {product.source}")

    feature_candidates = _get_feature_candidates(feature)

    for candidate in feature_candidates:
        normalized_candidate = _normalize_text(candidate)

        if normalized_candidate in searchable_text:
            return True

        candidate_words = [
            word for word in normalized_candidate.split() if len(word) > 2
        ]

        if any(word in searchable_text for word in candidate_words):
            return True

    return False


def _get_feature_candidates(feature: str) -> list[str]:
    normalized_feature = feature.lower().strip()

    synonyms = FEATURE_SYNONYMS.get(normalized_feature, [])

    return [
        normalized_feature,
        *synonyms,
    ]


def _normalize_text(text: str) -> str:
    return text.lower().replace("-", " ").replace("_", " ").strip()
