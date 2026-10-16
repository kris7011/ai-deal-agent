import { vi } from "vitest";
import type { ProductResult, SavedSearch } from "../types";

export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export function productResult(name: string, score: number, overrides: Partial<ProductResult> = {}): ProductResult {
  return {
    product: {
      name,
      price: 4799,
      image_url: `https://example.com/${encodeURIComponent(name)}.jpg`,
      source: "Test Shop",
      url: "https://www.google.com/shopping/product/123",
    },
    score,
    badges: score >= 70 ? ["Stærkt match"] : ["Muligt match"],
    explanations: ["✓ Matcher krav: moppe"],
    ...overrides,
  };
}

export function searchResponse(query: string, products: ProductResult[], usedCache = true) {
  return {
    query,
    count: products.length,
    used_cache: usedCache,
    requirements: {
      product_type: "robotstøvsuger",
      max_price: 5000,
      required_features: ["moppe"],
    },
    products,
  };
}

export function savedSearch(id: string, query: string, createdAt: string): SavedSearch {
  return {
    id,
    query,
    product_type: query.split(" ")[0],
    max_price: null,
    required_features: [],
    result_count: 10,
    best_score: 80,
    created_at: createdAt,
  };
}

type Route = (method: string, path: string, body: unknown) => Response | Promise<Response> | undefined;

/**
 * Stubs global fetch with an in-memory version of the AI Deal Agent API.
 * Saved searches are kept in `state` and can be inspected or changed by tests.
 */
export function stubApi(options: { savedSearches?: SavedSearch[]; routes?: Route[] } = {}) {
  const state = { savedSearches: options.savedSearches ?? [] };

  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(input.toString());
    const method = init?.method ?? "GET";
    const body = init?.body ? JSON.parse(init.body.toString()) : undefined;

    for (const route of options.routes ?? []) {
      const response = route(method, url.pathname, body);
      if (response) {
        return response;
      }
    }

    if (method === "GET" && url.pathname === "/api/saved-searches") {
      return jsonResponse({ count: state.savedSearches.length, saved_searches: state.savedSearches });
    }

    if (method === "POST" && url.pathname === "/api/saved-searches") {
      const created = savedSearch(`saved-${state.savedSearches.length + 1}`, body.query, "2026-10-16T12:00:00Z");
      state.savedSearches = [...state.savedSearches, created];
      return jsonResponse({ saved_search: created });
    }

    if (method === "DELETE" && url.pathname.startsWith("/api/saved-searches/")) {
      const id = decodeURIComponent(url.pathname.split("/").pop() ?? "");
      state.savedSearches = state.savedSearches.filter((item) => item.id !== id);
      return jsonResponse({ deleted: true, id });
    }

    return jsonResponse({ detail: `No fake route for ${method} ${url.pathname}` }, 404);
  });

  vi.stubGlobal("fetch", fetchMock);

  return { fetchMock, state };
}

export function requestsTo(fetchMock: ReturnType<typeof stubApi>["fetchMock"], method: string, path: string) {
  return fetchMock.mock.calls.filter(([input, init]) => {
    return (init?.method ?? "GET") === method && new URL(input.toString()).pathname === path;
  });
}
