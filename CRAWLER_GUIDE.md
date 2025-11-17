# 🚀 Finance Data Crawler - Usage Guide

## Overview

The Finance Data Crawler scrapes company financial data from screener.in with:
- ⏱️  Rate limiting (15 seconds between requests)
- 🔄 Automatic retries on failures
- 📊 Real-time progress logging
- 💾 Automatic data saving (JSON + PostgreSQL)

## Quick Start

### Option 1: Using Make Commands (Recommended)

```bash
# Test crawl a single company
make crawl-test

# Run full crawler
make crawl
```

### Option 2: Direct Python Execution

```bash
# Make sure dependencies are installed
pip install -r backend/requirements.txt

# Run the crawler
python crawler_main.py
```

### Option 3: Inside Docker Container

```bash
# Access backend container
docker exec -it finance_crawler_backend bash

# Run crawler inside container
python /app/crawler_main.py
```

## What You'll See

When the crawler runs, you'll see real-time output like this:

```
============================================================
🚀 FINANCE DATA CRAWLER
============================================================
⚙️  Rate limit: 15s between requests
🔄 Max retries: 3
============================================================

============================================================
📊 Starting scrape: /company/SUNPHARMA/
============================================================
⏳ Rate limiting: waiting 0.0 seconds...
🌐 Requesting: https://www.screener.in/company/SUNPHARMA/consolidated/
✅ Success: https://www.screener.in/company/SUNPHARMA/consolidated/

📈 Extracting company overview...
✅ Company: Sun Pharmaceuticals Industries Ltd
   Price: 1,809
   Change: -2.66%

📊 Extracting quarterly data...
💰 Extracting balance sheet...
💾 Saving data to JSON...
✅ Saved: companies/Sun Pharmaceuticals Industries Ltd.json

🎉 Successfully scraped Sun Pharmaceuticals Industries Ltd
📊 Total companies scraped this session: 1

============================================================
✅ CRAWLER TEST COMPLETED SUCCESSFULLY
============================================================
📁 Data saved in:
   - json/company_data.json
   - json/quarters_data.json
   - json/balance_sheet_data.json
   - companies/*.json
============================================================
```

## Output Files

### Directory Structure
```
FinanceDataCrawler/
├── json/                              # Latest scraped data
│   ├── company_data.json             # Company overview
│   ├── quarters_data.json            # Quarterly financials
│   ├── balance_sheet_data.json       # Balance sheet
│   ├── cash_flows_data.json          # Cash flow statements
│   ├── ratios_data.json              # Financial ratios
│   └── shareholding_data.json        # Shareholding patterns
│
└── companies/                         # Archive of all scraped companies
    ├── Sun Pharmaceuticals Industries Ltd.json
    ├── Reliance Industries Ltd.json
    └── ...
```

## Customizing the Crawler

### Scrape a Different Company

Edit `crawler_main.py` and change the company URL:

```python
# Find this line in the main() function:
test_company = "/company/SUNPHARMA/"

# Change to your desired company:
test_company = "/company/RELIANCE/"  # Reliance Industries
test_company = "/company/TCS/"       # Tata Consultancy Services
test_company = "/company/INFY/"      # Infosys
```

### Adjust Rate Limiting

Edit the configuration at the top of `crawler_main.py`:

```python
# Configuration
RATE_LIMIT_INTERVAL = 15  # Increase to 20 for slower crawling
MAX_RETRIES = 3           # Number of retry attempts
REQUEST_TIMEOUT = 10      # Timeout in seconds
```

## Advanced Usage

### Scrape Multiple Companies

Create a list of companies and loop through them:

```python
companies = [
    "/company/SUNPHARMA/",
    "/company/RELIANCE/",
    "/company/TCS/",
    "/company/INFY/",
]

crawler = FinanceCrawler()
for company_url in companies:
    success = crawler.scrape_company(company_url)
    if not success:
        logger.error(f"Failed to scrape {company_url}")
```

### Scrape from Queue

The crawler integrates with the queue system. Companies added via the web interface are stored in the database and can be processed:

```python
from backend.crud import get_pending_companies
from backend.database import SessionLocal

db = SessionLocal()
pending = get_pending_companies(db)

for company in pending:
    crawler.scrape_company(f"/company/{company.name}/")
```

## Integration with Web App

The crawler data automatically syncs with the web application:

1. **Manual Crawl** → Run `make crawl` → Data saved to JSON
2. **Migration** → Run `make migrate` → JSON imported to PostgreSQL
3. **Web App** → View at `http://localhost:3000` → Data displayed

### Auto-Migration

The Docker setup runs migration automatically on startup, so newly scraped data appears in the web app immediately after restarting the backend:

```bash
# Crawl new data
make crawl

# Restart backend to trigger migration
docker-compose restart backend

# View in browser
open http://localhost:3000
```

## Troubleshooting

### Issue: Rate Limiting (HTTP 429)

**Solution:** The crawler automatically waits 60 seconds and retries. If this persists, increase `RATE_LIMIT_INTERVAL`:

```python
RATE_LIMIT_INTERVAL = 20  # Increase from 15 to 20 seconds
```

### Issue: Timeout Errors

**Solution:** Increase the timeout value:

```python
REQUEST_TIMEOUT = 20  # Increase from 10 to 20 seconds
```

### Issue: Connection Errors

**Solution:** Check your internet connection. The crawler requires access to `https://www.screener.in`.

### Issue: Missing Data Fields

**Solution:** Some companies may not have all data sections. The crawler logs warnings for missing sections but continues execution.

## Rate Limiting Best Practices

**Important:** Respect the website's resources:

- ✅ Keep rate limit at 15+ seconds
- ✅ Run crawler during off-peak hours
- ✅ Limit batch size to 10-20 companies per session
- ❌ Don't run multiple instances simultaneously
- ❌ Don't reduce rate limit below 10 seconds

## CLI Commands Summary

```bash
# Crawler commands
make crawl          # Run live crawler
make crawl-test     # Test with single company
python crawler_main.py  # Direct execution

# View data
python run.py list          # List all companies
python run.py info "Name"   # Show company details
python run.py validate      # Validate data quality

# Migrate to database
make migrate        # Import JSON to PostgreSQL
```

## API Integration (Future)

The crawler can be triggered via API (coming soon):

```bash
# Trigger crawl via API
curl -X POST http://localhost:8000/api/crawl/trigger \
  -H "Content-Type: application/json" \
  -d '{"company_url": "/company/SUNPHARMA/"}'
```

## Monitoring Crawler Status

### Real-time via WebSocket

The web dashboard shows real-time crawler status at `http://localhost:3000` with:
- Currently scraping company
- Progress percentage
- Estimated time remaining
- Success/failure statistics

### Via CLI

```bash
# Check crawler statistics
python run.py status

# Output:
# Total Companies: 3
# Data Quality Score: 95/100
# Last Crawl: 2025-11-17 10:30:00
```

## Performance

### Expected Timing
- Single company: ~15-20 seconds (rate limit)
- 10 companies: ~2.5-3 minutes
- 100 companies: ~25-30 minutes

### Optimization Tips
1. Run crawler overnight for large batches
2. Use queue system to prioritize companies
3. Monitor logs for errors and retry failures
4. Regular database cleanup for old data

## Legal & Ethical Usage

⚠️ **Important Notes:**
- This crawler is for personal educational use only
- Respect screener.in's Terms of Service
- Do not overload their servers with requests
- Always maintain rate limiting
- Consider using their official API if available for commercial use

## Support

For issues or questions:
1. Check logs: `docker-compose logs backend`
2. Review `FEATURES.md` for advanced features
3. Check GitHub issues: [Create new issue](https://github.com/SILICON-HAWK/FinanceDataCrawler/issues)

---

**Happy Crawling! 🕷️📊**
