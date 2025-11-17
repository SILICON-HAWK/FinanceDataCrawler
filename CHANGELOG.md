# Changelog

All notable changes to the Finance Data Crawler project.

## [3.0.0] - 2025-01-17

### 🎉 Production-Ready Full-Stack Release

#### Added

**Complete Full-Stack Application**
- Production-ready Docker setup with one-command deployment
- FastAPI backend with PostgreSQL integration
- Next.js 14 frontend with TypeScript and modern UI
- Real-time WebSocket monitoring
- Comprehensive documentation

**Backend (FastAPI + PostgreSQL)**
- `backend/main_db.py` - Full REST API with SQLAlchemy ORM
- `backend/models.py` - Complete database schema (8 tables)
- `backend/crud.py` - CRUD operations for all entities
- `backend/websocket_manager.py` - Real-time status updates
- `backend/migrate_json_to_db.py` - JSON to PostgreSQL migration
- Dual storage: JSON files + PostgreSQL database
- WebSocket endpoint for live crawler monitoring
- Advanced filtering and sorting API
- Sector-wise analysis endpoint
- Company comparison API

**Frontend (Next.js 14 + TypeScript)**
- `frontend-nextjs/` - Modern Next.js application with App Router
- Dashboard page with real-time status monitoring
- Company detail pages with interactive financial charts
- Multi-company comparison tool with visualizations
- Sector analysis page showing all 86 sectors
- Add company to queue interface
- Search functionality with live results
- Responsive design for all screen sizes
- Real-time WebSocket integration
- TanStack Query for data management
- Recharts for financial visualizations
- Tailwind CSS for modern styling

**CLI Interface**
- `src/cli.py` - Comprehensive command-line interface
- `run.py` - Main CLI entry point
- Commands:
  - `status` - Show crawler statistics
  - `list` - List all companies
  - `validate` - Data quality validation
  - `reset` - Reset tracking data
  - `config` - Configuration management
  - `info` - Company information lookup

**Modular Python Structure**
- `src/config.py` - Centralized configuration management
- `src/validation.py` - Data validation and quality scoring
- Supports both SQLite and PostgreSQL
- Environment-based configuration
- User agent rotation
- Quality score calculation

**Docker & DevOps**
- `docker-compose.yml` - Orchestration for 3 services
- `backend/Dockerfile` - Backend container with entrypoint
- `frontend-nextjs/Dockerfile` - Frontend container
- `backend/entrypoint.sh` - Auto-setup and migration
- `setup.sh` - One-command deployment script
- `Makefile` - Quick commands for common operations
- Health checks for all services
- Auto-restart policies
- Data persistence via volumes

**Real-time Features**
- WebSocket status monitoring (updates every 5 seconds)
- Live connection indicator
- Auto-reconnection on disconnect
- Processing status tracking
- Queue monitoring

**Advanced Features**
- Advanced filtering by financial metrics
- Sort by multiple fields (market cap, ROE, ROCE, etc.)
- Sector-wise analysis with visit tracking
- Company comparison with interactive charts
- Search with live results
- Data validation with quality scores

**Documentation**
- `README.md` - Complete project documentation
- `QUICKSTART.md` - 2-minute setup guide
- `DOCKER_GUIDE.md` - Comprehensive Docker reference
- `FEATURES.md` - Advanced features documentation
- `CHANGELOG.md` - Version history
- API documentation via FastAPI /docs
- ASCII architecture diagrams
- Data flow diagrams

**Database Schema**
- `companies` - Company master data with indexes
- `balance_sheets` - Historical balance sheet data
- `profit_loss` - P&L statements over time
- `cash_flows` - Cash flow statements
- `quarterly_data` - Quarterly financial results
- `financial_ratios` - Financial ratios and metrics
- `shareholding` - Shareholding patterns
- `crawl_queue` - Queue management with priorities
- `sectors` - Sector tracking and analysis
- `price_history` - Historical price data (schema ready)

**API Endpoints**
- GET `/api/companies` - List all companies
- GET `/api/companies/{name}` - Company details
- GET `/api/companies/{name}/balance-sheet` - Balance sheet
- GET `/api/companies/{name}/profit-loss` - P&L data
- GET `/api/companies/{name}/quarters` - Quarterly data
- GET `/api/companies/{name}/ratios` - Financial ratios
- GET `/api/companies/{name}/shareholding` - Shareholding
- POST `/api/search` - Search companies
- POST `/api/companies/compare` - Compare companies
- GET `/api/companies/filter` - Advanced filtering
- GET `/api/sectors/analysis` - Sector statistics
- POST `/api/crawl/add-company` - Add to queue
- GET `/api/queue/status` - Queue status
- GET `/api/stats` - Overall statistics
- WS `/ws/crawler-status` - Real-time updates

#### Changed

- Upgraded from basic Jupyter notebooks to production application
- Migrated from JSON-only to dual JSON+PostgreSQL storage
- Enhanced from manual execution to Docker automation
- Improved from static pages to real-time monitoring
- Modernized UI from basic HTML to Next.js 14 + TypeScript
- Upgraded data storage to indexed PostgreSQL database

#### Fixed

- Proper CORS configuration for frontend-backend communication
- Database connection pooling and session management
- WebSocket connection stability with auto-reconnection
- Data migration handling with duplicate detection
- Path handling for Docker volumes
- Environment variable configuration
- Health check reliability

### Technical Improvements

**Architecture**
- Microservices architecture with 3 containers
- Docker network isolation
- RESTful API design
- WebSocket for real-time updates
- Client-side caching with React Query
- Server-side rendering with Next.js

**Performance**
- Database indexing on all critical queries
- Connection pooling for PostgreSQL
- React Query caching strategy
- Lazy loading of components
- Optimized Docker images
- Health-based service dependencies

**Security**
- Docker network isolation
- Environment variable secrets
- SQL injection protection via ORM
- CORS configuration
- Input validation
- Prepared statements

**Scalability**
- Horizontal scaling ready
- Database connection pooling
- Stateless API design
- Volume-based data persistence
- Configurable resource limits

**Developer Experience**
- One-command setup (`./setup.sh`)
- Hot reload for both frontend and backend
- Comprehensive logging
- API documentation at `/docs`
- TypeScript type safety
- Modular code structure

### Migration Notes

For users upgrading from v2.x:

1. **New Docker Setup**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **PostgreSQL Database**
   - Automatic migration from JSON files
   - Run migration: `docker-compose exec backend python migrate_json_to_db.py`

3. **New Frontend**
   - Access at http://localhost:3000
   - Old dashboard moved to `dashboard/` (archived)
   - New frontend in `frontend-nextjs/`

4. **CLI Commands**
   ```bash
   python run.py status
   python run.py list
   python run.py validate
   python run.py info "Company Name"
   ```

5. **Environment Variables**
   - Backend: `backend/.env`
   - Frontend: `frontend-nextjs/.env.local`
   - See `.env.example` files

### Breaking Changes

- Removed old `dashboard/` directory (replaced with `frontend-nextjs/`)
- API now requires PostgreSQL (SQLite optional via config)
- Changed API base URL to `/api/*` prefix
- WebSocket endpoint for real-time updates

### Deprecated

- Old Next.js dashboard in `dashboard/` (archived)
- Direct JSON file access (use API instead)
- Manual database management (automated now)

---

## [2.1.0] - 2024

### 🎊 Interactive Dashboard Release

#### Added

**Interactive Web Dashboard**
- `dashboard/` - Next.js 14 application
- Real-time company search
- Financial data visualizations
- Company comparison tool
- Responsive design
- API routes for data access

---

## [2.0.0] - 2024

### 🎉 Major Refactoring and Enhancements

#### Added

**Core Modules**
- Modular Python package structure
- SQLite database support
- CLI interface with commands
- Data validation system
- Progress tracking
- Configuration management

---

## [1.0.0] - 2024

### Features

- Basic web scraping from screener.in
- Data extraction in Jupyter notebooks
- JSON storage
- Queue management
- Rate limiting

---

**Note**: For detailed API documentation, visit http://localhost:8000/docs after starting the application.
