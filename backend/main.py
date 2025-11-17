"""
FastAPI Backend for Finance Data Crawler
Provides REST API endpoints to access scraped financial data
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path
import glob
from datetime import datetime

app = FastAPI(title="Finance Data Crawler API", version="1.0.0")

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base paths
BASE_DIR = Path(__file__).parent.parent
COMPANIES_DIR = BASE_DIR / "companies"
JSON_DIR = BASE_DIR / "json"
COMPANY_QUEUE_FILE = BASE_DIR / "company_queue.json"
SECTORS_QUEUE_FILE = BASE_DIR / "sectors_queue.json"

# Pydantic models
class CompanySummary(BaseModel):
    name: str
    stock_price: Optional[str] = None
    percentage_change: Optional[str] = None
    market_cap: Optional[str] = None
    current_price: Optional[str] = None

class CompanyDetail(BaseModel):
    company_name: str
    stock_price: Optional[str] = None
    percentage_change: Optional[str] = None
    ratios: Optional[Dict[str, str]] = None
    about_and_key_points: Optional[str] = None
    company_links: Optional[List[str]] = None

class CrawlRequest(BaseModel):
    company_url: str
    priority: Optional[int] = 0

class SearchQuery(BaseModel):
    query: str

# Helper functions
def load_json_file(file_path: Path) -> Dict:
    """Load and return JSON file content"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return {}

def get_all_companies() -> List[Dict]:
    """Get all companies from the companies directory"""
    companies = []
    if COMPANIES_DIR.exists():
        for company_file in COMPANIES_DIR.glob("*.json"):
            data = load_json_file(company_file)
            if data:
                companies.append({
                    "name": company_file.stem,
                    "file": company_file.name,
                    **data
                })
    return companies

def get_company_by_name(company_name: str) -> Optional[Dict]:
    """Get company data by name"""
    company_file = COMPANIES_DIR / f"{company_name}.json"
    if company_file.exists():
        return load_json_file(company_file)
    return None

# API Routes

@app.get("/")
def read_root():
    """API health check"""
    return {
        "message": "Finance Data Crawler API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/companies", response_model=List[CompanySummary])
def get_companies():
    """Get list of all companies"""
    companies = get_all_companies()
    return [
        CompanySummary(
            name=c.get("company_name", c.get("name", "Unknown")),
            stock_price=c.get("stock_price"),
            percentage_change=c.get("percentage_change"),
            market_cap=c.get("ratios", {}).get("Market Cap") if c.get("ratios") else None,
            current_price=c.get("ratios", {}).get("Current Price") if c.get("ratios") else None
        )
        for c in companies
    ]

@app.get("/api/companies/{company_name}")
def get_company(company_name: str):
    """Get detailed information for a specific company"""
    # URL decode the company name
    company_name = company_name.replace("%20", " ")

    company_data = get_company_by_name(company_name)
    if not company_data:
        raise HTTPException(status_code=404, detail="Company not found")

    return company_data

@app.get("/api/companies/{company_name}/balance-sheet")
def get_balance_sheet(company_name: str):
    """Get balance sheet data for a company"""
    balance_sheet_data = load_json_file(JSON_DIR / "balance_sheet_data.json")
    if not balance_sheet_data:
        raise HTTPException(status_code=404, detail="Balance sheet data not found")
    return balance_sheet_data

@app.get("/api/companies/{company_name}/profit-loss")
def get_profit_loss(company_name: str):
    """Get profit & loss data for a company"""
    pl_data = load_json_file(JSON_DIR / "profit_loss_data.json")
    if not pl_data:
        raise HTTPException(status_code=404, detail="Profit & Loss data not found")
    return pl_data

@app.get("/api/companies/{company_name}/cash-flows")
def get_cash_flows(company_name: str):
    """Get cash flows data for a company"""
    cf_data = load_json_file(JSON_DIR / "cash_flows_data.json")
    if not cf_data:
        raise HTTPException(status_code=404, detail="Cash flows data not found")
    return cf_data

@app.get("/api/companies/{company_name}/quarters")
def get_quarters(company_name: str):
    """Get quarterly data for a company"""
    quarters_data = load_json_file(JSON_DIR / "quarters_data.json")
    if not quarters_data:
        raise HTTPException(status_code=404, detail="Quarters data not found")
    return quarters_data

@app.get("/api/companies/{company_name}/ratios")
def get_ratios(company_name: str):
    """Get financial ratios for a company"""
    ratios_data = load_json_file(JSON_DIR / "ratios_data.json")
    if not ratios_data:
        raise HTTPException(status_code=404, detail="Ratios data not found")
    return ratios_data

@app.get("/api/companies/{company_name}/shareholding")
def get_shareholding(company_name: str):
    """Get shareholding pattern for a company"""
    shareholding_data = load_json_file(JSON_DIR / "shareholding_data.json")
    if not shareholding_data:
        raise HTTPException(status_code=404, detail="Shareholding data not found")
    return shareholding_data

@app.get("/api/financials/latest")
def get_latest_financials():
    """Get the latest financial data from all JSON files"""
    return {
        "company": load_json_file(JSON_DIR / "company_data.json"),
        "balance_sheet": load_json_file(JSON_DIR / "balance_sheet_data.json"),
        "profit_loss": load_json_file(JSON_DIR / "profit_loss_data.json"),
        "cash_flows": load_json_file(JSON_DIR / "cash_flows_data.json"),
        "quarters": load_json_file(JSON_DIR / "quarters_data.json"),
        "ratios": load_json_file(JSON_DIR / "ratios_data.json"),
        "shareholding": load_json_file(JSON_DIR / "shareholding_data.json")
    }

@app.post("/api/search")
def search_companies(query: SearchQuery):
    """Search companies by name"""
    companies = get_all_companies()
    search_term = query.query.lower()

    results = [
        c for c in companies
        if search_term in c.get("company_name", "").lower() or
           search_term in c.get("name", "").lower()
    ]

    return results

@app.post("/api/companies/compare")
def compare_companies(company_names: List[str]):
    """Compare multiple companies"""
    comparison_data = []

    for name in company_names:
        company = get_company_by_name(name)
        if company:
            comparison_data.append(company)

    if not comparison_data:
        raise HTTPException(status_code=404, detail="No companies found for comparison")

    return comparison_data

@app.get("/api/queue/status")
def get_queue_status():
    """Get current crawler queue status"""
    company_queue = load_json_file(COMPANY_QUEUE_FILE)
    sectors_queue = load_json_file(SECTORS_QUEUE_FILE)

    return {
        "companies_in_queue": len(company_queue) if isinstance(company_queue, list) else 0,
        "sectors_in_queue": len(sectors_queue) if isinstance(sectors_queue, list) else 0,
        "total_companies_scraped": len(get_all_companies())
    }

@app.post("/api/crawl/add-company")
def add_company_to_queue(request: CrawlRequest):
    """Add a company URL to the crawl queue"""
    try:
        # Load existing queue
        queue = []
        if COMPANY_QUEUE_FILE.exists():
            queue = load_json_file(COMPANY_QUEUE_FILE)
            if not isinstance(queue, list):
                queue = []

        # Add new company URL if not already in queue
        if request.company_url not in queue:
            queue.append(request.company_url)

            # Save updated queue
            with open(COMPANY_QUEUE_FILE, 'w', encoding='utf-8') as f:
                json.dump(queue, f, indent=2)

            return {
                "message": "Company added to queue successfully",
                "url": request.company_url,
                "queue_position": len(queue)
            }
        else:
            return {
                "message": "Company already in queue",
                "url": request.company_url
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding company to queue: {str(e)}")

@app.get("/api/stats")
def get_statistics():
    """Get overall statistics"""
    companies = get_all_companies()

    # Count sectors
    sectors = set()
    for company in companies:
        if "sector" in company:
            sectors.add(company["sector"])

    return {
        "total_companies": len(companies),
        "total_sectors": len(sectors),
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
