import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import App from "./App";
import { jsonResponse, productResult, requestsTo, searchResponse, stubApi, type Route } from "./test/fakeApi";
import type { Freshness, PriceHistorySummary, ProductResult } from "./types";

const query = "robotstøvsuger med moppe og høj sugeevne";

const demoSource: Freshness = {
  origin: "demo",
  origin_label: "Demodata (fiktive priser)",
  fetched_at: "2026-10-31T09:30:00Z",
  age_hours: 26.4,
  status: "aging",
  status_label: "Ældre",
};

function summary(overrides: Partial<PriceHistorySummary> = {}): PriceHistorySummary {
  return {
    observation_count: 4,
    latest_price: 4499,
    latest_observed_at: "2026-10-31T09:30:00Z",
    first_observed_at: "2026-10-10T09:15:00Z",
    lowest_price: 4499,
    highest_price: 4999,
    previous_price: 4799,
    price_change: -300,
    is_lowest_seen: true,
    freshness: demoSource,
    ...overrides,
  };
}

function withHistory(name: string, score: number, productId: number, history = summary()): ProductResult {
  return productResult(name, score, { product_id: productId, price_history: history });
}

const results = [
  withHistory("Nordvac R5", 90, 1),
  withHistory("AquaClean", 80, 2, summary({ latest_price: 3299, is_lowest_seen: false, price_change: 0 })),
  withHistory("Støvfri S1", 70, 3),
  withHistory("BudgetBot", 60, 4),
  withHistory("Nordvac R3", 50, 5),
];

function apiWith(extraRoutes: Route[] = []) {
  return stubApi({
    routes: [
      (method, path) =>
        method === "POST" && path === "/api/search"
          ? jsonResponse({ ...searchResponse(query, results), data_source: demoSource })
          : undefined,
      ...extraRoutes,
    ],
  });
}

async function searchFor(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByPlaceholderText("Søg efter produkter..."), `${query}{Enter}`);
  await screen.findByText("Nordvac R5");
}

function card(name: string) {
  return screen.getByRole("heading", { name }).closest(".product-card") as HTMLElement;
}

describe("price history and comparison", () => {
  it("labels demo data and shows when each price was fetched", async () => {
    apiWith();
    const user = userEvent.setup();
    render(<App />);

    await searchFor(user);

    const notice = screen.getByRole("status");
    expect(notice).toHaveTextContent("Demodata (fiktive priser)");
    expect(notice).toHaveTextContent("26 timer gammel");
    expect(notice).toHaveTextContent("Ældre");
    expect(notice).toHaveTextContent("ikke rigtige tilbud");

    const nordvac = within(card("Nordvac R5"));
    expect(nordvac.getByText(/Pris hentet/)).toBeInTheDocument();
    expect(nordvac.getByText(/↓ 300 kr\. siden forrige pris/)).toBeInTheDocument();
    expect(nordvac.getByText(/4 målinger/)).toBeInTheDocument();
    expect(nordvac.getByText("Laveste pris set")).toBeInTheDocument();
  });

  it("loads and shows the price history of a product on request", async () => {
    const { fetchMock } = apiWith([
      (method, path) =>
        method === "GET" && path === "/api/products/1/price-history"
          ? jsonResponse({
              product: { id: 1, name: "Nordvac R5", source: "Demo", url: "", image_url: null, rating: 4.6, first_seen_at: "", last_seen_at: "" },
              summary: summary(),
              observations: [
                { price: 4999, currency: "DKK", observed_at: "2026-10-10T09:15:00Z", recorded_at: "", origin: "demo", query },
                { price: 4499, currency: "DKK", observed_at: "2026-10-31T09:30:00Z", recorded_at: "", origin: "demo", query },
              ],
            })
          : undefined,
    ]);
    const user = userEvent.setup();
    render(<App />);
    await searchFor(user);

    expect(requestsTo(fetchMock, "GET", "/api/products/1/price-history")).toHaveLength(0);
    await user.click(within(card("Nordvac R5")).getByRole("button", { name: "Vis prishistorik" }));

    const table = await screen.findByRole("table");
    const rows = within(table).getAllByRole("row");
    expect(rows).toHaveLength(3);
    // Newest first.
    expect(rows[1]).toHaveTextContent("4.499 kr.");
    expect(rows[2]).toHaveTextContent("4.999 kr.");
    expect(screen.getByRole("img", { name: "Pris fra 4.999 kr. til 4.499 kr." })).toBeInTheDocument();
  });

  it("compares two to four selected products", async () => {
    const { fetchMock } = apiWith([
      (method, path) =>
        method === "GET" && path === "/api/products/compare"
          ? jsonResponse({
              count: 2,
              price_spread: 1200,
              items: [
                { product: { id: 1, name: "Nordvac R5", source: "Demo Elektronik", url: "", image_url: null, rating: 4.6, first_seen_at: "", last_seen_at: "" }, summary: summary(), highlights: ["lowest_price_seen"] },
                { product: { id: 2, name: "AquaClean", source: "Demo Hvidevarer", url: "", image_url: null, rating: 4.3, first_seen_at: "", last_seen_at: "" }, summary: summary({ latest_price: 3299 }), highlights: ["cheapest_now"] },
              ],
            })
          : undefined,
    ]);
    const user = userEvent.setup();
    render(<App />);
    await searchFor(user);

    await user.click(within(card("Nordvac R5")).getByRole("checkbox", { name: "Sammenlign" }));
    expect(screen.getByRole("button", { name: "Sammenlign valgte" })).toBeDisabled();

    await user.click(within(card("AquaClean")).getByRole("checkbox", { name: "Sammenlign" }));
    // A new selection starts a fresh comparison panel, so the button is looked up again.
    await user.click(screen.getByRole("button", { name: "Sammenlign valgte" }));

    const panel = await screen.findByRole("region", { name: "Sammenligning" });
    expect(await within(panel).findByText("Billigst nu")).toBeInTheDocument();
    expect(within(panel).getByText("Forskel mellem dyreste og billigste: 1.200 kr.")).toBeInTheDocument();

    const [request] = requestsTo(fetchMock, "GET", "/api/products/compare");
    expect(new URL(request[0].toString()).searchParams.getAll("ids")).toEqual(["1", "2"]);
  });

  it("allows at most four products to be selected", async () => {
    apiWith();
    const user = userEvent.setup();
    render(<App />);
    await searchFor(user);

    for (const name of ["Nordvac R5", "AquaClean", "Støvfri S1", "BudgetBot"]) {
      await user.click(within(card(name)).getByRole("checkbox", { name: "Sammenlign" }));
    }

    expect(within(card("Nordvac R3")).getByRole("checkbox", { name: "Sammenlign" })).toBeDisabled();
    expect(screen.getByText("4 valgt til sammenligning (2-4)")).toBeInTheDocument();
  });
});
