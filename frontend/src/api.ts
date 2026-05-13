import type { ProductResult, SavedSearch, SearchRequirements } from "./types";

export type SearchResponse = {
    query: string;
    count: number;
    used_cache: boolean;
    requirements: SearchRequirements;
    products: ProductResult[];
};

export type SaveSearchResponse = {
    saved_search: {
        query: string;
        product_type: string;
        max_price: number | null;
        required_features: string[];
        result_count: number;
        best_score: number;
        created_at: string;
    };
};

export type GetSavedSearchesResponse = {
    count: number;
    saved_searches: SavedSearch[];
};

export async function searchProductsApi(
    query: string,
    allowLiveSearch: boolean
): Promise<SearchResponse> {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

    const response = await fetch(`${apiBaseUrl}/api/search`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            query,
            allow_live_search: allowLiveSearch,
        }),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail ?? "Søgningen fejlede.");
    }

    return data;
}

export async function saveSearchApi(
    query: string,
    resultCount: number,
    bestScore: number
): Promise<SaveSearchResponse> {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

    const response = await fetch(`${apiBaseUrl}/api/saved-searches`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            query,
            result_count: resultCount,
            best_score: bestScore,
        }),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail ?? "Kunne ikke gemme søgningen.");
    }

    return data;
}

export async function getSavedSearchesApi(): Promise<GetSavedSearchesResponse> {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

    const response = await fetch(`${apiBaseUrl}/api/saved-searches`);

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail ?? "Kunne ikke hente gemte søgninger.");
    }

    return data;
}

export async function deleteSavedSearchApi(savedSearchId: string): Promise<void> {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

    const response = await fetch(`${apiBaseUrl}/api/saved-searches/${savedSearchId}`, {
        method: "DELETE",
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail ?? "Kunne ikke slette søgningen.");
    }
}