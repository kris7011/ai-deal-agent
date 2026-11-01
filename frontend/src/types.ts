export type Product = {
    name: string;
    price: number;
    image_url: string | null;
    source: string;
    url: string;
};

export type DataOrigin = "live" | "cache" | "demo";

export type FreshnessStatus = "fresh" | "aging" | "stale";

/** Where product data came from and how old it is (when it was fetched from the source). */
export type Freshness = {
    origin: DataOrigin;
    origin_label: string;
    fetched_at: string;
    age_hours: number;
    status: FreshnessStatus;
    status_label: string;
};

export type PriceHistorySummary = {
    observation_count: number;
    latest_price: number | null;
    latest_observed_at: string | null;
    first_observed_at: string | null;
    lowest_price: number | null;
    highest_price: number | null;
    previous_price: number | null;
    price_change: number | null;
    is_lowest_seen: boolean;
    freshness: Freshness | null;
};

export type ProductResult = {
    product: Product;
    /** Id in the price history; null when the history could not be stored. Optional for older API versions. */
    product_id?: number | null;
    price_history?: PriceHistorySummary | null;
    score: number;
    badges: string[];
    explanations: string[];
};

export type StoredProduct = {
    id: number;
    name: string;
    source: string;
    url: string;
    image_url: string | null;
    rating: number | null;
    first_seen_at: string;
    last_seen_at: string;
};

export type PriceObservation = {
    price: number;
    currency: string;
    observed_at: string;
    recorded_at: string;
    origin: DataOrigin;
    query: string;
};

export type PriceHistory = {
    product: StoredProduct;
    observations: PriceObservation[];
    summary: PriceHistorySummary;
};

export type ComparisonHighlight = "cheapest_now" | "best_rated" | "lowest_price_seen";

export type Comparison = {
    count: number;
    price_spread: number | null;
    items: {
        product: StoredProduct;
        summary: PriceHistorySummary;
        highlights: ComparisonHighlight[];
    }[];
};

export type SearchRequirements = {
    product_type: string;
    max_price: number | null;
    required_features: string[];
};

export type SavedSearch = {
    id: string;
    query: string;
    product_type: string;
    max_price: number | null;
    required_features: string[];
    result_count: number;
    best_score: number;
    created_at: string;
};