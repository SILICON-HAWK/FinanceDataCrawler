"""
SQLAlchemy ORM Models for Finance Data Crawler
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    stock_price = Column(String(50))
    percentage_change = Column(String(50))
    market_cap = Column(String(100))
    current_price = Column(String(50))
    high_low = Column(String(100))
    stock_pe = Column(String(50))
    book_value = Column(String(50))
    dividend_yield = Column(String(50))
    roce = Column(String(50))
    roe = Column(String(50))
    face_value = Column(String(50))
    about = Column(Text)
    source_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    balance_sheets = relationship("BalanceSheet", back_populates="company", cascade="all, delete-orphan")
    profit_loss = relationship("ProfitLoss", back_populates="company", cascade="all, delete-orphan")
    cash_flows = relationship("CashFlow", back_populates="company", cascade="all, delete-orphan")
    quarters = relationship("QuarterlyData", back_populates="company", cascade="all, delete-orphan")
    ratios = relationship("FinancialRatio", back_populates="company", cascade="all, delete-orphan")
    shareholding = relationship("Shareholding", back_populates="company", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_company_name', 'name'),
    )


class BalanceSheet(Base):
    __tablename__ = "balance_sheets"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period = Column(String(50), nullable=False)  # e.g., "Mar 2024"
    equity_capital = Column(Numeric(20, 2))
    reserves = Column(Numeric(20, 2))
    borrowings = Column(Numeric(20, 2))
    other_liabilities = Column(Numeric(20, 2))
    total_liabilities = Column(Numeric(20, 2))
    fixed_assets = Column(Numeric(20, 2))
    cwip = Column(Numeric(20, 2))  # Capital Work in Progress
    investments = Column(Numeric(20, 2))
    other_assets = Column(Numeric(20, 2))
    total_assets = Column(Numeric(20, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="balance_sheets")

    __table_args__ = (
        Index('idx_balance_sheet_company_period', 'company_id', 'period'),
    )


class ProfitLoss(Base):
    __tablename__ = "profit_loss"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period = Column(String(50), nullable=False)
    sales = Column(Numeric(20, 2))
    expenses = Column(Numeric(20, 2))
    operating_profit = Column(Numeric(20, 2))
    opm_percent = Column(Numeric(10, 2))  # Operating Profit Margin
    other_income = Column(Numeric(20, 2))
    interest = Column(Numeric(20, 2))
    depreciation = Column(Numeric(20, 2))
    profit_before_tax = Column(Numeric(20, 2))
    tax = Column(Numeric(20, 2))
    net_profit = Column(Numeric(20, 2))
    eps = Column(Numeric(10, 2))  # Earnings Per Share
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="profit_loss")

    __table_args__ = (
        Index('idx_profit_loss_company_period', 'company_id', 'period'),
    )


class CashFlow(Base):
    __tablename__ = "cash_flows"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period = Column(String(50), nullable=False)
    operating_activities = Column(Numeric(20, 2))
    investing_activities = Column(Numeric(20, 2))
    financing_activities = Column(Numeric(20, 2))
    net_cash_flow = Column(Numeric(20, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="cash_flows")

    __table_args__ = (
        Index('idx_cash_flow_company_period', 'company_id', 'period'),
    )


class QuarterlyData(Base):
    __tablename__ = "quarterly_data"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    quarter = Column(String(50), nullable=False)  # e.g., "Sep 2024"
    sales = Column(Numeric(20, 2))
    expenses = Column(Numeric(20, 2))
    operating_profit = Column(Numeric(20, 2))
    opm_percent = Column(Numeric(10, 2))
    other_income = Column(Numeric(20, 2))
    interest = Column(Numeric(20, 2))
    depreciation = Column(Numeric(20, 2))
    profit_before_tax = Column(Numeric(20, 2))
    tax = Column(Numeric(20, 2))
    net_profit = Column(Numeric(20, 2))
    eps = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="quarters")

    __table_args__ = (
        Index('idx_quarterly_company_quarter', 'company_id', 'quarter'),
    )


class FinancialRatio(Base):
    __tablename__ = "financial_ratios"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period = Column(String(50), nullable=False)
    debtor_days = Column(Numeric(10, 2))
    inventory_days = Column(Numeric(10, 2))
    days_payable = Column(Numeric(10, 2))
    cash_conversion_cycle = Column(Numeric(10, 2))
    working_capital_days = Column(Numeric(10, 2))
    roce_percent = Column(Numeric(10, 2))  # Return on Capital Employed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="ratios")

    __table_args__ = (
        Index('idx_ratios_company_period', 'company_id', 'period'),
    )


class Shareholding(Base):
    __tablename__ = "shareholding"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period = Column(String(50), nullable=False)
    promoters = Column(Numeric(10, 2))
    fii = Column(Numeric(10, 2))  # Foreign Institutional Investors
    dii = Column(Numeric(10, 2))  # Domestic Institutional Investors
    government = Column(Numeric(10, 2))
    public = Column(Numeric(10, 2))
    others = Column(Numeric(10, 2))
    total_shareholders = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="shareholding")

    __table_args__ = (
        Index('idx_shareholding_company_period', 'company_id', 'period'),
    )


class CrawlQueue(Base):
    __tablename__ = "crawl_queue"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, nullable=False)
    queue_type = Column(String(50), nullable=False)  # 'company' or 'sector'
    priority = Column(Integer, default=0)
    status = Column(String(50), default='pending')  # pending, processing, completed, failed
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_queue_status', 'status'),
        Index('idx_queue_type', 'queue_type'),
    )


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    url = Column(String(500))
    companies_count = Column(Integer, default=0)
    is_visited = Column(Integer, default=0)  # 0 or 1 for boolean
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_sector_name', 'name'),
    )
