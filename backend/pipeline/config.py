"""
Configuration settings for the Finance Data Crawler Pipeline.
"""

import os
from pathlib import Path

# Base URLs
BASE_URL = "https://www.screener.in"
EXPLORE_URL = f"{BASE_URL}/explore/"

# User-Agent rotation for request headers
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
]

# Rate limiting configuration
REQUEST_DELAY = 15  # seconds between requests
MAX_RETRIES = 3  # max retry attempts for failed requests
REQUEST_TIMEOUT = 10  # timeout per request in seconds

# File paths
# When running from backend/, __file__ is at backend/pipeline/config.py
# so parent.parent resolves to backend/
BACKEND_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent
DATA_DIR = BACKEND_ROOT / "data"
SECTORS_QUEUE_FILE = DATA_DIR / "sectors_queue.json"
COMPANY_QUEUE_FILE = DATA_DIR / "company_queue.json"
VISITED_SECTORS_FILE = DATA_DIR / "visited_sectors.json"
COMPANIES_DIR = PROJECT_ROOT / "companies"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
COMPANIES_DIR.mkdir(exist_ok=True)

# HTML parsing constants
SECTOR_LINK_SELECTOR = 'a.bordered.radius-6.padding-4-12.font-size-14.ink-700'
COMPANY_LINK_SELECTOR = 'a[target="_blank"]'

# Company data section IDs
SECTION_IDS = {
    'company_info': 'top',
    'quarters': 'quarters',
    'profit_loss': 'profit-loss',
    'balance_sheet': 'balance-sheet',
    'cash_flow': 'cash-flow',
    'ratios': 'ratios',
    'shareholding': 'shareholding'
}

# Log configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = BACKEND_ROOT / 'pipeline' / 'logs' / 'crawler.log'
LOG_DIR = LOG_FILE.parent
LOG_DIR.mkdir(exist_ok=True)

# Data cleaning constants
CURRENCY_SYMBOLS = ['₹', '¹', 'â‚', 'Â']
ENCODING_ERRORS = 'ignore'
SPACE_CHARS = ['\n', '\t', ' ', '\u00a0']
SPECIAL_CHARS = ['+', '-', '<span class="blue-icon">', '</span>']