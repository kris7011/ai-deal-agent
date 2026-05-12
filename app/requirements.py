from dataclasses import dataclass


@dataclass
class SearchRequirements:
    product_type: str
    max_price: int | None
    required_features: list[str]
    raw_query: str
