# AI Deal Agent

AI Deal Agent is a full-stack prototype for an AI-assisted product search and deal recommendation tool.

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

It then searches for products, scores them, and presents the results in a webshop like interface.

---

## Current Features

- React frontend with product cards
- FastAPI backend
- SerpAPI Google Shopping integration
- Local cache to avoid unnecessary API calls
- Controlled live search to protect API quota
- Product scoring
- Product badges
- Recommendation explanations
- Parsed search requirements shown in the UI
- Feature matching with simple Danish/English synonym support
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
│   └── scorer.py
│
├── cache/
│   └── cached SerpAPI responses
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   └── App.css
│   └── package.json
│
├── tests/
│   ├── test_feature_matcher.py
│   ├── test_requirements_parser.py
│   └── test_scorer.py
│
├── .env
├── .gitignore
├── pytest.ini
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

---

## Backend Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```txt
SERPAPI_API_KEY=your_serpapi_key_here
ALLOW_LIVE_SEARCH=false
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

## API Usage

The main endpoint is:

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

### 2. Frontend Checkbox

The frontend has a checkbox:

```txt
Allow live search if cache is missing
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

Run all tests:

```bash
python -m pytest
```

Current test coverage includes:

- Requirements parsing
- Product scoring
- Feature matching

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
9. Tests

This makes the system easier to understand, debug, and extend.

---

## Current Limitations

- Product links often point to Google Shopping rather than directly to the retailer.
- Product specifications are limited to what Google Shopping returns.
- Feature matching is still rule-based and not yet powered by an LLM.
- The search parser is simple and does not fully understand complex natural language.
- There is no user login, database, or saved search history yet.
- There is no price history tracking yet.
- There is no production deployment yet.

---

## Possible Future Improvements

- Direct retailer link lookup
- Price history tracking
- Saved searches
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
- A practical AI-agent style architecture