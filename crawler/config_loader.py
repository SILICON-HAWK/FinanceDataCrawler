"""Configuration loader for the crawler"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class CrawlerConfig:
    """Configuration manager for the crawler"""

    def __init__(self, config_file: str = "crawler_config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self._apply_env_overrides()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = Path(self.config_file)

        if not config_path.exists():
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            return self._get_default_config()

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'crawler': {
                'base_url': 'https://www.screener.in',
                'rate_limit_interval': 15,
                'request_timeout': 10,
                'max_retries': 3,
                'sector_limit': 50,
                'modules': {
                    'company_overview': True,
                    'quarterly_data': True,
                    'balance_sheet': True,
                    'cash_flow': True,
                    'profit_loss': True,
                    'ratios': True,
                    'shareholding': True,
                },
            },
            'storage': {
                'save_json': True,
                'json_dir': 'json',
                'companies_dir': 'companies',
                'auto_import_db': True,
            },
            'logging': {
                'level': 'INFO',
                'colorize': True,
            },
            'queue': {
                'auto_process_queue': False,
                'max_batch_size': 20,
                'skip_existing': True,
            },
        }

    def _apply_env_overrides(self):
        """Override config with environment variables"""
        # Rate limit
        if rate_limit := os.getenv('CRAWLER_RATE_LIMIT'):
            self.config['crawler']['rate_limit_interval'] = int(rate_limit)

        # Database settings
        if db_host := os.getenv('DATABASE_HOST'):
            self.config.setdefault('storage', {}).setdefault('database', {})['host'] = db_host

        if db_name := os.getenv('DATABASE_NAME'):
            self.config.setdefault('storage', {}).setdefault('database', {})['name'] = db_name

        # Logging level
        if log_level := os.getenv('CRAWLER_LOG_LEVEL'):
            self.config['logging']['level'] = log_level

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    @property
    def base_url(self) -> str:
        return self.get('crawler.base_url', 'https://www.screener.in')

    @property
    def rate_limit(self) -> int:
        return self.get('crawler.rate_limit_interval', 15)

    @property
    def max_retries(self) -> int:
        return self.get('crawler.max_retries', 3)

    @property
    def request_timeout(self) -> int:
        return self.get('crawler.request_timeout', 10)

    @property
    def user_agents(self) -> list:
        return self.get('crawler.user_agents', [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        ])

    @property
    def enabled_modules(self) -> Dict[str, bool]:
        return self.get('crawler.modules', {})

    @property
    def save_json(self) -> bool:
        return self.get('storage.save_json', True)

    @property
    def json_dir(self) -> str:
        return self.get('storage.json_dir', 'json')

    @property
    def companies_dir(self) -> str:
        return self.get('storage.companies_dir', 'companies')

    @property
    def log_level(self) -> str:
        return self.get('logging.level', 'INFO')

    @property
    def max_batch_size(self) -> int:
        return self.get('queue.max_batch_size', 20)

    def reload(self):
        """Reload configuration from file"""
        self.config = self._load_config()
        self._apply_env_overrides()
        logger.info("Configuration reloaded")


# Global config instance
_config = None


def get_config() -> CrawlerConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = CrawlerConfig()
    return _config


def reload_config():
    """Reload global configuration"""
    global _config
    _config = None
    return get_config()
