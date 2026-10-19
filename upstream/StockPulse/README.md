# StockPulse

A news aggregator for Indian equity markets (NSE/BSE) focused on Nifty 50 stocks. Select a stock and a time window to receive three categorised views of relevant news: direct company coverage, supply chain and related company signals, and sector-level macro factors — all sourced from free, credible Indian financial media.

---

## Features

- **Direct company news** — headlines, financial results, and official BSE corporate announcements for the selected stock
- **Supply chain and related news** — news about key input suppliers, competitors, and commodity prices that affect the stock's cost base or revenue
- **Sector and macro news** — RBI policy, sector-wide trends, and broader market forces relevant to the stock's industry
- **Hand-curated dependency map** — supply chain relationships for all 50 Nifty stocks, with static "why it matters" labels on every article
- **Time range filtering** — 24h, 48h, 72h, 1 week, or 2 weeks
- **Password-protected access** — the entire application sits behind a shared password gate; suitable for private or limited distribution

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11+) |
| Frontend | React 18 + Vite + TypeScript |
| Styling | Tailwind CSS v4 |
| RSS parsing | feedparser |
| HTTP client | httpx (async) |
| Caching | cachetools TTLCache (30-minute in-memory RSS cache) |
| Environment | python-dotenv |

---

## Data Sources

All sources are free with no credit card required.

| Source | Category | Notes |
|---|---|---|
| 14 curated RSS feeds | All categories | ET Markets, Business Standard, Mint, NDTV Profit, BusinessLine, Reuters India, Financial Express, CNBC TV18 — cached in memory for 30 minutes |
| BSE public announcements API | Direct (company) | Official corporate filings and disclosures from bseindia.com |
| Marketaux API | Direct (company) | Ticker-tagged news; 100 requests/day on the free tier |

All article URLs are validated against a trusted domain allowlist before being returned, preventing non-financial sources from appearing in results.

---

## Project Structure

```
StockPulse/
├── backend/
│   ├── main.py                    # FastAPI app, CORS, password middleware
│   ├── routers/
│   │   └── news.py                # GET /api/stocks, GET /api/news, POST /api/auth
│   ├── services/
│   │   ├── rss_service.py         # RSS fetch, TTLCache, domain filter, keyword matching
│   │   ├── marketaux_service.py   # Marketaux ticker-tagged news
│   │   ├── bse_service.py         # BSE corporate announcements
│   │   └── newsapi_service.py     # Disabled (returns empty list)
│   ├── data/
│   │   ├── stocks.py              # Nifty 50 stock list
│   │   └── dependency_map.py      # Supply chain dependency map for all 50 stocks
│   ├── models/
│   │   └── schemas.py             # Pydantic response models
│   ├── .env                       # API keys — not committed
│   ├── .env.example               # Environment variable template
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Root component, layout, auth gate
│   │   ├── components/
│   │   │   ├── LoginScreen.tsx    # Password entry screen
│   │   │   ├── StockSelector.tsx  # Searchable Nifty 50 dropdown
│   │   │   ├── TimeRangeSelector.tsx
│   │   │   ├── NewsSection.tsx    # Categorised section with header
│   │   │   ├── NewsCard.tsx       # Individual article card
│   │   │   └── LoadingSpinner.tsx
│   │   ├── api/
│   │   │   └── client.ts          # Fetch wrapper with password header
│   │   └── types/
│   │       └── news.ts            # TypeScript interfaces
│   ├── vercel.json
│   ├── vite.config.ts
│   └── package.json
├── render.yaml                    # Render deployment configuration
└── .gitignore
```

---

## Local Development

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```
MARKETAUX_API_KEY=your_marketaux_key_here
SITE_PASSWORD=your_chosen_password
```

`SITE_PASSWORD` can be left empty during local development — the password gate is skipped when no value is set.

Start the backend:

```bash
uvicorn main:app --reload
# Runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

The Vite dev server proxies all `/api` requests to `http://localhost:8000` automatically.

---

## API Reference

### `GET /api/stocks`
Returns the full Nifty 50 stock list for the dropdown.

### `GET /api/news?symbol=MARUTI&timerange=48h`
Returns categorised news for the given stock and time range.

Valid `timerange` values: `24h`, `48h`, `72h`, `1w`, `2w`

**Response schema:**
```json
{
  "stock": { "symbol": "MARUTI", "name": "Maruti Suzuki India Ltd", "sector": "Automobile" },
  "timerange": "48h",
  "categories": {
    "direct":       [ ...NewsItem ],
    "supply_chain": [ ...NewsItem ],
    "macro":        [ ...NewsItem ]
  },
  "total": 24,
  "fetched_at": "2025-05-21T10:30:00Z"
}
```

**NewsItem schema:**
```json
{
  "title": "string",
  "snippet": "string",
  "url": "string",
  "source": "string",
  "published_at": "ISO 8601 datetime",
  "category": "direct | supply_chain | macro",
  "why_it_matters": "string"
}
```

### `POST /api/auth`
Validates the site password. Used by the login screen.

```json
// Request
{ "password": "string" }

// Response — 200 OK
{ "ok": true }

// Response — 401 Unauthorized
{ "ok": false }
```

All other endpoints require an `X-Password` header matching the configured `SITE_PASSWORD`.

---

## Deployment

### Backend — Render

1. Create a new **Web Service** on [render.com](https://render.com) pointing to this repository
2. Set **Root Directory** to `backend`
3. **Build command**: `pip install -r requirements.txt`
4. **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `SITE_PASSWORD` — the password users will enter on the login screen
   - `MARKETAUX_API_KEY` — from [marketaux.com](https://marketaux.com)

A `render.yaml` file is included at the project root for reference.

Note: The free tier on Render spins down the service after 15 minutes of inactivity. The first request after an idle period takes approximately 30-50 seconds to respond while the server boots.

### Frontend — Vercel

1. Create a new project on [vercel.com](https://vercel.com) pointing to this repository
2. Set **Root Directory** to `frontend`
3. Add environment variable:
   - `VITE_API_URL` — the full Render backend URL (e.g. `https://your-service.onrender.com`)
4. Deploy

---

## Extending the Stock Coverage

The application is designed to make adding new stocks straightforward.

**Step 1 — Add to the stock list** (`backend/data/stocks.py`):
```python
{"symbol": "NEWSYMBOL", "name": "Company Full Name", "sector": "Sector"},
```

**Step 2 — Add to the dependency map** (`backend/data/dependency_map.py`):
```python
"NEWSYMBOL": {
    "display_name": "Company Short Name",
    "sector": "Sector",
    "direct_keywords": ["Company Name", "Ticker"],
    "related_companies": {
        "Related Co Name": "Why this relationship matters to the stock",
    },
    "commodity_keywords": ["relevant commodity 1", "relevant commodity 2"],
    "macro_keywords": ["sector trend", "relevant policy keyword"],
},
```

**Step 3 — Add the BSE scrip code** (`backend/services/bse_service.py`):
```python
"NEWSYMBOL": "BSE_SCRIP_CODE",
```
BSE scrip codes can be found by searching the company on [bseindia.com](https://www.bseindia.com).

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `MARKETAUX_API_KEY` | Recommended | Free API key from marketaux.com. If not set, Marketaux news is skipped silently. |
| `SITE_PASSWORD` | Recommended | Password for the login gate. If not set, the gate is disabled and all requests pass through. |
| `VITE_API_URL` | Production only | Full URL of the deployed backend, set in the Vercel frontend environment. Not needed for local development. |
