"""
Storage module for Finance Data Crawler
Supports both JSON and SQLite database storage
"""
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class JSONStorage:
    """Handles JSON file storage"""

    def __init__(self, companies_dir: Path, json_dir: Path):
        """
        Initialize JSON storage.

        Args:
            companies_dir (Path): Directory for company JSON files
            json_dir (Path): Directory for intermediate JSON files
        """
        self.companies_dir = companies_dir
        self.json_dir = json_dir

        # Create directories if they don't exist
        self.companies_dir.mkdir(exist_ok=True, parents=True)
        self.json_dir.mkdir(exist_ok=True, parents=True)

    def save_company_data(self, company_name: str, data: Dict) -> bool:
        """
        Save company data to JSON file.

        Args:
            company_name (str): Name of the company
            data (Dict): Company data dictionary

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = self.companies_dir / f"{company_name}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Saved company data: {company_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving company data for {company_name}: {e}")
            return False

    def load_company_data(self, company_name: str) -> Optional[Dict]:
        """
        Load company data from JSON file.

        Args:
            company_name (str): Name of the company

        Returns:
            Dict: Company data or None if not found
        """
        try:
            file_path = self.companies_dir / f"{company_name}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading company data for {company_name}: {e}")
            return None

    def save_intermediate_data(self, data_type: str, data: Dict) -> bool:
        """
        Save intermediate data (quarters, profit_loss, etc.) to JSON file.

        Args:
            data_type (str): Type of data (e.g., 'quarters_data', 'profit_loss_data')
            data (Dict): Data dictionary

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = self.json_dir / f"{data_type}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Saved intermediate data: {data_type}")
            return True
        except Exception as e:
            logger.error(f"Error saving intermediate data {data_type}: {e}")
            return False

    def list_companies(self) -> List[str]:
        """
        List all saved companies.

        Returns:
            List[str]: List of company names
        """
        try:
            companies = [f.stem for f in self.companies_dir.glob('*.json')]
            return companies
        except Exception as e:
            logger.error(f"Error listing companies: {e}")
            return []


class DatabaseStorage:
    """Handles SQLite database storage"""

    def __init__(self, db_path: Path):
        """
        Initialize database storage.

        Args:
            db_path (Path): Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()

    def _init_database(self):
        """Initialize database connection and create tables"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
            logger.info(f"Initialized database at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Companies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT UNIQUE NOT NULL,
                url TEXT,
                stock_price TEXT,
                percentage_change TEXT,
                market_cap TEXT,
                about TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Ratios table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                ratio_name TEXT,
                ratio_value TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        ''')

        # Quarters data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quarters_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                quarter TEXT,
                data JSON,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        ''')

        # Financial statements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                statement_type TEXT,
                data JSON,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        ''')

        # Crawl history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                url TEXT,
                status TEXT,
                error_message TEXT,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()
        logger.info("Database tables created successfully")

    def save_company_data(self, company_name: str, data: Dict) -> bool:
        """
        Save company data to database.

        Args:
            company_name (str): Name of the company
            data (Dict): Company data dictionary

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()

            # Extract company basic info
            company_data = data.get('company_data', {})
            stock_price = company_data.get('stock_price', '')
            percentage_change = company_data.get('percentage_change', '')
            ratios = company_data.get('ratios', {})
            market_cap = ratios.get('Market Cap', '')
            about = company_data.get('about_and_key_points', '')
            url = data.get('url', '')

            # Insert or update company
            cursor.execute('''
                INSERT INTO companies (company_name, url, stock_price, percentage_change, market_cap, about, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_name) DO UPDATE SET
                    stock_price=excluded.stock_price,
                    percentage_change=excluded.percentage_change,
                    market_cap=excluded.market_cap,
                    about=excluded.about,
                    updated_at=excluded.updated_at
            ''', (company_name, url, stock_price, percentage_change, market_cap, about, datetime.now()))

            company_id = cursor.lastrowid

            # Insert ratios
            cursor.execute('DELETE FROM ratios WHERE company_id = ?', (company_id,))
            for ratio_name, ratio_value in ratios.items():
                cursor.execute('''
                    INSERT INTO ratios (company_id, ratio_name, ratio_value)
                    VALUES (?, ?, ?)
                ''', (company_id, ratio_name, ratio_value))

            # Insert financial statements
            cursor.execute('DELETE FROM financial_statements WHERE company_id = ?', (company_id,))
            for statement_type in ['quarters_data', 'profit_loss_data', 'balance_sheet_data',
                                   'cash_flows_data', 'ratios_data', 'shareholding_data']:
                if statement_type in data:
                    cursor.execute('''
                        INSERT INTO financial_statements (company_id, statement_type, data)
                        VALUES (?, ?, ?)
                    ''', (company_id, statement_type, json.dumps(data[statement_type])))

            self.conn.commit()
            logger.info(f"Saved company data to database: {company_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving company data to database for {company_name}: {e}")
            self.conn.rollback()
            return False

    def load_company_data(self, company_name: str) -> Optional[Dict]:
        """
        Load company data from database.

        Args:
            company_name (str): Name of the company

        Returns:
            Dict: Company data or None if not found
        """
        try:
            cursor = self.conn.cursor()

            # Get company basic info
            cursor.execute('SELECT * FROM companies WHERE company_name = ?', (company_name,))
            company_row = cursor.fetchone()

            if not company_row:
                return None

            company_id = company_row['id']

            # Get ratios
            cursor.execute('SELECT ratio_name, ratio_value FROM ratios WHERE company_id = ?', (company_id,))
            ratios = {row['ratio_name']: row['ratio_value'] for row in cursor.fetchall()}

            # Get financial statements
            cursor.execute('SELECT statement_type, data FROM financial_statements WHERE company_id = ?', (company_id,))
            statements = {row['statement_type']: json.loads(row['data']) for row in cursor.fetchall()}

            # Construct full company data
            company_data = {
                'company_name': company_row['company_name'],
                'url': company_row['url'],
                'company_data': {
                    'company_name': company_row['company_name'],
                    'stock_price': company_row['stock_price'],
                    'percentage_change': company_row['percentage_change'],
                    'ratios': ratios,
                    'about_and_key_points': company_row['about']
                },
                **statements
            }

            return company_data
        except Exception as e:
            logger.error(f"Error loading company data from database for {company_name}: {e}")
            return None

    def log_crawl(self, company_name: str, url: str, status: str, error_message: str = None):
        """
        Log crawl attempt to database.

        Args:
            company_name (str): Name of the company
            url (str): Company URL
            status (str): Status of crawl (success, error, skipped)
            error_message (str, optional): Error message if failed
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO crawl_history (company_name, url, status, error_message)
                VALUES (?, ?, ?, ?)
            ''', (company_name, url, status, error_message))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error logging crawl: {e}")

    def get_statistics(self) -> Dict:
        """
        Get database statistics.

        Returns:
            Dict: Statistics dictionary
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute('SELECT COUNT(*) as count FROM companies')
            total_companies = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) as count FROM crawl_history WHERE status = "success"')
            successful_crawls = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) as count FROM crawl_history WHERE status = "error"')
            failed_crawls = cursor.fetchone()['count']

            return {
                'total_companies': total_companies,
                'successful_crawls': successful_crawls,
                'failed_crawls': failed_crawls
            }
        except Exception as e:
            logger.error(f"Error getting database statistics: {e}")
            return {}

    def list_companies(self) -> List[str]:
        """
        List all companies in database.

        Returns:
            List[str]: List of company names
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT company_name FROM companies ORDER BY company_name')
            return [row['company_name'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error listing companies: {e}")
            return []

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


class StorageManager:
    """Unified storage manager that handles both JSON and database storage"""

    def __init__(self, config):
        """
        Initialize storage manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self.json_storage = JSONStorage(config.COMPANIES_DIR, config.JSON_DIR)
        self.db_storage = None

        if config.DB_TYPE == "sqlite":
            self.db_storage = DatabaseStorage(config.SQLITE_DB_PATH)

    def save_company_data(self, company_name: str, data: Dict, use_db: bool = True) -> bool:
        """
        Save company data to storage.

        Args:
            company_name (str): Name of the company
            data (Dict): Company data dictionary
            use_db (bool): Whether to use database storage

        Returns:
            bool: True if successful, False otherwise
        """
        # Always save to JSON
        json_success = self.json_storage.save_company_data(company_name, data)

        # Optionally save to database
        db_success = True
        if use_db and self.db_storage:
            db_success = self.db_storage.save_company_data(company_name, data)

        return json_success and db_success

    def load_company_data(self, company_name: str, from_db: bool = False) -> Optional[Dict]:
        """
        Load company data from storage.

        Args:
            company_name (str): Name of the company
            from_db (bool): Whether to load from database

        Returns:
            Dict: Company data or None if not found
        """
        if from_db and self.db_storage:
            return self.db_storage.load_company_data(company_name)
        else:
            return self.json_storage.load_company_data(company_name)

    def list_companies(self, from_db: bool = False) -> List[str]:
        """
        List all companies.

        Args:
            from_db (bool): Whether to list from database

        Returns:
            List[str]: List of company names
        """
        if from_db and self.db_storage:
            return self.db_storage.list_companies()
        else:
            return self.json_storage.list_companies()

    def get_statistics(self) -> Dict:
        """
        Get storage statistics.

        Returns:
            Dict: Statistics dictionary
        """
        stats = {
            'json_companies': len(self.json_storage.list_companies())
        }

        if self.db_storage:
            db_stats = self.db_storage.get_statistics()
            stats.update(db_stats)

        return stats

    def close(self):
        """Close storage connections"""
        if self.db_storage:
            self.db_storage.close()
