import type { ProductResult, SearchRequirements } from "./types";

export type SearchResponse = {
    query: string;
    count: number;
    used_cache: boolean;
    requirements: SearchRequirements;
    products: ProductResult[];
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