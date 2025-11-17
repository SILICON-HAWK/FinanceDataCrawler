"""
CRUD operations for database models
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
import models

# Company CRUD
def get_company(db: Session, company_id: int):
    return db.query(models.Company).filter(models.Company.id == company_id).first()

def get_company_by_name(db: Session, name: str):
    return db.query(models.Company).filter(models.Company.name == name).first()

def get_companies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Company).offset(skip).limit(limit).all()

def create_company(db: Session, company_data: dict):
    db_company = models.Company(**company_data)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def update_company(db: Session, company_id: int, company_data: dict):
    db_company = get_company(db, company_id)
    if db_company:
        for key, value in company_data.items():
            setattr(db_company, key, value)
        db.commit()
        db.refresh(db_company)
    return db_company

def search_companies(db: Session, query: str):
    return db.query(models.Company).filter(
        models.Company.name.ilike(f"%{query}%")
    ).all()

# Balance Sheet CRUD
def get_balance_sheets(db: Session, company_id: int):
    return db.query(models.BalanceSheet).filter(
        models.BalanceSheet.company_id == company_id
    ).order_by(models.BalanceSheet.period.desc()).all()

def create_balance_sheet(db: Session, company_id: int, data: dict):
    db_bs = models.BalanceSheet(company_id=company_id, **data)
    db.add(db_bs)
    db.commit()
    db.refresh(db_bs)
    return db_bs

# Profit & Loss CRUD
def get_profit_loss(db: Session, company_id: int):
    return db.query(models.ProfitLoss).filter(
        models.ProfitLoss.company_id == company_id
    ).order_by(models.ProfitLoss.period.desc()).all()

def create_profit_loss(db: Session, company_id: int, data: dict):
    db_pl = models.ProfitLoss(company_id=company_id, **data)
    db.add(db_pl)
    db.commit()
    db.refresh(db_pl)
    return db_pl

# Cash Flow CRUD
def get_cash_flows(db: Session, company_id: int):
    return db.query(models.CashFlow).filter(
        models.CashFlow.company_id == company_id
    ).order_by(models.CashFlow.period.desc()).all()

def create_cash_flow(db: Session, company_id: int, data: dict):
    db_cf = models.CashFlow(company_id=company_id, **data)
    db.add(db_cf)
    db.commit()
    db.refresh(db_cf)
    return db_cf

# Quarterly Data CRUD
def get_quarterly_data(db: Session, company_id: int):
    return db.query(models.QuarterlyData).filter(
        models.QuarterlyData.company_id == company_id
    ).order_by(models.QuarterlyData.quarter.desc()).all()

def create_quarterly_data(db: Session, company_id: int, data: dict):
    db_qd = models.QuarterlyData(company_id=company_id, **data)
    db.add(db_qd)
    db.commit()
    db.refresh(db_qd)
    return db_qd

# Financial Ratios CRUD
def get_financial_ratios(db: Session, company_id: int):
    return db.query(models.FinancialRatio).filter(
        models.FinancialRatio.company_id == company_id
    ).order_by(models.FinancialRatio.period.desc()).all()

def create_financial_ratio(db: Session, company_id: int, data: dict):
    db_fr = models.FinancialRatio(company_id=company_id, **data)
    db.add(db_fr)
    db.commit()
    db.refresh(db_fr)
    return db_fr

# Shareholding CRUD
def get_shareholding(db: Session, company_id: int):
    return db.query(models.Shareholding).filter(
        models.Shareholding.company_id == company_id
    ).order_by(models.Shareholding.period.desc()).all()

def create_shareholding(db: Session, company_id: int, data: dict):
    db_sh = models.Shareholding(company_id=company_id, **data)
    db.add(db_sh)
    db.commit()
    db.refresh(db_sh)
    return db_sh

# Crawl Queue CRUD
def get_queue_items(db: Session, queue_type: Optional[str] = None, status: Optional[str] = None):
    query = db.query(models.CrawlQueue)
    if queue_type:
        query = query.filter(models.CrawlQueue.queue_type == queue_type)
    if status:
        query = query.filter(models.CrawlQueue.status == status)
    return query.order_by(models.CrawlQueue.priority.desc(), models.CrawlQueue.created_at).all()

def create_queue_item(db: Session, url: str, queue_type: str, priority: int = 0):
    # Check if already exists
    existing = db.query(models.CrawlQueue).filter(models.CrawlQueue.url == url).first()
    if existing:
        return existing

    db_queue = models.CrawlQueue(url=url, queue_type=queue_type, priority=priority)
    db.add(db_queue)
    db.commit()
    db.refresh(db_queue)
    return db_queue

def update_queue_status(db: Session, queue_id: int, status: str, error_message: Optional[str] = None):
    db_queue = db.query(models.CrawlQueue).filter(models.CrawlQueue.id == queue_id).first()
    if db_queue:
        db_queue.status = status
        if error_message:
            db_queue.error_message = error_message
        db.commit()
        db.refresh(db_queue)
    return db_queue

# Sector CRUD
def get_sectors(db: Session):
    return db.query(models.Sector).all()

def create_sector(db: Session, name: str, url: str):
    db_sector = models.Sector(name=name, url=url)
    db.add(db_sector)
    db.commit()
    db.refresh(db_sector)
    return db_sector

# Statistics
def get_stats(db: Session):
    total_companies = db.query(func.count(models.Company.id)).scalar()
    total_sectors = db.query(func.count(models.Sector.id)).scalar()
    pending_queue = db.query(func.count(models.CrawlQueue.id)).filter(
        models.CrawlQueue.status == 'pending'
    ).scalar()

    return {
        "total_companies": total_companies,
        "total_sectors": total_sectors,
        "pending_in_queue": pending_queue
    }
