# Finance Data Dashboard

A modern, interactive Next.js dashboard for visualizing financial data from Indian stock market companies.

## Features

- 🔍 **Company Search** - Fast, real-time search across all companies
- 📊 **Interactive Charts** - Visualize quarterly performance, P&L statements, and more
- 🔄 **Company Comparison** - Compare multiple companies side-by-side
- 📈 **Top Performers** - See companies with highest positive changes
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile
- ⚡ **Fast Performance** - Built with Next.js 14 and optimized for speed

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Database**: SQLite (via better-sqlite3)
- **Icons**: Lucide React

## Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Finance Data Crawler database (`finance_data.db` in parent directory)

## Installation

1. Navigate to the dashboard directory:
```bash
cd dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Ensure the database file exists:
```bash
# The dashboard expects the database at ../finance_data.db
# Run the crawler first to generate data:
cd ..
python run.py crawl --limit 10
```

## Development

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Building for Production

Build the application:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

## Project Structure

```
dashboard/
├── src/
│   ├── app/
│   │   ├── api/              # API routes
│   │   │   ├── companies/    # Company data endpoints
│   │   │   ├── search/       # Search endpoint
│   │   │   └── stats/        # Statistics endpoint
│   │   ├── company/[name]/   # Company detail page
│   │   ├── compare/          # Company comparison page
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Home page
│   │   └── globals.css       # Global styles
│   ├── components/           # Reusable components
│   │   ├── SearchBar.tsx
│   │   ├── StatsCard.tsx
│   │   └── QuarterlyChart.tsx
│   └── lib/                  # Utilities
│       ├── db.ts             # Database functions
│       └── utils.ts          # Helper functions
├── public/                   # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## API Routes

### GET `/api/companies`
Get all companies in the database.

**Response:**
```json
[
  {
    "id": 1,
    "company_name": "Company Name",
    "stock_price": "1,234 INR",
    "percentage_change": "+2.5%",
    "market_cap": "10,000 Cr. INR",
    ...
  }
]
```

### GET `/api/companies/[name]`
Get detailed information for a specific company.

**Response:**
```json
{
  "company_name": "Company Name",
  "stock_price": "1,234 INR",
  "ratios": [...],
  "financial_data": {
    "quarters_data": {...},
    "profit_loss_data": {...},
    ...
  }
}
```

### GET `/api/search?q=query`
Search for companies by name.

**Query Parameters:**
- `q` - Search query (minimum 2 characters)

**Response:**
```json
[
  {
    "company_name": "Matching Company",
    "stock_price": "1,234 INR",
    "percentage_change": "+1.2%"
  }
]
```

### GET `/api/stats`
Get database statistics and top performers.

**Response:**
```json
{
  "totalCompanies": 100,
  "successfulCrawls": 95,
  "failedCrawls": 5,
  "recentCompanies": [...],
  "topPerformers": [...]
}
```

## Features in Detail

### Home Page (`/`)
- Overview statistics (total companies, crawl success rate, etc.)
- Top performers list
- Full company listing with clickable rows
- Global search bar

### Company Detail Page (`/company/[name]`)
- Company overview with current stock price and change %
- Key financial ratios in a grid layout
- Quarterly performance chart
- Shareholding pattern (quarterly and yearly)
- Profit & Loss statement
- Compounded growth metrics

### Comparison Page (`/compare`)
- Add multiple companies to compare
- Side-by-side metric comparison
- Interactive bar chart visualization
- Detailed comparison table

## Database Schema

The dashboard reads from these SQLite tables:

- `companies` - Basic company information
- `ratios` - Financial ratios
- `financial_statements` - JSON-stored financial data
- `crawl_history` - Crawl attempt logs

## Customization

### Colors & Styling

Edit `tailwind.config.ts` and `src/app/globals.css` to customize the theme.

### Chart Configuration

Modify `src/components/QuarterlyChart.tsx` to customize chart appearance and metrics.

### Add New Pages

Create new routes in `src/app/` following the Next.js App Router convention.

## Troubleshooting

### Database not found

**Error**: `Error: ENOENT: no such file or directory, open '../finance_data.db'`

**Solution**: Run the crawler first to generate the database:
```bash
cd ..
python run.py crawl --limit 5
```

### Build errors with better-sqlite3

**Error**: Module errors with `better-sqlite3`

**Solution**:
1. Delete `node_modules` and package-lock.json
2. Run `npm install` again
3. Ensure you're using Node.js 18+

### No data showing

**Solution**:
1. Verify database has data: `sqlite3 ../finance_data.db "SELECT COUNT(*) FROM companies;"`
2. Check console for API errors
3. Ensure API routes are working: Visit `http://localhost:3000/api/companies`

## Performance Optimization

The dashboard includes several optimizations:

- Server-side data fetching with Next.js API routes
- Client-side caching of search results
- Lazy loading of charts
- Responsive images and icons
- Minimal bundle size with tree-shaking

## Contributing

To add new features:

1. Create a new branch
2. Add your feature in the appropriate directory
3. Test thoroughly
4. Submit a pull request

## License

Same as the Finance Data Crawler project.

## Support

For issues specific to the dashboard:
- Check the console for JavaScript errors
- Verify the database path is correct
- Ensure all dependencies are installed
- Check Node.js version (18+ required)

For data-related issues:
- Run the crawler's validation: `python run.py validate`
- Check crawler logs: `logs/crawler.log`

---

**Version**: 1.0.0
**Built with**: Next.js 14, TypeScript, and Tailwind CSS
