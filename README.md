# AI Deal Agent

AI Deal Agent is a full-stack prototype for an AI-assisted product search and deal recommendation tool.

Current version: v1.0

The goal is to let a user describe what they are looking for in natural language, and then return relevant product suggestions with prices, images, match scores, badges, and explanations.

Example search:

```txt
robotstøvsuger med moppe og høj sugeevne
```

The system will try to understand:

```txt
Product type: robotstøvsuger
Required features: moppe, høj sugeevne
Max price: not specified
```

It then searches for products, scores them, and presents the results in a webshop-like interface.

---

## Current Features

- React frontend with product cards
- FastAPI backend
- SerpAPI Google Shopping integration
- Local cache to avoid unnecessary API calls
- Controlled live search to protect API quota
- Configurable frontend API base URL
- Configurable backend CORS origins
- Product scoring
- Product badges
- Recommendation explanations
- Parsed search requirements shown in the UI
- Feature matching with simple Danish/English synonym support
- Saved searches
- Reuse saved searches
- Run saved searches again
- Delete saved searches
- Duplicate protection for saved searches
- Backend tests with pytest

---

## Tech Stack

### Backend

- Python
- FastAPI
- SerpAPI
- python-dotenv
- requests
- pytest

### Frontend

- React
- TypeScript
- Vite
- CSS

---

## Project Structure

```txt
ai-deal-agent/
│
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── badge_generator.py
│   ├── cache_service.py
│   ├── debug_cache.py
│   ├── explainer.py
│   ├── feature_matcher.py
│   ├── models.py
│   ├── product_search.py
│   ├── requirements.py
│   ├── requirements_parser.py
│   ├── saved_searches.py
│   ├── scorer.py
│   └── settings.py
│
├── cache/
│   └── cached SerpAPI responses
│
├── data/
│   └── runtime saved search data
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── EmptyState.tsx
│   │   │   ├── ProductCard.tsx
│   │   │   ├── ProductGrid.tsx
│   │   │   ├── RequirementsSummary.tsx
│   │   │   ├── SavedSearchesPanel.tsx
│   │   │   └── SearchSection.tsx
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── main.tsx
│   │   └── types.ts
│   ├── .env.example
│   └── package.json
│
├── tests/
│   ├── test_feature_matcher.py
│   ├── test_requirements_parser.py
│   ├── test_saved_searches.py
│   └── test_scorer.py
│
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements-dev.txt
├── requirements.txt
└── README.md
```

---

## How It Works

The application follows this flow:

```txt
User search text
        ↓
Requirements parser
        ↓
Product search
        ↓
Cache check
        ↓
SerpAPI call if explicitly allowed
        ↓
Product scoring
        ↓
Badges and explanations
        ↓
Frontend product cards
```

Saved searches follow this flow:

```txt
Completed search
        ↓
Save search
        ↓
Store query, parsed requirements, result count and best score
        ↓
Show saved searches in frontend
        ↓
Reuse, run again or delete saved search
```

---

## Backend Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

For development and tests, install the dev requirements instead (adds pytest and httpx2 for FastAPI's TestClient):

```bash
pip install -r requirements-dev.txt
```

Create a `.env` file in the project root.

Use `.env.example` as a template:

```txt
SERPAPI_API_KEY=your_serpapi_key_here
ALLOW_LIVE_SEARCH=false
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Do not commit `.env` to GitHub.

Start the backend:

```bash
uvicorn app.api:app --reload
```

The API will run at:

```txt
http://127.0.0.1:8000
```

Swagger/OpenAPI documentation is available at:

```txt
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Go to the frontend folder:

```bash
cd frontend
```

Create a `.env` file inside the `frontend` folder.

Use `frontend/.env.example` as a template:

```txt
VITE_API_BASE_URL=http://127.0.0.1:8000
```

If `VITE_API_BASE_URL` is not set, the frontend falls back to `http://127.0.0.1:8000`.

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

The frontend will run at:

```txt
http://localhost:5173
```

---

## Local Development

For local development, run the backend and frontend in two separate terminals.

### Terminal 1: Backend

From the project root:

```bash
uvicorn app.api:app --reload
```

### Terminal 2: Frontend

From the project root:

```bash
cd frontend
npm run dev
```

Then open:

```txt
http://localhost:5173
```

For normal development, keep live search disabled:

```txt
ALLOW_LIVE_SEARCH=false
```

Use cached searches while developing. Only enable live search when you intentionally want to spend a SerpAPI request.

To allow a new live search, both conditions must be true:

```txt
ALLOW_LIVE_SEARCH=true
```

and the frontend checkbox must be enabled:

```txt
Tillad live-søgning hvis cache mangler
```

After testing live search, set `ALLOW_LIVE_SEARCH` back to `false`.

### Cache files and error handling

Cached responses are stored in `cache/` in the project root, one JSON file per query. The file name is a stable key: a readable label from the query plus the first 16 hex characters of the SHA-256 hash of the normalized query (lowercase, repeated whitespace collapsed), for example `robotstøvsuger_med_moppe-e393725d9d5c75d7.json`. Different queries such as `laptop/16GB` and `laptop?16GB` therefore never share a file, and a query can never write outside the cache folder.

Cache files from older versions (named only from the lowercased query) are still used, but only when the SerpAPI response inside the file records the same query in `search_parameters.q`. Such files are copied to the new name on first use. Files that cannot be proven to belong to the query are ignored.

If SerpAPI is unreachable, times out or returns an error, the API responds with `502 Bad Gateway` and a Danish error message. Error responses are never written to the cache.

---

## API Usage

### Product Search

The main search endpoint is:

```txt
POST /api/search
```

Example request:

```json
{
  "query": "robotstøvsuger med moppe og høj sugeevne",
  "allow_live_search": false
}
```

Example response structure:

```json
{
  "query": "robotstøvsuger med moppe og høj sugeevne",
  "count": 40,
  "used_cache": true,
  "requirements": {
    "product_type": "robotstøvsuger",
    "max_price": null,
    "required_features": [
      "moppe",
      "høj sugeevne"
    ]
  },
  "products": [
    {
      "product": {
        "name": "Example product",
        "price": 3999,
        "url": "https://example.com",
        "image_url": "https://example.com/image.jpg",
        "rating": 4.5,
        "source": "Example Store"
      },
      "score": 75,
      "badges": [
        "Stærkt match",
        "Høj rating"
      ],
      "explanations": [
        "✓ Rating fundet (4.5)",
        "✓ Matcher krav: moppe"
      ]
    }
  ]
}
```

### Saved Searches Endpoints

```txt
GET /api/saved-searches
POST /api/saved-searches
DELETE /api/saved-searches/{saved_search_id}
```

Example save search request:

```json
{
  "query": "robotstøvsuger med moppe og høj sugeevne",
  "result_count": 40,
  "best_score": 75
}
```

Example saved search response:

```json
{
  "saved_search": {
    "id": "example-id",
    "query": "robotstøvsuger med moppe og høj sugeevne",
    "product_type": "robotstøvsuger",
    "max_price": null,
    "required_features": [
      "moppe",
      "høj sugeevne"
    ],
    "result_count": 40,
    "best_score": 75,
    "created_at": "2026-05-13T10:00:00+00:00"
  }
}
```

---

## Cache and Live Search

SerpAPI has a limited number of searches per month, so the project uses local caching.

The backend checks the cache first:

```txt
If cached result exists:
    use cache

If cache does not exist and live search is not allowed:
    return an error

If cache does not exist and live search is allowed:
    call SerpAPI and save the response to cache
```

There are two layers of protection.

### 1. Environment Variable

```txt
ALLOW_LIVE_SEARCH=false
```

This prevents new SerpAPI calls globally.

The backend reads `.env` from the project root once at startup. Variables that are already set in the environment take precedence over `.env`, so restart the backend after changing `.env`.

### 2. Frontend Checkbox

The frontend has a checkbox:

```txt
Tillad live-søgning hvis cache mangler
```

A live SerpAPI call is only made when:

```txt
ALLOW_LIVE_SEARCH=true
```

and the frontend request sends:

```json
{
  "allow_live_search": true
}
```

This prevents accidental API usage during development.

---

## Saved Searches

The application supports saved searches.

A saved search includes:

- Unique id
- Query text
- Parsed product type
- Maximum price
- Required features
- Result count
- Best score
- Creation timestamp

Saved searches are stored locally in:

```txt
data/saved_searches.json
```

The `data/` folder is ignored by Git because it contains runtime data.

The saved search feature currently supports:

- Saving a search
- Listing saved searches
- Reusing a saved search in the search input
- Running a saved search again
- Deleting a saved search
- Preventing duplicate saved searches
- Sorting saved searches newest first

The relevant backend logic is located in:

```txt
app/saved_searches.py
```

The relevant frontend component is located in:

```txt
frontend/src/components/SavedSearchesPanel.tsx
```

---

## Product Scoring

Products are scored based on:

- Price
- Rating
- Required feature matches

The score is capped at 100.

The scoring logic is located in:

```txt
app/scorer.py
```

---

## Feature Matching

Feature matching is handled in:

```txt
app/feature_matcher.py
```

The matcher supports simple Danish/English synonym matching.

Examples:

```txt
trådløs → wireless
vandtæt → waterproof
støjsvag → quiet
usb-c → usb c, usbc, type-c
høj sugeevne → strong suction, suction, pa
```

This makes the agent better at matching Danish user requests with English product titles.

---

## Recommendation Explanations

Each product includes explanations that describe why it received its score.

Example:

```txt
✓ Rating fundet (4.7)
✓ Matcher krav: moppe
? Ikke tydeligt om produktet matcher: høj sugeevne
```

This logic is located in:

```txt
app/explainer.py
```

---

## Product Badges

The frontend displays badges such as:

```txt
Stærkt match
Muligt match
Under budget
Høj rating
Matcher: usb-c
```

Badge logic is located in:

```txt
app/badge_generator.py
```

---

## Running Tests

Run all backend tests from the project root:

```bash
python -m pytest
```

Current test coverage includes:

- Requirements parsing
- Product scoring
- Feature matching
- Saved searches
- API endpoints with FastAPI's `TestClient` (search, validation, error codes, saved search lifecycle)
- Cache file naming and round trips
- Product search: price parsing, cache-first behaviour, live search guards and SerpAPI failures

The tests never call SerpAPI and never need an API key. `tests/conftest.py` blocks all outgoing HTTP requests, forces `ALLOW_LIVE_SEARCH=false`, removes `SERPAPI_API_KEY`, and redirects the cache and saved searches to a temporary folder for every test. Live search is tested with a mocked SerpAPI response.

---

### Frontend tests

The frontend has component tests with Vitest, React Testing Library and jsdom. `fetch` is stubbed with a small in-memory fake of the API, so no backend or SerpAPI key is needed:

```bash
cd frontend
npm test
```

They cover the search flow (parsed requirements, cache/live source, ranked products), the live-search checkbox, error messages (backend `detail`, FastAPI validation errors, non-JSON errors, unreachable backend), saving searches with duplicate protection, running and deleting saved searches, and product card rendering.

---

## Quality Checks

Run backend tests from the project root:

```bash
python -m pytest
```

Lint and build the frontend from the frontend folder:

```bash
cd frontend
npm run lint
npm test
npm run build
```

A healthy project state should have:

```txt
Backend tests passing
Frontend lint and production build passing
Git working tree clean
```

### Continuous integration

GitHub Actions (`.github/workflows/ci.yml`) runs on every push to `main` and on every pull request:

- Backend: installs `requirements-dev.txt` on Python 3.12 and runs `python -m pytest`
- Frontend: `npm ci`, `npm run lint`, `npm test` and `npm run build`

CI sets `ALLOW_LIVE_SEARCH=false` and provides no SerpAPI key, so it can never make paid API calls.

If the frontend build fails because of local path or sync-folder issues, run the build from the actual project folder path used by your system.

---

## Development Notes

The project is intentionally built in small layers:

1. Search input
2. Requirement parsing
3. Product search
4. Cache protection
5. Scoring
6. Explanations
7. Badges
8. Frontend presentation
9. Saved searches
10. Tests

This makes the system easier to understand, debug, and extend.

---

## Current Limitations

- Product links often point to Google Shopping rather than directly to the retailer.
- Product specifications are limited to what Google Shopping returns.
- Feature matching is still rule-based and not yet powered by an LLM.
- The search parser is simple and does not fully understand complex natural language.
- Saved searches are stored in a local JSON file rather than a database.
- There is no user login or multi-user support yet.
- There is no price history tracking yet.
- There is no production deployment yet.

---

## Possible Future Improvements

- Direct retailer link lookup
- Price history tracking
- Saved searches backed by a database
- Email or push notifications for price drops
- Affiliate link support
- LLM-based requirement parsing
- LLM-based product analysis
- Review summarization
- Mobile app
- User accounts
- PostgreSQL database
- Deployment to cloud hosting
- Admin dashboard for monitoring searches and cache usage

---

## Purpose

This project is both a learning project and a potential product prototype.

It demonstrates:

- Full-stack development
- API integration
- React frontend development
- FastAPI backend development
- Caching strategy
- Test-driven improvements
- Basic recommendation logic
- Local persistence with JSON storage
- A practical AI-agent style architecture