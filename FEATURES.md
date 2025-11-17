# Advanced Features Documentation

This document describes the advanced features implemented in the Finance Data Crawler.

## 🔴 Real-time Crawler Status Monitoring

### Overview
WebSocket-based real-time monitoring of the crawler's status, providing live updates without page refresh.

### Implementation

**Backend (FastAPI WebSocket):**
```python
@app.websocket("/ws/crawler-status")
async def websocket_crawler_status(websocket: WebSocket):
    # Establishes WebSocket connection
    # Sends periodic status updates every 5 seconds
    # Includes: total companies, queue status, currently processing
```

**Frontend (React Component):**
```tsx
<CrawlerStatusMonitor />
// Automatically connects to WebSocket
// Displays live status with visual indicators
// Auto-reconnects on disconnect
```

### Features
- ✅ Live connection status indicator
- ✅ Real-time queue monitoring
- ✅ Currently processing items count
- ✅ Auto-reconnection on disconnect
- ✅ Visual processing indicator (pulsing dot)
- ✅ Last update timestamp

### Usage
Simply include the `<CrawlerStatusMonitor />` component in any page:

```tsx
import CrawlerStatusMonitor from '@/components/CrawlerStatusMonitor'

export default function Dashboard() {
  return (
    <div>
      <CrawlerStatusMonitor />
      {/* rest of your components */}
    </div>
  )
}
```

### WebSocket Endpoint
```
ws://localhost:8000/ws/crawler-status
```

### Status Updates Format
```json
{
  "total_companies": 25,
  "pending_in_queue": 10,
  "companies_in_queue": 10,
  "currently_processing": 2,
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

---

## 🔍 Advanced Filtering and Sorting

### Overview
Powerful filtering capabilities to find companies based on financial metrics.

### API Endpoint
```
GET /api/companies/filter
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_market_cap` | float | Minimum market capitalization |
| `max_market_cap` | float | Maximum market capitalization |
| `min_roe` | float | Minimum Return on Equity (%) |
| `min_roce` | float | Minimum Return on Capital Employed (%) |
| `min_pe` | float | Minimum P/E ratio |
| `max_pe` | float | Maximum P/E ratio |
| `sort_by` | string | Field to sort by: `name`, `market_cap`, `roe`, `roce` |
| `sort_order` | string | Sort order: `asc` or `desc` |
| `limit` | int | Maximum results (default: 100) |

### Example Requests

**Find high ROE companies:**
```bash
curl "http://localhost:8000/api/companies/filter?min_roe=20&sort_by=roe&sort_order=desc"
```

**Find companies by market cap range:**
```bash
curl "http://localhost:8000/api/companies/filter?min_market_cap=1000&max_market_cap=50000"
```

**Find value stocks (low P/E):**
```bash
curl "http://localhost:8000/api/companies/filter?max_pe=15&min_roe=15"
```

### Frontend Integration

Add a filter panel to your dashboard:

```tsx
const [filters, setFilters] = useState({
  min_roe: '',
  min_roce: '',
  sort_by: 'name'
})

const { data: filteredCompanies } = useQuery({
  queryKey: ['companies', 'filtered', filters],
  queryFn: () => axios.get('/api/companies/filter', { params: filters })
})
```

---

## 📊 Sector-wise Analysis

### Overview
View and analyze companies grouped by industry sectors, with visit tracking and statistics.

### Page Route
```
http://localhost:3000/sectors
```

### API Endpoint
```
GET /api/sectors/analysis
```

### Features
- ✅ View all sectors (86 total from Screener.in)
- ✅ See visited vs unvisited sectors
- ✅ Company count per sector
- ✅ Direct links to Screener.in sector pages
- ✅ Visual status indicators
- ✅ Statistics: Total sectors, visited sectors, total companies

### Response Format
```json
[
  {
    "sector_name": "Pharmaceuticals",
    "companies_count": 15,
    "is_visited": 1,
    "url": "https://www.screener.in/screens/..."
  },
  {
    "sector_name": "IT Services",
    "companies_count": 0,
    "is_visited": 0,
    "url": "https://www.screener.in/screens/..."
  }
]
```

### Database Schema
```sql
CREATE TABLE sectors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    url VARCHAR(500),
    companies_count INTEGER DEFAULT 0,
    is_visited INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_sector_name ON sectors(name);
```

### Use Cases
- **Investment Research**: Find sectors with high company counts
- **Crawler Planning**: See which sectors haven't been visited
- **Market Analysis**: Understand sector distribution
- **Portfolio Diversification**: Select companies from different sectors

---

## 📈 Historical Price Tracking (Coming Soon)

### Overview
Track and visualize historical stock prices over time.

### Database Schema (Ready to Use)
```python
class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    date = Column(DateTime)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
```

### Planned Features
- ✅ Store daily OHLC (Open, High, Low, Close) data
- ✅ Track trading volume
- ✅ Index by company and date for fast queries
- 🔲 API endpoint to fetch price history
- 🔲 Interactive line charts with zoom
- 🔲 Time range selectors (1M, 3M, 6M, 1Y, 5Y, ALL)
- 🔲 Technical indicators (SMA, EMA, RSI)
- 🔲 Compare multiple stock prices
- 🔲 Export to CSV

### API Endpoint (Planned)
```
GET /api/companies/{name}/price-history?start_date=2023-01-01&end_date=2024-01-01
```

### Usage Example (Planned)
```tsx
const { data: priceHistory } = useQuery({
  queryKey: ['priceHistory', companyName, dateRange],
  queryFn: () => getPriceHistory(companyName, dateRange)
})

return (
  <LineChart data={priceHistory}>
    <Line dataKey="close_price" stroke="#3b82f6" />
  </LineChart>
)
```

---

## 🔌 GraphQL API Integration (Optional)

### Overview
Add GraphQL support for more flexible data querying using Hasura or Strawberry GraphQL.

### Option 1: Hasura (Recommended)

**Advantages:**
- Instant GraphQL API from PostgreSQL
- Real-time subscriptions
- Fine-grained access control
- Automatic relationship mapping

**Setup:**
```bash
# Add Hasura to docker-compose.yml
hasura:
  image: hasura/graphql-engine:latest
  ports:
    - "8080:8080"
  environment:
    HASURA_GRAPHQL_DATABASE_URL: postgresql://finance_user:finance_pass@postgres:5432/finance_crawler
    HASURA_GRAPHQL_ENABLE_CONSOLE: "true"
```

**Example Query:**
```graphql
query GetCompanyWithFinancials {
  companies(where: {name: {_eq: "Sun Pharma"}}) {
    id
    name
    stock_price
    market_cap
    balance_sheets(order_by: {period: desc}, limit: 5) {
      period
      total_assets
      total_liabilities
    }
    profit_loss(order_by: {period: desc}, limit: 5) {
      period
      sales
      net_profit
    }
  }
}
```

**Subscription Example:**
```graphql
subscription CrawlerStatus {
  crawl_queue(where: {status: {_eq: "processing"}}) {
    id
    url
    status
    updated_at
  }
}
```

### Option 2: Strawberry GraphQL (Python)

**Advantages:**
- Integrates directly with FastAPI
- Type-safe with Python type hints
- More control over resolvers

**Installation:**
```bash
pip install strawberry-graphql[fastapi]
```

**Example Schema:**
```python
import strawberry
from typing import List

@strawberry.type
class Company:
    id: int
    name: str
    stock_price: str
    market_cap: str

@strawberry.type
class Query:
    @strawberry.field
    def companies(self) -> List[Company]:
        # Your resolver logic
        pass

schema = strawberry.Schema(query=Query)
app.add_route("/graphql", GraphQLRouter(schema))
```

---

## 🚀 Performance Optimizations

### Database Indexing
All critical queries are optimized with indexes:

```sql
-- Company name searches
CREATE INDEX idx_company_name ON companies(name);

-- Financial data time-series queries
CREATE INDEX idx_balance_sheet_company_period ON balance_sheets(company_id, period);
CREATE INDEX idx_profit_loss_company_period ON profit_loss(company_id, period);
CREATE INDEX idx_price_history_company_date ON price_history(company_id, date);

-- Queue status queries
CREATE INDEX idx_queue_status ON crawl_queue(status);
CREATE INDEX idx_queue_type ON crawl_queue(queue_type);
```

### Caching Strategy

**Frontend (React Query):**
- Stale time: 60 seconds
- Cache time: 5 minutes
- Automatic background refetch
- Optimistic updates

**Backend (Planned):**
- Redis for frequently accessed data
- API response caching
- Query result caching

---

## 📱 Mobile Responsiveness

All features are fully responsive:
- ✅ Adaptive grid layouts
- ✅ Touch-friendly controls
- ✅ Mobile-optimized charts
- ✅ Collapsible sidebars
- ✅ Swipe gestures support

---

## 🔒 Security Features

### Current
- ✅ CORS configuration
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Environment variable secrets
- ✅ Docker network isolation

### Recommended (Production)
- 🔲 JWT authentication
- 🔲 Rate limiting
- 🔲 API key management
- 🔲 HTTPS/SSL certificates
- 🔲 Input validation and sanitization
- 🔲 DDoS protection
- 🔲 Database connection pooling

---

## 📊 Monitoring & Logging

### Current
- ✅ WebSocket connection monitoring
- ✅ Console logging
- ✅ Docker logs

### Planned
- 🔲 Prometheus metrics
- 🔲 Grafana dashboards
- 🔲 Error tracking (Sentry)
- 🔲 Performance monitoring (New Relic/DataDog)
- 🔲 Audit logs
- 🔲 User activity tracking

---

## 🧪 Testing

### Recommended Testing Stack
```bash
# Backend
pip install pytest pytest-asyncio httpx

# Frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

### Test Coverage Goals
- Unit tests: 80%+
- Integration tests: Key user flows
- E2E tests: Critical paths
- Performance tests: Load testing

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [React Query Documentation](https://tanstack.com/query/latest)
- [Recharts Documentation](https://recharts.org/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

---

## 🎯 Future Roadmap

### Phase 1 (Current)
- ✅ Real-time monitoring
- ✅ Advanced filtering
- ✅ Sector analysis
- ✅ Basic infrastructure

### Phase 2 (Next 2-3 months)
- 🔲 Historical price tracking
- 🔲 Technical indicators
- 🔲 Portfolio tracking
- 🔲 Email alerts
- 🔲 Export functionality

### Phase 3 (6+ months)
- 🔲 Machine learning predictions
- 🔲 Sentiment analysis
- 🔲 News integration
- 🔲 Mobile app
- 🔲 Premium features

---

## 💡 Contributing

To add new features:

1. **Backend**: Add endpoint in `backend/main_db.py`
2. **Database**: Update models in `backend/models.py`
3. **Frontend**: Create page in `frontend-nextjs/src/app/`
4. **API Client**: Add function in `frontend-nextjs/src/lib/api.ts`
5. **Documentation**: Update this file

Happy coding! 🚀
