# Changelog

All notable changes to the Finance Data Crawler project.

## [2.1.0] - 2024

### 🎊 Interactive Dashboard Release

#### Added

**Interactive Web Dashboard** (NEW!)
- `dashboard/` - Complete Next.js 14 application with TypeScript
- Real-time company search functionality
- Interactive financial data visualizations using Recharts
- Company comparison tool with side-by-side metrics
- Responsive design for desktop, tablet, and mobile
- Three main pages:
  - Home: Database statistics, top performers, company listing
  - Company Detail: Comprehensive financial data with charts
  - Compare: Multi-company comparison with interactive charts
- API routes for data access:
  - `/api/companies` - List all companies
  - `/api/companies/[name]` - Get company details
  - `/api/search` - Search companies
  - `/api/stats` - Database statistics

**Dashboard Features**
- Modern UI with Tailwind CSS
- Interactive quarterly performance charts
- Shareholding pattern visualization
- Profit & Loss statement displays
- Compounded growth metrics
- Top performers tracking
- Complete task 5 from original roadmap ✅

---

## [2.0.0] - 2024

### 🎉 Major Refactoring and Enhancements

#### Added

**Core Modules**
- `src/config.py` - Centralized configuration management system
- `src/crawler.py` - Main crawler engine with retry logic and rate limiting
- `src/extractors.py` - Modular data extraction functions for all financial data types
- `src/storage.py` - Dual storage system supporting JSON and SQLite database
- `src/deduplication.py` - Hash map implementation for tracking visited sectors and companies
- `src/progress.py` - Real-time progress tracking with statistics
- `src/validation.py` - Data quality validation and scoring system
- `src/main.py` - Full-featured CLI interface with multiple commands

**CLI Commands**
- `crawl` - Start crawling with timeout and limit support
- `status` - View crawler status and statistics
- `list` - List all crawled companies
- `validate` - Validate data quality
- `reset` - Reset tracking data
- `config` - Manage configuration

**Storage Features**
- SQLite database with 5 tables (companies, ratios, quarters_data, financial_statements, crawl_history)
- JSON file storage for backward compatibility
- Dual storage mode for flexibility

**Deduplication System**
- Sector-level tracking (prevents re-crawling visited sectors)
- Company-level tracking with MD5 hash map (prevents duplicate companies)
- Persistent storage of visited items
- Statistics and reporting

**Progress Tracking**
- Session-based tracking with start/end times
- Real-time statistics (sectors processed, companies processed, success rate)
- Error logging with timestamps
- Progress percentage calculation
- Resumable sessions

**Data Validation**
- Required field validation
- Data quality scoring (0-100 scale)
- Batch validation support
- Freshness checks
- Error categorization

**Configuration Management**
- Centralized config.py with all settings
- Support for custom configuration files
- Runtime configuration loading
- Config save/load functionality

**Error Handling**
- Automatic retry with exponential backoff
- HTTP 429 (rate limit) detection and handling
- Comprehensive error logging
- Graceful failure handling
- Resume capability

**Documentation**
- Complete README with usage examples
- CLI help text for all commands
- Configuration documentation
- Troubleshooting guide

#### Changed

- Refactored from Jupyter notebooks to proper Python package structure
- Improved from basic JSON storage to dual JSON+SQLite storage
- Enhanced rate limiting from simple delays to intelligent rate management
- Upgraded from sector-only tracking to full sector+company deduplication
- Transformed from manual execution to full CLI automation

#### Fixed

- Fixed encoding issues in data extraction (proper handling of special characters)
- Fixed memory leaks by properly closing database connections
- Fixed rate limit violations with configurable intervals
- Fixed data loss on errors with proper exception handling
- Fixed duplicate company crawling with hash map implementation

### Technical Improvements

**Code Organization**
- Modular package structure under `src/`
- Separation of concerns (extraction, storage, validation, etc.)
- Type hints for better code maintainability
- Comprehensive logging throughout

**Performance**
- Efficient hash-based deduplication (O(1) lookup)
- Connection pooling with requests.Session
- Lazy loading of configuration
- Optimized JSON storage with incremental writes

**Reliability**
- Retry logic for failed requests
- Timeout enforcement to prevent hanging
- Progress persistence for crash recovery
- Validation to ensure data quality

**Scalability**
- Database support for large-scale data
- Configurable batch sizes
- Memory-efficient streaming
- Extensible storage backends

### Migration Notes

For users upgrading from v1.x:

1. Install new dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Your existing JSON data in `companies/` will work as-is

3. New SQLite database will be created automatically on first run

4. Visited sectors from `visited_sectors.json` will be recognized

5. Use the new CLI interface:
   ```bash
   python run.py crawl --help
   ```

### Breaking Changes

- Removed `crawler.py` visualization script (renamed to `old_viewer.py`)
- Jupyter notebooks (notebook.ipynb, queue_manager.ipynb) are now legacy
  - All functionality moved to `src/` modules
  - Notebooks kept for reference but not maintained

### Deprecated

- Direct notebook execution (use CLI instead)
- Manual queue management (now automated)

---

## [1.0.0] - Previous Version

### Features

- Basic web scraping from screener.in
- Data extraction in Jupyter notebooks
- JSON storage
- Sector queue management
- Rate limiting (basic)
- Visited sector tracking
