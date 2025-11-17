# Finance Data Crawler Dashboard

A comprehensive full-stack application for crawling, storing, and visualizing financial data from Screener.in for Listed Indian Companies. Built with modern technologies including FastAPI, PostgreSQL, Next.js, and Docker.

## Features

### Backend (FastAPI + PostgreSQL)
- ✅ RESTful API with FastAPI
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Dual storage: JSON files + PostgreSQL
- ✅ Automatic data migration from JSON to PostgreSQL
- ✅ Company financial data endpoints
- ✅ Search and comparison APIs
- ✅ Crawl queue management
- ✅ Interactive API documentation (Swagger/OpenAPI)

### Frontend (Next.js 14 + TypeScript)
- ✅ Modern Next.js 14 with App Router
- ✅ TypeScript for type safety
- ✅ Tailwind CSS for styling
- ✅ Real-time data visualization with Recharts
- ✅ Company dashboard with financial charts
- ✅ Company comparison tool
- ✅ Search functionality
- ✅ Add companies to crawl queue via UI
- ✅ Responsive design

### Data Crawler
- ✅ Web scraping from Screener.in
- ✅ Queue-based crawling system
- ✅ Rate limiting and retry logic
- ✅ Comprehensive financial data extraction:
  - Balance Sheet
  - Profit & Loss
  - Cash Flows
  - Quarterly Data
  - Financial Ratios
  - Shareholding Patterns

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Charts | Recharts |
| State Management | TanStack Query (React Query) |
| Containerization | Docker, Docker Compose |
| Web Scraping | BeautifulSoup4, Requests |

## Project Structure

```
FinanceDataCrawler/
├── backend/
│   ├── main_db.py              # FastAPI app with PostgreSQL
│   ├── models.py               # SQLAlchemy models
│   ├── database.py             # Database configuration
│   ├── crud.py                 # CRUD operations
│   ├── migrate_json_to_db.py   # JSON to PostgreSQL migration
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile
├── frontend-nextjs/
│   ├── src/
│   │   ├── app/                # Next.js app router pages
│   │   ├── components/         # React components
│   │   └── lib/                # API client and utilities
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
├── companies/                  # Individual company JSON files
├── json/                       # Latest scraped financial data
├── docker-compose.yml          # Docker Compose configuration
├── setup.sh                    # Automated setup script
└── README.md
```

## Quick Start

### Option 1: Docker (Recommended)

1. **Prerequisites**
   - Docker and Docker Compose installed
   - At least 2GB of free RAM

2. **Setup and Run**
   ```bash
   # Make setup script executable
   chmod +x setup.sh

   # Run setup
   ./setup.sh
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Install PostgreSQL**
   ```bash
   # Create database
   createdb finance_crawler
   ```

2. **Setup Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure database**
   ```bash
   # Copy .env.example to .env and update if needed
   cp .env.example .env
   ```

4. **Migrate JSON data to PostgreSQL**
   ```bash
   python migrate_json_to_db.py
   ```

5. **Run the backend**
   ```bash
   uvicorn main_db:app --reload --port 8000
   ```

#### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend-nextjs
   npm install
   ```

2. **Run the development server**
   ```bash
   npm run dev
   ```

3. **Open browser**
   - Navigate to http://localhost:3000

## API Endpoints

### Companies
- `GET /api/companies` - List all companies
- `GET /api/companies/{name}` - Get company details
- `GET /api/companies/{name}/balance-sheet` - Balance sheet data
- `GET /api/companies/{name}/profit-loss` - P&L data
- `GET /api/companies/{name}/cash-flows` - Cash flow data
- `GET /api/companies/{name}/quarters` - Quarterly data
- `GET /api/companies/{name}/ratios` - Financial ratios
- `GET /api/companies/{name}/shareholding` - Shareholding pattern

### Search & Compare
- `POST /api/search` - Search companies
- `POST /api/companies/compare` - Compare multiple companies

### Crawl Queue
- `GET /api/queue/status` - Get queue status
- `POST /api/crawl/add-company` - Add company to crawl queue

### Statistics
- `GET /api/stats` - Get overall statistics

## Database Schema

### Main Tables
- `companies` - Company master data
- `balance_sheets` - Balance sheet time series
- `profit_loss` - P&L statements
- `cash_flows` - Cash flow statements
- `quarterly_data` - Quarterly financial data
- `financial_ratios` - Financial ratios
- `shareholding` - Shareholding patterns
- `crawl_queue` - Crawl queue management
- `sectors` - Sector information

All tables include proper indexes for performance and foreign key relationships.

## Data Storage

The application supports **dual storage**:

1. **JSON Files** (Legacy/Backup)
   - Located in `companies/` and `json/` directories
   - Human-readable
   - Easy to backup and version control

2. **PostgreSQL Database** (Primary)
   - Structured relational data
   - Fast querying and indexing
   - Support for complex queries and aggregations

**Migration**: Use `migrate_json_to_db.py` to sync JSON data to PostgreSQL.

## Usage Guide

### Dashboard
- View all scraped companies
- Search companies by name
- Quick stats overview (total companies, queue status)

### Company Details
- Click any company to view detailed information
- Interactive charts for financial trends
- Key metrics display
- Historical financial data tables

### Compare Companies
- Select up to 5 companies
- Visual comparison with charts
- Side-by-side metrics comparison

### Add Company to Queue
- Enter Screener.in company URL
- Set priority (0-10)
- Company will be added to crawl queue
- Monitor queue status

## Development

### Run with hot reload
```bash
# Backend
cd backend
uvicorn main_db:app --reload

# Frontend
cd frontend-nextjs
npm run dev
```

### Database Migrations
```bash
# Run migration from JSON to PostgreSQL
python backend/migrate_json_to_db.py
```

## Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose build

# Run migrations
docker-compose run --rm backend python migrate_json_to_db.py

# Access PostgreSQL
docker-compose exec postgres psql -U finance_user -d finance_crawler
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://finance_user:finance_pass@localhost:5432/finance_crawler
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Backend won't start
- Check if PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure all Python dependencies are installed

### Frontend won't connect to backend
- Verify backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in .env.local
- Check browser console for CORS errors

### Database connection errors
- Verify PostgreSQL is running: `docker-compose ps`
- Check database credentials
- Ensure database exists: `createdb finance_crawler`

### Migration fails
- Ensure JSON files exist in `companies/` and `json/`
- Check database permissions
- Verify database schema is created

## Crawler Notes & Best Practices

**1. Processing Limit:**
- Set a limit on the number of pages to scrape per session

**2. Rate Limit:**
- ✅ Implemented: 15-second delay between HTTP requests
- Prevents overwhelming the website
- Respects Screener.in's server resources

**3. Crawl Limit:**
- Set a limit on the number of crawls throughout the website per session
- Currently: 86 sectors total

**4. Hash Map for Listed Companies:**
- ✅ Implemented via PostgreSQL and visited tracking
- Prevents duplicate scraping
- Efficient lookup and deduplication

## Roadmap

- [ ] User authentication and authorization
- [ ] Real-time crawler status monitoring
- [ ] Email alerts for company updates
- [ ] Export data to CSV/Excel
- [ ] Advanced filtering and sorting
- [ ] Sector-wise analysis
- [ ] Portfolio tracking
- [ ] Historical price charts
- [ ] GraphQL API (optional Hasura integration)
- [ ] Mobile app (React Native)

## License

MIT License

## Acknowledgments

- Data source: [Screener.in](https://www.screener.in)
- Built with modern open-source technologies

---

**Note**: This tool is for educational and research purposes. Please respect Screener.in's terms of service and rate limits when scraping data.
