#!/usr/bin/env python3
"""
Finance Data Crawler - Main Scraper Script
Scrapes company financial data from screener.in
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Configure logging with colorized output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://www.screener.in"
RATE_LIMIT_INTERVAL = 15  # seconds between requests
MAX_RETRIES = 3
REQUEST_TIMEOUT = 10
SECTORS_LIMIT = 50  # Number of companies per sector page

# User-agent rotation to avoid detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
]

# Ensure directories exist
Path("json").mkdir(exist_ok=True)
Path("companies").mkdir(exist_ok=True)


class FinanceCrawler:
    """Main crawler class for scraping financial data"""

    def __init__(self):
        self.last_request_time = 0
        self.companies_scraped = 0
        self.sectors_processed = 0

    def wait_rate_limit(self):
        """Ensure rate limiting between requests"""
        current_time = time.time()
        time_elapsed = current_time - self.last_request_time
        delay = max(0, RATE_LIMIT_INTERVAL - time_elapsed)

        if delay > 0:
            logger.info(f"⏳ Rate limiting: waiting {delay:.1f} seconds...")
            time.sleep(delay)

        self.last_request_time = time.time()

    def make_request(self, url: str) -> Optional[str]:
        """Make HTTP request with retries and rate limiting"""
        self.wait_rate_limit()

        for attempt in range(MAX_RETRIES):
            try:
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                logger.info(f"🌐 Requesting: {url}")

                response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)

                if response.status_code == 200:
                    logger.info(f"✅ Success: {url}")
                    return response.text
                elif response.status_code == 429:
                    wait_time = 60
                    logger.warning(f"⚠️  Rate limit exceeded. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ HTTP {response.status_code}: {url}")

            except requests.exceptions.Timeout:
                logger.error(f"⏱️  Timeout on attempt {attempt + 1}/{MAX_RETRIES}")
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Request error: {e}")

            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # Exponential backoff

        return None

    def extract_company_data(self, html: str) -> Optional[Dict]:
        """Extract company overview and key metrics"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            company_info_div = soup.find('div', id='top')

            if not company_info_div:
                logger.error("Company info section not found")
                return None

            # Extract company name
            company_name_tag = company_info_div.find('h1', class_='margin-0')
            company_name = company_name_tag.text.strip() if company_name_tag else "Unknown"

            # Extract stock price
            stock_price_div = company_info_div.find('div', class_='font-size-18')
            if stock_price_div:
                stock_price = stock_price_div.find('span').text.strip().replace('₹', '').strip()
                percentage_change = stock_price_div.find('span', class_='font-size-12').text.strip()
            else:
                stock_price = "N/A"
                percentage_change = "N/A"

            # Extract financial ratios
            ratios = {}
            ratios_div = company_info_div.find('ul', id='top-ratios')
            if ratios_div:
                for ratio in ratios_div.find_all('li'):
                    name = ratio.find('span', class_='name').text.strip()
                    value = ratio.find('span', class_='value').text.strip().replace('₹', '').strip()
                    value = ' '.join(value.split())
                    ratios[name] = value

            return {
                'company_name': company_name,
                'stock_price': stock_price,
                'percentage_change': percentage_change,
                'ratios': ratios,
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error extracting company data: {e}")
            return None

    def extract_quarters_data(self, html: str) -> Optional[Dict]:
        """Extract quarterly financial data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            quarters_section = soup.find('section', id='quarters')

            if not quarters_section:
                return None

            table = quarters_section.find('table', class_='data-table')
            if not table:
                return None

            headers = [th.text.strip() for th in table.find_all('th')][1:]

            data = []
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                cols = [col.text.strip().replace(' ', '').replace('+', '') for col in cols][1:]
                data.append([col for col in cols if col])

            categories = ['Sales', 'Expenses', 'Operating Profit', 'OPM %',
                         'Other Income', 'Interest', 'Depreciation',
                         'Profit before tax', 'Tax %', 'Net Profit', 'EPS in Rs']

            quarters_data = {}
            for i, header in enumerate(headers):
                quarters_data[header] = {}
                for j, category in enumerate(categories):
                    if j < len(data) and i < len(data[j]):
                        quarters_data[header][category] = data[j][i]

            return quarters_data

        except Exception as e:
            logger.error(f"Error extracting quarters data: {e}")
            return None

    def extract_balance_sheet_data(self, html: str) -> Optional[Dict]:
        """Extract balance sheet data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            section = soup.find('section', id='balance-sheet')

            if not section:
                return None

            table = section.find('table', class_='data-table')
            if not table:
                return None

            headers = [th.text.strip() for th in table.find_all('th')][1:]

            data = []
            categories = []
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                categories.append(cols[0].text.strip())
                cols = [col.text.strip().replace(' ', '').replace('+', '') for col in cols][1:]
                data.append([col for col in cols if col])

            balance_sheet_data = {}
            for i, header in enumerate(headers):
                balance_sheet_data[header] = {}
                for j, category in enumerate(categories):
                    if j < len(data) and i < len(data[j]):
                        balance_sheet_data[header][category] = data[j][i]

            return balance_sheet_data

        except Exception as e:
            logger.error(f"Error extracting balance sheet: {e}")
            return None

    def scrape_company(self, company_url: str) -> bool:
        """Scrape all data for a single company"""
        full_url = f"{BASE_URL}{company_url}consolidated/"

        logger.info(f"\n{'='*60}")
        logger.info(f"📊 Starting scrape: {company_url}")
        logger.info(f"{'='*60}")

        html = self.make_request(full_url)
        if not html:
            logger.error(f"Failed to fetch company page")
            return False

        # Extract company data
        logger.info("📈 Extracting company overview...")
        company_data = self.extract_company_data(html)

        if not company_data:
            logger.error("Failed to extract company data")
            return False

        company_name = company_data['company_name']
        logger.info(f"✅ Company: {company_name}")
        logger.info(f"   Price: {company_data['stock_price']}")
        logger.info(f"   Change: {company_data['percentage_change']}")

        # Extract additional data
        logger.info("📊 Extracting quarterly data...")
        quarters_data = self.extract_quarters_data(html)

        logger.info("💰 Extracting balance sheet...")
        balance_sheet = self.extract_balance_sheet_data(html)

        # Save individual JSON files
        logger.info("💾 Saving data to JSON...")
        with open('json/company_data.json', 'w') as f:
            json.dump(company_data, f, indent=4)

        if quarters_data:
            with open('json/quarters_data.json', 'w') as f:
                json.dump(quarters_data, f, indent=4)

        if balance_sheet:
            with open('json/balance_sheet_data.json', 'w') as f:
                json.dump(balance_sheet, f, indent=4)

        # Save combined company file
        combined_data = {
            'company_name': company_name,
            'company_data': company_data,
            'quarters_data': quarters_data,
            'balance_sheet_data': balance_sheet,
            'scraped_at': datetime.now().isoformat()
        }

        company_file = f"companies/{company_name.replace('/', '_')}.json"
        with open(company_file, 'w') as f:
            json.dump(combined_data, f, indent=4)

        logger.info(f"✅ Saved: {company_file}")
        self.companies_scraped += 1

        logger.info(f"\n🎉 Successfully scraped {company_name}")
        logger.info(f"📊 Total companies scraped this session: {self.companies_scraped}")

        return True


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🚀 FINANCE DATA CRAWLER")
    print("="*60)
    print(f"⚙️  Rate limit: {RATE_LIMIT_INTERVAL}s between requests")
    print(f"🔄 Max retries: {MAX_RETRIES}")
    print("="*60 + "\n")

    crawler = FinanceCrawler()

    # Example: Scrape a single company
    test_company = "/company/SUNPHARMA/"

    logger.info(f"🎯 Starting crawler test with: {test_company}")

    success = crawler.scrape_company(test_company)

    if success:
        print("\n" + "="*60)
        print("✅ CRAWLER TEST COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"📁 Data saved in:")
        print(f"   - json/company_data.json")
        print(f"   - json/quarters_data.json")
        print(f"   - json/balance_sheet_data.json")
        print(f"   - companies/*.json")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("❌ CRAWLER TEST FAILED")
        print("="*60 + "\n")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
