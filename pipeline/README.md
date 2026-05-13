# Finance Data Crawler Pipeline

A robust, modular pipeline for extracting comprehensive financial data from Screener.in for Indian companies.

## ✅ Status: COMPLETE - Pipeline Structure Built

The pipeline has been successfully implemented with a modular, production-ready structure.

## Structure

```
pipeline/
├── __init__.py
├── main.py                # Pipeline entry point and orchestration ✅
├── config.py              # Constants, Base URLs, User-Agents, and Rate Limits ✅
├── core/                  # Core business logic modules ✅
│   ├── __init__.py
│   ├── crawler.py         # HTTP Client with UA rotation and rate-limit handling ✅
│   ├── queue_manager.py   # Logic for sector/company queues and visited tracking ✅
│   └── storage.py         # Interface for saving/loading JSON data ✅
├── parsers/               # Data extraction parsers ✅
│   ├── __init__.py
│   ├── base_parser.py     # Base class for parsing logic ✅
│   ├── sector_parser.py   # Extracts company links from sector pages ✅
│   └── company_parser.py  # Orchestrates extraction of all company sections ✅
└── utils/                 # Utility functions ✅
    ├── __init__.py
    ├── logger.py          # Centralized logging configuration ✅
    └── helpers.py         # String cleaning and data normalization utilities ✅
```

## Features Implemented

### ✅ Core Components
- **HTTP Crawler**: Rate limiting, user-agent rotation, retry logic
- **Queue Management**: Sector/company queues with progress tracking
- **Data Storage**: JSON file handling with validation
- **Modular Parsers**: Extensible parsing architecture

### ✅ Utilities
- **Text Cleaning**: Currency symbol removal, whitespace normalization
- **Data Validation**: Financial data structure validation
- **Logging**: Structured logging with file and console output
- **Path Management**: Safe file handling and directory creation

### ✅ Error Handling
- **Retry Logic**: Configurable retry attempts for failed requests
- **Rate Limiting**: Built-in delays and 429 error handling
- **Progress Tracking**: Visited sectors/companies tracking
- **Graceful Degradation**: Components work even if dependencies missing

## Pipeline Workflow

1. **Initialization**: `main.py` loads `config.py` and initializes components
2. **Sector Discovery**: Crawler fetches explore page → SectorParser extracts URLs → Saves to `sectors_queue.json`
3. **Company Discovery**: Crawler processes sectors → SectorParser extracts companies → Saves to `company_queue.json`
4. **Data Extraction**: Crawler processes companies → CompanyParser extracts all sections → Storage saves to `/companies/{name}.json`

## Usage

### Testing the Structure
```bash
python3 pipeline/test_pipeline.py
```

### Running the Pipeline
```bash
# Full pipeline (requires dependencies)
python3 pipeline/main.py --mode full --timeout 60 --max-companies 100

# Individual stages
python3 pipeline/main.py --mode sectors        # Sector discovery only
python3 pipeline/main.py --mode companies      # Company discovery only  
python3 pipeline/main.py --mode extract       # Company extraction only
```

### Dependencies Required
```bash
pip install -r requirements.txt
```

## Data Output

### Queue Files
- `pipeline/data/sectors_queue.json`: List of sector URLs
- `pipeline/data/visited_sectors.json`: Track completed sectors
- `pipeline/data/company_queue.json`: List of company URLs

### Company Data
- `companies/{Company_Name}.json`: Complete financial data including:
  - Company profile (name, stock price, ratios)
  - Financial statements (P&L, Balance Sheet, Cash Flow)
  - Quarterly data and growth metrics
  - Shareholding patterns

## Next Steps

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Test Individual Components**: Run test script to validate structure
3. **Run Full Pipeline**: Execute with `--mode full`
4. **Monitor Progress**: Check logs in `pipeline/logs/`

## Architecture Benefits

- **Modular Design**: Easy to extend with new parsers or data sources
- **Production Ready**: Built-in error handling, logging, and rate limiting
- **Maintainable**: Clear separation of concerns and clean interfaces
- **Scalable**: Can handle large datasets with proper queue management
- **Testable**: Individual components can be tested in isolation