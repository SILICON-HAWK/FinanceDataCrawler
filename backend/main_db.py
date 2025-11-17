"""
FastAPI Backend for Finance Data Crawler with PostgreSQL
"""
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import asyncio

import crud
import models
from database import engine, get_db
from websocket_manager import manager, broadcast_crawler_status

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Data Crawler API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schemas
class CompanySummary(BaseModel):
    id: int
    name: str
    stock_price: Optional[str] = None
    percentage_change: Optional[str] = None
    market_cap: Optional[str] = None

    class Config:
        from_attributes = True

class CompanyDetail(BaseModel):
    id: int
    name: str
    stock_price: Optional[str] = None
    percentage_change: Optional[str] = None
    market_cap: Optional[str] = None
    current_price: Optional[str] = None
    stock_pe: Optional[str] = None
    book_value: Optional[str] = None
    dividend_yield: Optional[str] = None
    roce: Optional[str] = None
    roe: Optional[str] = None
    about: Optional[str] = None

    class Config:
        from_attributes = True

class CrawlRequest(BaseModel):
    company_url: str
    priority: Optional[int] = 0

class SearchQuery(BaseModel):
    query: str

class BalanceSheetData(BaseModel):
    period: str
    equity_capital: Optional[float] = None
    reserves: Optional[float] = None
    borrowings: Optional[float] = None
    total_liabilities: Optional[float] = None
    fixed_assets: Optional[float] = None
    investments: Optional[float] = None
    total_assets: Optional[float] = None

    class Config:
        from_attributes = True

class ProfitLossData(BaseModel):
    period: str
    sales: Optional[float] = None
    expenses: Optional[float] = None
    operating_profit: Optional[float] = None
    opm_percent: Optional[float] = None
    net_profit: Optional[float] = None
    eps: Optional[float] = None

    class Config:
        from_attributes = True

# API Routes
@app.get("/")
def read_root():
    return {
        "message": "Finance Data Crawler API with PostgreSQL",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/api/companies", response_model=List[CompanySummary])
def get_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of all companies"""
    companies = crud.get_companies(db, skip=skip, limit=limit)
    return companies

@app.get("/api/companies/{company_name}", response_model=CompanyDetail)
def get_company(company_name: str, db: Session = Depends(get_db)):
    """Get detailed information for a specific company"""
    company = crud.get_company_by_name(db, company_name)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@app.get("/api/companies/{company_name}/balance-sheet", response_model=List[BalanceSheetData])
def get_balance_sheet(company_name: str, db: Session = Depends(get_db)):
    """Get balance sheet data for a company"""
    company = crud.get_company_by_name(db, company_name)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    balance_sheets = crud.get_balance_sheets(db, company.id)
    return balance_sheets

@app.get("/api/companies/{company_name}/profit-loss", response_model=List[ProfitLossData])
def get_profit_loss(company_name: str, db: Session = Depends(get_db)):
    """Get profit & loss data for a company"""
    company = crud.get_company_by_name(db, company_name)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    profit_loss = crud.get_profit_loss(db, company.id)
    return profit_loss

@app.get("/api/companies/{company_name}/cash-flows")
def get_cash_flows(company_name: str, db: Session = Depends(get_db)):
    """Get cash flows data for a company"""
    company = crud.get_company_by_name(db, company_name)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    cash_flows = crud.get_cash_flows(db, company.id)
    return cash_flows

@app.get("/api/companies/{company_name}/quarters")
def get_quarters(company_name: str, db: Session = Depends(get_db)):
    """Get quarterly data for a company"""
    company = crud.get_company_by_name(db, company_name)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    quarters = crud.get_quarterly_data(db, company.id)
    return quarters

@app.get("/api/companies/{company_name}/ratios")
def get_ratios(company_name: str, db: Session = Depends(get_db)):
    """Get financial ratios for a company"""
    company = crud.get_company_by_name(db, company_name)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    ratios = crud.get_financial_ratios(db, company.id)
    return ratios

@app.get("/api/companies/{company_name}/shareholding")
def get_shareholding(company_name: str, db: Session = Depends(get_db)):
    """Get shareholding pattern for a company"""
    company = crud.get_company_by_name(db, company_name)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    shareholding = crud.get_shareholding(db, company.id)
    return shareholding

@app.post("/api/search")
def search_companies(query: SearchQuery, db: Session = Depends(get_db)):
    """Search companies by name"""
    results = crud.search_companies(db, query.query)
    return results

@app.post("/api/companies/compare")
def compare_companies(company_names: List[str], db: Session = Depends(get_db)):
    """Compare multiple companies"""
    comparison_data = []

    for name in company_names:
        company = crud.get_company_by_name(db, name)
        if company:
            # Get latest financial data
            balance_sheet = crud.get_balance_sheets(db, company.id)
            profit_loss = crud.get_profit_loss(db, company.id)

            comparison_data.append({
                "company": company,
                "latest_balance_sheet": balance_sheet[0] if balance_sheet else None,
                "latest_profit_loss": profit_loss[0] if profit_loss else None
            })

    if not comparison_data:
        raise HTTPException(status_code=404, detail="No companies found for comparison")

    return comparison_data

@app.get("/api/queue/status")
def get_queue_status(db: Session = Depends(get_db)):
    """Get current crawler queue status"""
    company_queue = crud.get_queue_items(db, queue_type="company", status="pending")
    sector_queue = crud.get_queue_items(db, queue_type="sector", status="pending")

    stats = crud.get_stats(db)

    return {
        "companies_in_queue": len(company_queue),
        "sectors_in_queue": len(sector_queue),
        "total_companies_scraped": stats["total_companies"]
    }

@app.post("/api/crawl/add-company")
def add_company_to_queue(request: CrawlRequest, db: Session = Depends(get_db)):
    """Add a company URL to the crawl queue"""
    try:
        queue_item = crud.create_queue_item(
            db,
            url=request.company_url,
            queue_type="company",
            priority=request.priority
        )

        return {
            "message": "Company added to queue successfully",
            "url": request.company_url,
            "queue_id": queue_item.id,
            "status": queue_item.status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding company to queue: {str(e)}")

@app.get("/api/stats")
def get_statistics(db: Session = Depends(get_db)):
    """Get overall statistics"""
    stats = crud.get_stats(db)
    stats["last_updated"] = datetime.now().isoformat()
    return stats

@app.get("/api/sectors")
def get_sectors(db: Session = Depends(get_db)):
    """Get all sectors"""
    sectors = crud.get_sectors(db)
    return sectors

@app.get("/api/companies/filter")
def filter_companies(
    min_market_cap: Optional[float] = None,
    max_market_cap: Optional[float] = None,
    min_roe: Optional[float] = None,
    min_roce: Optional[float] = None,
    min_pe: Optional[float] = None,
    max_pe: Optional[float] = None,
    sort_by: Optional[str] = "name",
    sort_order: Optional[str] = "asc",
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Advanced filtering and sorting of companies"""
    query = db.query(models.Company)

    # Apply filters (simplified - would need proper numeric parsing in production)
    # In production, you'd parse market_cap, roe, etc. from strings to numbers

    # Sorting
    if sort_by == "name":
        query = query.order_by(models.Company.name.asc() if sort_order == "asc" else models.Company.name.desc())
    elif sort_by == "market_cap":
        query = query.order_by(models.Company.market_cap.asc() if sort_order == "asc" else models.Company.market_cap.desc())

    companies = query.limit(limit).all()
    return companies

@app.get("/api/sectors/analysis")
def sector_analysis(db: Session = Depends(get_db)):
    """Get sector-wise analysis with company counts and average metrics"""
    sectors = crud.get_sectors(db)

    sector_stats = []
    for sector in sectors:
        # Get companies in this sector (would need sector field in Company model)
        # This is a placeholder - you'd need to add sector relationships
        sector_stats.append({
            "sector_name": sector.name,
            "companies_count": sector.companies_count if hasattr(sector, 'companies_count') else 0,
            "is_visited": sector.is_visited,
            "url": sector.url
        })

    return sector_stats

@app.websocket("/ws/crawler-status")
async def websocket_crawler_status(websocket: WebSocket):
    """WebSocket endpoint for real-time crawler status updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(5)

            # Get current status from database
            db = next(get_db())
            try:
                stats = crud.get_stats(db)
                company_queue = crud.get_queue_items(db, queue_type="company", status="pending")
                processing_queue = crud.get_queue_items(db, queue_type="company", status="processing")

                status = {
                    "total_companies": stats["total_companies"],
                    "pending_in_queue": stats["pending_in_queue"],
                    "companies_in_queue": len(company_queue),
                    "currently_processing": len(processing_queue),
                    "timestamp": datetime.now().isoformat()
                }

                await websocket.send_json(status)
            finally:
                db.close()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
