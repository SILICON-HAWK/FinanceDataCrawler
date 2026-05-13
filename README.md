# FinanceDataCrawler

Scrapes financial data for listed Indian companies from Screener.in, stores it as JSON, and serves it via a SvelteKit dashboard.

## Structure

```
backend/                         # FastAPI server
├── main.py                      # Entry point — uvicorn backend.main:app
├── requirements.txt
├── Dockerfile
├── pipeline/                    # Core scraping pipeline (moved from pipeline/)
│   ├── main.py                  # FinanceDataPipeline orchestrator
│   ├── config.py                # Paths, selectors, rate-limit config
│   ├── core/
│   │   ├── crawler.py           # HTTP client with UA rotation + rate limiting
│   │   ├── queue_manager.py     # Sector/company queue persistence + search
│   │   └── storage.py           # JSON read/write for company data
│   ├── parsers/                 # HTML parsers (sector, company)
│   └── utils/                   # Helpers, logger
├── api/
│   ├── schemas.py               # Pydantic models
│   ├── deps.py                  # DI helpers
│   └── routes/
│       ├── discovery.py         # Sector & company discovery
│       ├── extraction.py        # Company extraction (single/bulk)
│       └── status.py            # Pipeline status, company listing
└── data/                        # Queue files (sectors, companies, visited)

frontend/                        # SvelteKit app
├── src/
│   ├── lib/api.js               # API client → FastAPI backend
│   ├── lib/components/
│   ├── routes/
│   │   ├── +page.svelte         # Dashboard / company list
│   │   ├── discover/+page.svelte # Admin: run discovery
│   │   ├── extract/+page.svelte  # Admin: trigger extraction
│   │   └── company/[name]/      # Company detail page
│   └── app.css
├── Dockerfile
└── package.json

companies/                       # Extracted company JSON files
backend/data/                    # Queue state files (sectors, companies, visited)
```

## Quick Start (Local Dev)

**1. Backend (FastAPI):**

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

API runs at `http://localhost:8000`. Docs at `/docs`.

**2. Frontend (SvelteKit):**

```bash
cd frontend
npm install
npm run dev -- --host
```

Frontend runs at `http://localhost:5173`.

## Docker

```bash
docker compose up backend-dev frontend-dev
```

Or fully containerized:

```bash
docker compose up -d backend-dev frontend-dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Pipeline stats (sectors, companies, storage) |
| `POST` | `/api/discover/sectors` | Scrape Screener.in explore page → populate sector queue |
| `POST` | `/api/discover/companies` | Scrape unvisited sectors → populate company queue |
| `GET` | `/api/companies` | List discovered companies grouped by sector (`?search=`) |
| `GET` | `/api/companies/{name}` | Get extracted JSON for a company |
| `POST` | `/api/extract` | Extract companies (`company_urls[]`, `sector_names[]`, `max_companies`, `skip_existing`) |
| `GET` | `/api/extract/status` | Current extraction progress |

All long-running operations run in background threads. Check `/api/extract/status` to poll progress.

## Frontend Pages

| Route | Description |
|-------|-------------|
| `/` | Company listing with search & filter |
| `/company/[name]` | Full financial data (quarterly, balance sheet, cash flows, ratios, shareholding) |
| `/discover` | Admin: run sector & company discovery, see queue stats |
| `/extract` | Admin: browse companies by sector, select, trigger extraction |

## Running the Pipeline

From the admin UI (`/discover`):
1. Click **Discover Sectors** to scrape the Screener.in explore page
2. Click **Discover Companies** to find all companies in unvisited sectors
3. Go to `/extract`, select sectors, click **Start Extraction**
