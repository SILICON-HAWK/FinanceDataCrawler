"""
Configuration management for Finance Data Crawler
"""
import os
import json
from pathlib import Path

class Config:
    """Configuration class for crawler settings"""

    # Base URLs
    BASE_URL = "https://www.screener.in"
    EXPLORE_URL = "https://www.screener.in/explore/"

    # Crawling settings
    RATE_LIMIT_INTERVAL = 15  # seconds between requests
    REQUEST_TIMEOUT = 10  # request timeout in seconds
    MAX_RETRIES = 3  # maximum retry attempts
    RATE_LIMIT_WAIT = 60  # seconds to wait after 429 response

    # Session timeout
    DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour default timeout

    # User agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0'
    ]

    # Directory paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    COMPANIES_DIR = BASE_DIR / "companies"
    JSON_DIR = BASE_DIR / "json"
    LOGS_DIR = BASE_DIR / "logs"

    # File paths
    SECTORS_QUEUE_FILE = BASE_DIR / "sectors_queue.json"
    COMPANY_QUEUE_FILE = BASE_DIR / "company_queue.json"
    VISITED_SECTORS_FILE = BASE_DIR / "visited_sectors.json"
    VISITED_COMPANIES_FILE = BASE_DIR / "visited_companies.json"
    PROGRESS_FILE = BASE_DIR / "progress.json"

    # Database settings
    DB_TYPE = "sqlite"  # sqlite or postgresql
    SQLITE_DB_PATH = BASE_DIR / "finance_data.db"

    # PostgreSQL settings (for future use)
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB = os.getenv("POSTGRES_DB", "finance_data")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = LOGS_DIR / "crawler.log"

    # Data validation settings
    REQUIRED_COMPANY_FIELDS = [
        'company_name',
        'stock_price',
        'ratios'
    ]

    # Pagination settings
    SECTOR_PAGE_LIMIT = 50  # Number of companies per sector page

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.COMPANIES_DIR.mkdir(exist_ok=True)
        cls.JSON_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)

    @classmethod
    def load_custom_config(cls, config_file: str):
        """Load custom configuration from JSON file"""
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
                for key, value in custom_config.items():
                    if hasattr(cls, key):
                        setattr(cls, key, value)

    @classmethod
    def save_config(cls, config_file: str):
        """Save current configuration to JSON file"""
        config_data = {
            "RATE_LIMIT_INTERVAL": cls.RATE_LIMIT_INTERVAL,
            "REQUEST_TIMEOUT": cls.REQUEST_TIMEOUT,
            "MAX_RETRIES": cls.MAX_RETRIES,
            "DEFAULT_SESSION_TIMEOUT": cls.DEFAULT_SESSION_TIMEOUT,
            "SECTOR_PAGE_LIMIT": cls.SECTOR_PAGE_LIMIT,
            "DB_TYPE": cls.DB_TYPE,
            "LOG_LEVEL": cls.LOG_LEVEL
        }

        config_path = Path(config_file)
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)
