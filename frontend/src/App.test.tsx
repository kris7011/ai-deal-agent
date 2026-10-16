import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import App from "./App";
import { jsonResponse, productResult, requestsTo, savedSearch, searchResponse, stubApi } from "./test/fakeApi";

const query = "robotstøvsuger med moppe under 5000 kr";

function searchRoute(response: Response | (() => Response)) {
  return (method: string, path: string) => {
    if (method === "POST" && path === "/api/search") {
      return typeof response === "function" ? response() : response;
    }
  };
}

async function search(user: ReturnType<typeof userEvent.setup>, text: string) {
  await user.type(screen.getByPlaceholderText("Søg efter produkter..."), `${text}{Enter}`);
}

describe("App", () => {
  it("searches and shows the parsed requirements, cache source and ranked products", async () => {
    const { fetchMock } = stubApi({
      routes: [
        searchRoute(() =>
          jsonResponse(searchResponse(query, [productResult("Roborock S8", 92), productResult("Basic robot", 45)])),
        ),
      ],
    });
    const user = userEvent.setup();

    render(<App />);
    await search(user, query);

    expect(await screen.findByText("Roborock S8")).toBeInTheDocument();
    expect(screen.getByText("Basic robot")).toBeInTheDocument();
    expect(screen.getByText("Produkt: robotstøvsuger")).toBeInTheDocument();
    expect(screen.getByText("Resultater hentet fra cache. Ingen SerpAPI-søgning brugt.")).toBeInTheDocument();
    expect(screen.getByText("Score: 92/100")).toBeInTheDocument();

    const [, init] = requestsTo(fetchMock, "POST", "/api/search")[0];
    expect(JSON.parse(init?.body as string)).toEqual({ query, allow_live_search: false });
  });

  it("only requests a live search when the user ticks the checkbox", async () => {
    const { fetchMock } = stubApi({
      routes: [searchRoute(() => jsonResponse(searchResponse(query, [productResult("Roborock S8", 92)], false)))],
    });
    const user = userEvent.setup();

    render(<App />);
    await user.click(screen.getByLabelText("Tillad live-søgning hvis cache mangler"));
    await search(user, query);

    expect(await screen.findByText("Ny live-søgning udført og gemt i cache.")).toBeInTheDocument();
    const [, init] = requestsTo(fetchMock, "POST", "/api/search")[0];
    expect(JSON.parse(init?.body as string).allow_live_search).toBe(true);
  });

  it("asks for a query instead of calling the API when the search field is empty", async () => {
    const { fetchMock } = stubApi();
    const user = userEvent.setup();

    render(<App />);
    await user.click(screen.getByRole("button", { name: "Søg" }));

    expect(screen.getByText("Skriv hvad du leder efter først.")).toBeInTheDocument();
    expect(requestsTo(fetchMock, "POST", "/api/search")).toHaveLength(0);
  });

  it.each([
    {
      name: "the backend's detail message",
      response: () => jsonResponse({ detail: "Ingen cache fundet for denne søgning. Live-søgning er ikke valgt." }, 400),
      expected: "Ingen cache fundet for denne søgning. Live-søgning er ikke valgt.",
    },
    {
      name: "FastAPI validation messages",
      response: () => jsonResponse({ detail: [{ loc: ["body", "query"], msg: "Field required" }] }, 422),
      expected: "Field required",
    },
    {
      name: "a fallback for non-JSON errors",
      response: () => new Response("Internal Server Error", { status: 500 }),
      expected: "Søgningen fejlede.",
    },
  ])("shows $name when the search fails", async ({ response, expected }) => {
    stubApi({ routes: [searchRoute(response)] });
    const user = userEvent.setup();

    render(<App />);
    await search(user, query);

    expect(await screen.findByText(expected)).toBeInTheDocument();
  });

  it("explains that the backend is unreachable when fetch fails", async () => {
    stubApi({
      routes: [
        (method, path) => {
          if (method === "POST" && path === "/api/search") {
            return Promise.reject(new TypeError("Failed to fetch"));
          }
        },
      ],
    });
    const user = userEvent.setup();

    render(<App />);
    await search(user, query);

    expect(
      await screen.findByText("Kunne ikke kontakte serveren. Kontroller at backend kører."),
    ).toBeInTheDocument();
  });

  it("saves the current search once and shows it in the saved searches panel", async () => {
    const { fetchMock } = stubApi({
      routes: [searchRoute(() => jsonResponse(searchResponse(query, [productResult("Roborock S8", 92)])))],
    });
    const user = userEvent.setup();

    render(<App />);
    await search(user, query);
    await user.click(await screen.findByRole("button", { name: "Gem søgning" }));

    expect(await screen.findByText("Søgningen er gemt.")).toBeInTheDocument();
    const panel = screen.getByRole("heading", { name: "Gemte søgninger" }).parentElement as HTMLElement;
    expect(within(panel).getByRole("heading", { name: query })).toBeInTheDocument();
    expect(JSON.parse(requestsTo(fetchMock, "POST", "/api/saved-searches")[0][1]?.body as string)).toEqual({
      query,
      result_count: 1,
      best_score: 92,
    });

    await user.click(screen.getByRole("button", { name: "Gem søgning" }));

    expect(await screen.findByText("Søgningen er allerede gemt.")).toBeInTheDocument();
    expect(requestsTo(fetchMock, "POST", "/api/saved-searches")).toHaveLength(1);
  });

  it("lists saved searches newest first, runs them again and deletes them", async () => {
    const { fetchMock } = stubApi({
      savedSearches: [
        savedSearch("old", "laptop til programmering", "2026-10-01T10:00:00Z"),
        savedSearch("new", "vinterjakke til herre", "2026-10-15T10:00:00Z"),
      ],
      routes: [
        searchRoute(() => jsonResponse(searchResponse("vinterjakke til herre", [productResult("Jakke", 70)]))),
      ],
    });
    const user = userEvent.setup();

    render(<App />);

    const headings = await screen.findAllByRole("heading", { level: 3 });
    expect(headings.map((heading) => heading.textContent)).toEqual([
      "vinterjakke til herre",
      "laptop til programmering",
    ]);

    await user.click(screen.getAllByRole("button", { name: "Søg igen" })[0]);
    expect(await screen.findByText("Jakke")).toBeInTheDocument();
    expect(JSON.parse(requestsTo(fetchMock, "POST", "/api/search")[0][1]?.body as string).query).toBe(
      "vinterjakke til herre",
    );

    await user.click(screen.getAllByRole("button", { name: "Slet" })[1]);
    await waitFor(() =>
      expect(screen.queryByRole("heading", { name: "laptop til programmering" })).not.toBeInTheDocument(),
    );
    expect(requestsTo(fetchMock, "DELETE", "/api/saved-searches/old")).toHaveLength(1);
  });
});
