export type Product = {
    name: string;
    price: number;
    image_url: string | null;
    source: string;
    url: string;
};

export type ProductResult = {
    product: Product;
    score: number;
    badges: string[];
    explanations: string[];
};

export type SearchRequirements = {
    product_type: string;
    max_price: number | null;
    required_features: string[];
};

export type SavedSearch = {
    query: string;
    product_type: string;
    max_price: number | null;
    required_features: string[];
    result_count: number;
    best_score: number;
    created_at: string;
};