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

// Falls back to the default local backend when VITE_API_BASE_URL is not set.
const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function readErrorMessage(response: Response, fallbackMessage: string): Promise<string> {
    try {
        const data: unknown = await response.json();

        if (data && typeof data === "object" && "detail" in data) {
            const { detail } = data;

            // HTTPException errors return a string detail.
            if (typeof detail === "string") {
                return detail;
            }

            // FastAPI validation errors (422) return a list of { msg } objects.
            if (Array.isArray(detail) && detail.length > 0 && typeof detail[0]?.msg === "string") {
                return detail.map((item: { msg: string }) => item.msg).join(" ");
            }
        }
    } catch {
        // Not a JSON body (for example a plain-text 500 or a proxy error page).
    }

    return fallbackMessage;
}

async function requestJson<T>(
    path: string,
    fallbackErrorMessage: string,
    init?: RequestInit,
): Promise<T> {
    let response: Response;

    try {
        response = await fetch(`${API_BASE_URL}${path}`, init);
    } catch {
        throw new Error("Kunne ikke kontakte serveren. Kontroller at backend kører.");
    }

    if (!response.ok) {
        throw new Error(await readErrorMessage(response, fallbackErrorMessage));
    }

    return response.json() as Promise<T>;
}

export function searchProductsApi(
    query: string,
    allowLiveSearch: boolean
): Promise<SearchResponse> {
    return requestJson<SearchResponse>("/api/search", "Søgningen fejlede.", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            query,
            allow_live_search: allowLiveSearch,
        }),
    });
}

export function saveSearchApi(
    query: string,
    resultCount: number,
    bestScore: number
): Promise<SaveSearchResponse> {
    return requestJson<SaveSearchResponse>("/api/saved-searches", "Kunne ikke gemme søgningen.", {
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
}

export function getSavedSearchesApi(): Promise<GetSavedSearchesResponse> {
    return requestJson<GetSavedSearchesResponse>(
        "/api/saved-searches",
        "Kunne ikke hente gemte søgninger.",
    );
}

export async function deleteSavedSearchApi(savedSearchId: string): Promise<void> {
    await requestJson<unknown>(
        `/api/saved-searches/${encodeURIComponent(savedSearchId)}`,
        "Kunne ikke slette søgningen.",
        { method: "DELETE" },
    );
}
