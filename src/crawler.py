"""
Main crawler module for Finance Data Crawler
Handles HTTP requests, rate limiting, and data extraction coordination
"""
import time
import random
import logging
import requests
from typing import Optional, Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .config import Config
from .extractors import (
    extract_all_data,
    extract_company_links,
    extract_sector_name
)
from .deduplication import DeduplicationManager
from .storage import StorageManager
from .progress import ProgressTracker

logger = logging.getLogger(__name__)


class FinanceCrawler:
    """Main crawler class for scraping financial data"""

    def __init__(self, config: Config, storage_manager: StorageManager,
                 dedup_manager: DeduplicationManager, progress_tracker: ProgressTracker):
        """
        Initialize the crawler.

        Args:
            config (Config): Configuration object
            storage_manager (StorageManager): Storage manager instance
            dedup_manager (DeduplicationManager): Deduplication manager instance
            progress_tracker (ProgressTracker): Progress tracker instance
        """
        self.config = config
        self.storage = storage_manager
        self.dedup = dedup_manager
        self.progress = progress_tracker
        self.last_request_time = 0
        self.session = requests.Session()

    def _get_random_user_agent(self) -> str:
        """Get a random user agent from config"""
        return random.choice(self.config.USER_AGENTS)

    def _wait_for_rate_limit(self):
        """Wait to respect rate limiting"""
        current_time = time.time()
        time_elapsed = current_time - self.last_request_time
        delay = max(0, self.config.RATE_LIMIT_INTERVAL - time_elapsed)

        if delay > 0:
            logger.info(f"Waiting {delay:.1f} seconds before next request...")
            time.sleep(delay)

        self.last_request_time = time.time()

    def fetch_page(self, url: str, retries: int = None) -> Optional[str]:
        """
        Fetch a web page with retry logic and rate limiting.

        Args:
            url (str): URL to fetch
            retries (int, optional): Number of retries (defaults to config value)

        Returns:
            str: HTML content or None if failed
        """
        if retries is None:
            retries = self.config.MAX_RETRIES

        for attempt in range(retries):
            try:
                # Wait for rate limit
                self._wait_for_rate_limit()

                # Prepare headers
                headers = {'User-Agent': self._get_random_user_agent()}

                # Make request
                logger.info(f"Fetching: {url} (attempt {attempt + 1}/{retries})")
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.config.REQUEST_TIMEOUT
                )

                if response.status_code == 200:
                    logger.info(f"Successfully fetched: {url}")
                    return response.text

                elif response.status_code == 429:
                    logger.warning(f"Rate limit exceeded (429). Waiting {self.config.RATE_LIMIT_WAIT}s...")
                    time.sleep(self.config.RATE_LIMIT_WAIT)
                    continue

                else:
                    logger.error(f"HTTP {response.status_code} for {url}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return None

            except requests.exceptions.Timeout:
                logger.error(f"Timeout fetching {url}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None

        return None

    def fetch_sector_urls(self) -> List[str]:
        """
        Fetch all sector URLs from the explore page.

        Returns:
            list: List of sector URLs
        """
        logger.info("Fetching sector URLs from explore page...")
        html = self.fetch_page(self.config.EXPLORE_URL)

        if not html:
            logger.error("Failed to fetch explore page")
            return []

        try:
            soup = BeautifulSoup(html, 'html.parser')
            sector_links = soup.find_all('a', class_='bordered radius-6 padding-4-12 font-size-14 ink-700')

            sector_urls = []
            for link in sector_links:
                href = link.get('href')
                if href:
                    absolute_url = urljoin(self.config.BASE_URL, href)
                    sector_urls.append(absolute_url)

            logger.info(f"Found {len(sector_urls)} sector URLs")
            return sector_urls

        except Exception as e:
            logger.error(f"Error parsing sector URLs: {e}")
            return []

    def crawl_sector(self, sector_url: str) -> Dict:
        """
        Crawl a single sector page and extract company URLs.

        Args:
            sector_url (str): URL of the sector page

        Returns:
            dict: Dictionary with sector name and company URLs
        """
        # Add limit parameter
        sector_url_with_limit = f"{sector_url}?limit={self.config.SECTOR_PAGE_LIMIT}"

        # Fetch page
        html = self.fetch_page(sector_url_with_limit)
        if not html:
            return {'sector_name': None, 'companies': []}

        # Extract sector name
        sector_name = extract_sector_name(html)
        if not sector_name:
            logger.error("Failed to extract sector name")
            return {'sector_name': None, 'companies': []}

        # Check if already visited
        if self.dedup.is_sector_visited(sector_name):
            logger.info(f"Skipping already visited sector: {sector_name}")
            return {'sector_name': sector_name, 'companies': [], 'skipped': True}

        # Extract company links
        company_urls = extract_company_links(html, self.config.BASE_URL)

        logger.info(f"Sector '{sector_name}': Found {len(company_urls)} companies")

        return {
            'sector_name': sector_name,
            'companies': company_urls,
            'skipped': False
        }

    def crawl_company(self, company_url: str) -> Optional[Dict]:
        """
        Crawl a single company page and extract all financial data.

        Args:
            company_url (str): URL of the company page

        Returns:
            dict: Company data or None if failed
        """
        # Check if already visited
        if self.dedup.is_company_visited(company_url):
            logger.info(f"Skipping already visited company: {company_url}")
            return None

        # Fetch page
        html = self.fetch_page(company_url)
        if not html:
            return None

        try:
            # Extract all data
            company_data = extract_all_data(html)

            if not company_data or 'company_name' not in company_data:
                logger.error(f"Failed to extract data from {company_url}")
                return None

            # Add URL to data
            company_data['url'] = company_url

            company_name = company_data['company_name']
            logger.info(f"Successfully extracted data for: {company_name}")

            return company_data

        except Exception as e:
            logger.error(f"Error extracting company data from {company_url}: {e}")
            return None

    def crawl_sectors(self, sector_urls: List[str], timeout: int = None) -> Dict:
        """
        Crawl multiple sectors with timeout support.

        Args:
            sector_urls (list): List of sector URLs to crawl
            timeout (int, optional): Maximum time in seconds (None for no limit)

        Returns:
            dict: Summary of crawling results
        """
        start_time = time.time()
        self.progress.start_session(total_sectors=len(sector_urls))

        results = {
            'sectors_processed': 0,
            'sectors_skipped': 0,
            'companies_found': 0,
            'companies_processed': 0,
            'companies_failed': 0,
            'timeout_reached': False
        }

        for sector_url in sector_urls:
            # Check timeout
            if timeout:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    logger.warning(f"Timeout reached: {timeout}s elapsed")
                    results['timeout_reached'] = True
                    break

            # Crawl sector
            sector_data = self.crawl_sector(sector_url)

            if sector_data['skipped']:
                results['sectors_skipped'] += 1
                continue

            sector_name = sector_data['sector_name']
            if not sector_name:
                continue

            company_urls = sector_data['companies']
            results['sectors_processed'] += 1
            results['companies_found'] += len(company_urls)

            # Update progress
            self.progress.update_sector(sector_name, len(company_urls))

            # Crawl companies in this sector
            for company_url in company_urls:
                # Check timeout again
                if timeout:
                    elapsed_time = time.time() - start_time
                    if elapsed_time > timeout:
                        logger.warning(f"Timeout reached: {timeout}s elapsed")
                        results['timeout_reached'] = True
                        break

                # Crawl company
                company_data = self.crawl_company(company_url)

                if company_data:
                    company_name = company_data['company_name']

                    # Save to storage
                    save_success = self.storage.save_company_data(company_name, company_data)

                    if save_success:
                        # Mark as visited
                        self.dedup.mark_company_as_visited(company_url, company_name)

                        # Update progress
                        self.progress.update_company(company_name, company_url, success=True)
                        results['companies_processed'] += 1

                        # Log to database if available
                        if self.storage.db_storage:
                            self.storage.db_storage.log_crawl(company_name, company_url, 'success')
                    else:
                        logger.error(f"Failed to save data for {company_name}")
                        self.progress.update_company(company_name, company_url, success=False, error="Save failed")
                        results['companies_failed'] += 1

                        if self.storage.db_storage:
                            self.storage.db_storage.log_crawl(company_name, company_url, 'error', 'Save failed')
                else:
                    results['companies_failed'] += 1
                    if self.storage.db_storage:
                        self.storage.db_storage.log_crawl('Unknown', company_url, 'error', 'Extraction failed')

            # Mark sector as visited
            self.dedup.mark_sector_as_visited(sector_name)

            if results['timeout_reached']:
                break

        self.progress.end_session()
        return results

    def close(self):
        """Close crawler resources"""
        self.session.close()
        logger.info("Crawler closed")
