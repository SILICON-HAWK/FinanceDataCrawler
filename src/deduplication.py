"""
Deduplication module for tracking visited sectors and companies
Implements hash map functionality for efficient lookup
"""
import json
import logging
import hashlib
from pathlib import Path
from typing import Set, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DeduplicationManager:
    """Manages visited sectors and companies to prevent duplicate crawling"""

    def __init__(self, sectors_file: Path, companies_file: Path):
        """
        Initialize deduplication manager.

        Args:
            sectors_file (Path): Path to visited sectors JSON file
            companies_file (Path): Path to visited companies JSON file
        """
        self.sectors_file = sectors_file
        self.companies_file = companies_file
        self.visited_sectors: Set[str] = set()
        self.visited_companies: Set[str] = set()
        self.company_hash_map: dict = {}  # Maps company URLs to their hash

        self._load_visited_data()

    def _load_visited_data(self):
        """Load visited sectors and companies from disk"""
        # Load visited sectors
        if self.sectors_file.exists():
            try:
                with open(self.sectors_file, 'r') as f:
                    sectors_data = json.load(f)
                    self.visited_sectors = set(sectors_data)
                logger.info(f"Loaded {len(self.visited_sectors)} visited sectors")
            except Exception as e:
                logger.error(f"Error loading visited sectors: {e}")
                self.visited_sectors = set()

        # Load visited companies
        if self.companies_file.exists():
            try:
                with open(self.companies_file, 'r') as f:
                    companies_data = json.load(f)
                    self.visited_companies = set(companies_data.get('companies', []))
                    self.company_hash_map = companies_data.get('hash_map', {})
                logger.info(f"Loaded {len(self.visited_companies)} visited companies")
            except Exception as e:
                logger.error(f"Error loading visited companies: {e}")
                self.visited_companies = set()
                self.company_hash_map = {}

    def save_visited_sectors(self):
        """Save visited sectors to disk"""
        try:
            with open(self.sectors_file, 'w') as f:
                json.dump(list(self.visited_sectors), f, indent=4)
            logger.info(f"Saved {len(self.visited_sectors)} visited sectors")
        except Exception as e:
            logger.error(f"Error saving visited sectors: {e}")

    def save_visited_companies(self):
        """Save visited companies to disk"""
        try:
            data = {
                'companies': list(self.visited_companies),
                'hash_map': self.company_hash_map
            }
            with open(self.companies_file, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Saved {len(self.visited_companies)} visited companies")
        except Exception as e:
            logger.error(f"Error saving visited companies: {e}")

    def is_sector_visited(self, sector_name: str) -> bool:
        """
        Check if a sector has been visited.

        Args:
            sector_name (str): Name of the sector

        Returns:
            bool: True if sector has been visited, False otherwise
        """
        return sector_name in self.visited_sectors

    def mark_sector_as_visited(self, sector_name: str):
        """
        Mark a sector as visited.

        Args:
            sector_name (str): Name of the sector
        """
        self.visited_sectors.add(sector_name)
        self.save_visited_sectors()
        logger.info(f"Marked sector as visited: {sector_name}")

    def is_company_visited(self, company_url: str) -> bool:
        """
        Check if a company has been visited.

        Args:
            company_url (str): URL of the company

        Returns:
            bool: True if company has been visited, False otherwise
        """
        company_hash = self._hash_url(company_url)
        return company_hash in self.visited_companies

    def mark_company_as_visited(self, company_url: str, company_name: Optional[str] = None):
        """
        Mark a company as visited.

        Args:
            company_url (str): URL of the company
            company_name (str, optional): Name of the company
        """
        company_hash = self._hash_url(company_url)
        self.visited_companies.add(company_hash)

        # Store mapping in hash map
        self.company_hash_map[company_hash] = {
            'url': company_url,
            'name': company_name if company_name else self._extract_company_id(company_url)
        }

        self.save_visited_companies()
        logger.info(f"Marked company as visited: {company_url}")

    def _hash_url(self, url: str) -> str:
        """
        Create a hash of the URL for efficient lookup.

        Args:
            url (str): URL to hash

        Returns:
            str: Hash of the URL
        """
        return hashlib.md5(url.encode()).hexdigest()

    def _extract_company_id(self, url: str) -> str:
        """
        Extract company identifier from URL.

        Args:
            url (str): Company URL

        Returns:
            str: Company identifier
        """
        # Extract company ID from URL like https://www.screener.in/company/SUNPHARMA/
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'company':
            return path_parts[1]
        return url

    def get_unvisited_sectors(self, all_sectors: list) -> list:
        """
        Get list of unvisited sectors.

        Args:
            all_sectors (list): List of all sector names

        Returns:
            list: List of unvisited sector names
        """
        return [sector for sector in all_sectors if sector not in self.visited_sectors]

    def get_unvisited_companies(self, all_companies: list) -> list:
        """
        Get list of unvisited companies.

        Args:
            all_companies (list): List of all company URLs

        Returns:
            list: List of unvisited company URLs
        """
        return [company for company in all_companies if not self.is_company_visited(company)]

    def get_statistics(self) -> dict:
        """
        Get statistics about visited items.

        Returns:
            dict: Statistics dictionary
        """
        return {
            'visited_sectors': len(self.visited_sectors),
            'visited_companies': len(self.visited_companies),
            'sectors_list': list(self.visited_sectors),
            'companies_count': len(self.company_hash_map)
        }

    def reset_sectors(self):
        """Reset visited sectors"""
        self.visited_sectors = set()
        self.save_visited_sectors()
        logger.info("Reset visited sectors")

    def reset_companies(self):
        """Reset visited companies"""
        self.visited_companies = set()
        self.company_hash_map = {}
        self.save_visited_companies()
        logger.info("Reset visited companies")

    def reset_all(self):
        """Reset all visited data"""
        self.reset_sectors()
        self.reset_companies()
        logger.info("Reset all visited data")
