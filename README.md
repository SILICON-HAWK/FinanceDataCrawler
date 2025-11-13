# Finance Data Crawler

An advanced Python application for scraping financial data from Indian stock market companies listed on screener.in.

## 🎯 Features

### ✅ Completed Features

- **Web Scraping Engine**: Robust HTTP request handling with automatic retries and rate limiting
- **Comprehensive Data Extraction**: Extracts 7 types of financial data:
  - Company information (name, stock price, market cap, ratios)
  - Quarterly financial data
  - Profit & Loss statements with compounded growth metrics
  - Balance sheets
  - Cash flow statements
  - Financial ratios over time
  - Shareholding patterns (quarterly and yearly)
- **Queue-Based Crawling**: Efficient queue management for sector and company URLs
- **Smart Deduplication**: Hash map implementation for tracking visited sectors and companies
- **Dual Storage System**:
  - JSON files for immediate access
  - SQLite database for structured queries and analytics
- **Progress Tracking**: Real-time progress monitoring with statistics
- **Data Validation**: Quality checks and scoring for extracted data
- **CLI Interface**: Full-featured command-line interface
- **Resume Capability**: Automatically resumes from where it left off
- **Rate Limiting**: Respects website rate limits (15s interval, handles 429 responses)
- **Error Handling**: Comprehensive error logging and recovery
- **Configuration Management**: Flexible configuration system

## 📁 Project Structure

```
FinanceDataCrawler/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # CLI entry point
│   ├── config.py             # Configuration management
│   ├── crawler.py            # Main crawler logic
│   ├── extractors.py         # Data extraction functions
│   ├── storage.py            # Storage layer (JSON + SQLite)
│   ├── deduplication.py      # Hash map for deduplication
│   ├── progress.py           # Progress tracking
│   └── validation.py         # Data validation
├── companies/                # Extracted company data (JSON)
├── json/                     # Intermediate data files
├── logs/                     # Application logs
├── data/                     # Additional data storage
├── run.py                    # Convenience runner script
├── requirements.txt          # Python dependencies
├── finance_data.db          # SQLite database
├── sectors_queue.json       # Queue of sector URLs
├── company_queue.json       # Queue of company URLs
├── visited_sectors.json     # Visited sectors tracker
├── visited_companies.json   # Visited companies tracker
├── progress.json            # Progress data
└── README.md                # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd FinanceDataCrawler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python run.py --help
```

## 📖 Usage

The crawler provides a comprehensive CLI interface with multiple commands:

### Basic Commands

#### 1. Start Crawling

```bash
# Crawl all sectors (no time limit)
python run.py crawl

# Crawl with 1 hour timeout
python run.py crawl --timeout 3600

# Crawl only first 5 sectors
python run.py crawl --limit 5

# Crawl and skip already visited sectors
python run.py crawl --skip-visited

# Use custom sectors file
python run.py crawl --sectors-file custom_sectors.json
```

#### 2. Check Status

```bash
# Show current status and statistics
python run.py status

# Show status with recent errors
python run.py status --show-errors

# Show status with last 20 errors
python run.py status --show-errors --error-limit 20
```

#### 3. List Companies

```bash
# List all companies from JSON storage
python run.py list

# List companies from database
python run.py list --from-db
```

#### 4. Validate Data

```bash
# Validate all companies
python run.py validate

# Validate specific company
python run.py validate --company "Sun Pharmaceuticals Industries Ltd"

# Validate from database
python run.py validate --from-db
```

#### 5. Reset Data

```bash
# Reset all tracking data
python run.py reset --all

# Reset only visited sectors
python run.py reset --sectors

# Reset only visited companies
python run.py reset --companies

# Reset progress data
python run.py reset --progress

# Clear error log
python run.py reset --errors
```

#### 6. Configuration

```bash
# Show current configuration
python run.py config --show

# Save configuration to file
python run.py config --save my_config.json

# Load configuration from file
python run.py config --load my_config.json
```

### Advanced Usage

#### Enable Debug Logging

```bash
python run.py --log-level DEBUG crawl
```

#### Crawl with Custom Settings

Edit `src/config.py` or create a custom config file:

```python
# Custom configuration example
{
    "RATE_LIMIT_INTERVAL": 20,
    "REQUEST_TIMEOUT": 15,
    "MAX_RETRIES": 5,
    "SECTOR_PAGE_LIMIT": 100
}
```

Then load it:
```bash
python run.py config --load custom_config.json
python run.py crawl
```

## 📊 Data Storage

### JSON Storage

All company data is saved as individual JSON files in the `companies/` directory:

```
companies/
├── Sun Pharmaceuticals Industries Ltd.json
├── Kaveri Seed Company Ltd.json
└── ...
```

Each file contains:
- Company basic information
- Stock price and ratios
- Quarters data
- Profit & Loss data
- Balance sheet data
- Cash flows data
- Ratios data
- Shareholding data

### SQLite Database

The SQLite database (`finance_data.db`) provides structured storage with tables:

- `companies`: Basic company information
- `ratios`: Financial ratios
- `quarters_data`: Quarterly data
- `financial_statements`: All financial statements (JSON)
- `crawl_history`: Crawl attempt logs

Query the database using any SQLite client:
```bash
sqlite3 finance_data.db "SELECT company_name, stock_price FROM companies LIMIT 10;"
```

## 🔧 Configuration Options

Key configuration parameters in `src/config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `RATE_LIMIT_INTERVAL` | 15 | Seconds between requests |
| `REQUEST_TIMEOUT` | 10 | Request timeout in seconds |
| `MAX_RETRIES` | 3 | Maximum retry attempts |
| `RATE_LIMIT_WAIT` | 60 | Wait time after 429 response |
| `SECTOR_PAGE_LIMIT` | 50 | Companies per sector page |
| `DB_TYPE` | "sqlite" | Database type |
| `LOG_LEVEL` | "INFO" | Logging level |

## 📈 Progress Tracking

The crawler automatically tracks:
- Session start/end times
- Sectors processed vs total
- Companies processed vs total
- Success/failure rates
- Recent errors with timestamps

View progress anytime:
```bash
python run.py status
```

## 🛡️ Error Handling

The crawler includes robust error handling:

- **Automatic Retries**: Failed requests are retried with exponential backoff
- **Rate Limit Handling**: Automatically waits when rate limits are hit (HTTP 429)
- **Error Logging**: All errors are logged with context
- **Graceful Failures**: Continues crawling even if individual companies fail
- **Resume Support**: Resumes from last successful position

## 🔍 Data Validation

Built-in data validation features:

- **Required Field Checks**: Ensures all critical fields are present
- **Quality Scoring**: Calculates quality score (0-100) for each company
- **Freshness Checks**: Identifies latest available data
- **Batch Validation**: Validates all crawled data at once

Run validation:
```bash
python run.py validate
```

## 📝 Development Status

### Completed Tasks ✅

- Task 1: HTML Retrieval ✔️
- Task 2: Data Extraction ✔️
- Task 3.1: Queue Implementation ✔️
- Task 3.2: Hash Map Implementation ✔️
- Task 4.1-4.3: Database Implementation (SQLite) ✔️
- **New**: Progress Tracking ✔️
- **New**: Data Validation ✔️
- **New**: CLI Interface ✔️
- **New**: Configuration Management ✔️
- **New**: Error Recovery ✔️

### Future Enhancements 🎯

- Task 4: PostgreSQL Support
- Task 5: Interactive Dashboard
  - Search function
  - Company comparison
  - Data visualization
  - Export features

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

[Add your license here]

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Rate limit exceeded" errors
```bash
# Increase rate limit interval in config
python run.py config --show
# Edit RATE_LIMIT_INTERVAL in src/config.py
```

**Issue**: Crawler stops unexpectedly
```bash
# Check progress and resume
python run.py status
python run.py crawl  # Will resume automatically
```

**Issue**: Database locked error
```bash
# Close any open database connections
# Restart the crawler
```

## 📞 Support

For issues and questions:
- Check the logs in `logs/crawler.log`
- Run `python run.py status --show-errors`
- Review the configuration with `python run.py config --show`

---

**Version**: 2.0.0
**Last Updated**: 2024
