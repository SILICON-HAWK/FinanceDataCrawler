"""
Finance Data Crawler
A Python application for scraping financial data from Indian stock market
"""

__version__ = "2.0.0"
__author__ = "Finance Data Crawler Team"

from .config import Config
from .crawler import FinanceCrawler
from .extractors import (
    extract_company_data,
    extract_quarters_data,
    extract_profit_loss_data,
    extract_balance_sheet_data,
    extract_cash_flows_data,
    extract_ratios_data,
    extract_shareholding_data,
    extract_all_data
)
from .storage import StorageManager, JSONStorage, DatabaseStorage
from .deduplication import DeduplicationManager
from .progress import ProgressTracker
from .validation import DataValidator

__all__ = [
    'Config',
    'FinanceCrawler',
    'StorageManager',
    'JSONStorage',
    'DatabaseStorage',
    'DeduplicationManager',
    'ProgressTracker',
    'DataValidator',
    'extract_company_data',
    'extract_quarters_data',
    'extract_profit_loss_data',
    'extract_balance_sheet_data',
    'extract_cash_flows_data',
    'extract_ratios_data',
    'extract_shareholding_data',
    'extract_all_data'
]
