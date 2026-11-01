# AI Deal Agent — project walkthrough

A developer-level guide to the system and, in depth, to the price history, comparison and freshness feature. It describes only what exists in the repository.

## 1. System overview

```text
React + TypeScript (Vite, :5173)
        │ fetch JSON
        ▼
FastAPI (app/api.py, :8000)
        ├─ requirements_parser  free text → product type, max price, features
        ├─ product_search       cache first; SerpAPI only when explicitly allowed
        │    └─ cache_service   one JSON file per normalised query (cache/)
        ├─ scorer, badge_generator, explainer
        ├─ price_history        SQLite: products + price_observations (data/)
        ├─ comparison           side-by-side highlights
        └─ saved_searches       JSON file (data/)
```

**Quota protection (unchanged):** a search uses the cache whenever it exists. A live SerpAPI call needs both the request flag `allow_live_search` and `ALLOW_LIVE_SEARCH=true` in the environment, plus an API key. Tests and CI block all network access and force live search off.

## 2. Price history, freshness and comparison

### Problem

A single price says little. Users want to know whether a price is low compared with earlier, how old the information is, and where it came from. An honest answer is required: cached data must not look current, and demonstration data must not look real.

### The key decision: date data by its fetch time

`product_search.search_products` now returns `fetched_at` and `origin`:

| Situation | `origin` | `fetched_at` |
| --- | --- | --- |
| Live SerpAPI call | `live` | `search_metadata.created_at` of the response (or now) |
| Cache hit | `cache` | `search_metadata.created_at` stored in the cached response, else the cache file's modification time |
| Cache hit on a file with `"ai_deal_agent_demo": true` | `demo` | the snapshot's `created_at` |

`price_history.record_observations` stores each priced product with `observed_at = fetched_at`. The table has `UNIQUE (product_id, observed_at, price)` and the insert is `INSERT OR IGNORE`. Reading the same cached response a hundred times therefore stores one observation. The alternative, dating by request time, would turn every cache read into a new "price point" and fake a flat history. A test patches the clock to different days and asserts a single observation; replacing the fetch time with the current time makes five tests fail.

### Schema (`app/price_history.py`)

```text
products(id, product_key UNIQUE, name, source, url, image_url, rating, first_seen_at, last_seen_at)
price_observations(id, product_id → products ON DELETE CASCADE, price CHECK (price > 0), currency,
                   observed_at, recorded_at, origin CHECK IN ('live','cache','demo'), query,
                   UNIQUE (product_id, observed_at, price))
```

- `product_key` is `id:<SerpAPI product_id>` when available, else `name:<normalised name>|<normalised shop>`.
- Product details (name, URL, rating) are only replaced by data with a newer `last_seen_at`, so loading an older snapshot later does not roll them back.
- Schema versioning uses `PRAGMA user_version`; version 1 creates the tables.
- Timestamps are ISO 8601 UTC strings with second precision (`2026-10-31T09:30:00Z`), which sort correctly as text.

### Freshness (`app/freshness.py`)

`describe_freshness(fetched_at, origin, now)` returns the origin with a Danish label, the fetch time, the age in hours, and a status: `fresh` under 24 hours, `aging` under 7 days, `stale` after. The thresholds are constants with a comment explaining them. `now` is a parameter so tests are deterministic.

### Summary and comparison

`summarize(observations)` gives the latest, lowest and highest price, the *previous different* price (so repeated equal prices do not hide a change), the change, the observation count, and `is_lowest_seen` (only when the price has actually varied).

`comparison.build_comparison` is a pure function over 2-4 stored histories. It marks `cheapest_now` among priced products, `best_rated` only when at least two products are rated (one rating alone says nothing), and `lowest_price_seen`. Ties mark every product sharing the best value.

### Request flow — search

```text
POST /api/search
  parse_requirements → search_products (cache/live/demo, fetched_at, origin)
  _record_price_history → record_observations + get_summaries   (sqlite3.Error → logged, history = null)
  score, badges, explanations per product
  ← { …existing fields…, data_source, products[i].product_id, products[i].price_history }
```

The new fields are additions; existing clients keep working.

### Endpoints

| Endpoint | Result |
| --- | --- |
| `GET /api/products/{id}/price-history` | product, observations (oldest first), summary; `404` if unknown |
| `GET /api/products/compare?ids=…` | 2-4 different ids; `400` for other counts, `404` naming unknown ids |

### Demo data (`demo/snapshots`, `app/demo_seed.py`)

Eight fictional snapshots (two queries × four weekly dates) in SerpAPI's shape. `load_snapshots` refuses any file without the demo marker and a date, so real responses cannot be loaded as demo data by mistake. `seed_demo_data` records all snapshots as `demo` observations and writes the newest snapshot of each query to the cache only when no cache file exists. A test proves an existing cache file is kept byte for byte.

### Frontend

- `DataSourceNotice` shows origin, fetch time in local time, age, freshness badge, and for demo data a sentence saying the prices are invented.
- `ProductCard` shows "Pris hentet …", the change since the previous price, the lowest/highest of N observations, a "Laveste pris set" badge, a "Vis prishistorik" toggle (loads `PriceHistoryPanel`: SVG line plus a newest-first table) and a "Sammenlign" checkbox.
- `ComparisonPanel` appears when products are selected; at most four can be selected; it is keyed by the selection so a new selection starts empty.

## 3. Testing

| Suite | Count | New coverage |
| --- | --- | --- |
| pytest (`tests/`) | 101 (34 new) | price history, freshness thresholds, comparison, demo seeding, API fields and endpoints, live/cache/demo origin, database failure |
| Vitest (`frontend/src`) | 16 (4 new) | demo label and fetch times, loading history, comparing, the four-product limit |

All backend tests are offline (network blocked in `conftest.py`) and use a temporary database, cache and data folder. Live search is tested with a mocked SerpAPI response. The frontend tests stub `fetch`.

## 4. Local demonstration (1 November 2026)

Windows 11, Python 3.12 venv, uvicorn on `127.0.0.1:8000`, Vite on `localhost:5173`, Microsoft Edge via Playwright, no `.env` and no API key:

1. `python -m app.demo_seed` loaded 8 snapshots, 35 observations and 9 products; a second run added nothing and kept the cache files.
2. Searching an uncached query was refused with the existing quota message; requesting live search was refused because it is disabled.
3. The robot vacuum query showed "Demodata (fiktive priser) · hentet 31. okt. 2026 10.30 · Frisk"; Nordvac R5 showed "↓ 300 kr. siden forrige pris … 4 målinger" and its four-row history.
4. Comparing three products marked AquaClean "Billigst nu", Støvfri S1 "Bedst bedømt", and gave a spread of 3,500 kr.
5. After all searches the database still held 35 observations; no browser console errors apart from the deliberate refused search; no horizontal page overflow at 390 px (the comparison table scrolls inside its panel).

## 5. Limitations

- History grows only when new data arrives; there is no scheduled polling (it would spend SerpAPI quota).
- The demo history is fictional.
- Product identity falls back to name + shop, so a shop renaming a product starts a new history.
- Single-user local storage; no authentication.

## 6. Ownership and AI assistance

Implemented with AI assistance (Claude Code). The owner defined the requirements (database-backed history, comparison, timestamps, freshness, cached demo, no paid calls) and reviews and merges. Design decisions are documented above so they can be explained and challenged.

## 7. Interview preparation — price history

**Non-technical:** The app remembers prices it has seen, shows how old each price is and where it came from, and lets you put up to four products side by side. Example prices are clearly marked as made up.

**Developer:** Observations are dated by fetch time and deduplicated by a unique constraint; the search response gains a `data_source` block and per-product summaries; two read endpoints serve history and comparison.

**Senior:** The design protects data integrity (no invented history), honesty (origin and age are part of the contract), cost (no new API calls, demo works offline) and resilience (history failure does not break search). SQLite keeps it portable and free; the schema is versioned for later migration to PostgreSQL.

**Questions and answers**

1. *Why not record a price every time someone searches?* Most searches are cache hits; recording them would create fake data points with the same price. Dating by fetch time plus a unique constraint makes the history reflect the source, not the traffic.
2. *Why SQLite instead of the existing JSON files?* History needs queries across products, constraints and safe concurrent writes. SQLite gives that with no server and no new dependency.
3. *How is demo data kept from looking real?* A marker in each snapshot sets `origin = demo`, the UI labels it, links use `example.com`, and the loader refuses files without the marker.
4. *What happens if the database is locked or the disk is full?* The search catches `sqlite3.Error`, logs it and returns results without history fields.
5. *How would you show history for products that are rarely searched?* A scheduled job with an explicit quota budget, or a cheaper price source. Both are cost decisions, so they are not done automatically.

**Hands-on exercise:** Add `GET /api/products/{id}/price-history?days=30` that limits observations to a period, validate `days` (1-365), cover it with tests, and add a period selector to `PriceHistoryPanel`.
