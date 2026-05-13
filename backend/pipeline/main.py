"""
Main entry point for the Finance Data Crawler Pipeline.
Orchestrates the complete data extraction workflow.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from .config import EXPLORE_URL
from .core.crawler import Crawler
from .core.queue_manager import QueueManager
from .core.storage import Storage
from .parsers.sector_parser import SectorParser
from .parsers.company_parser import CompanyParser
from .utils.logger import pipeline_logger
import time

class FinanceDataPipeline:
    """
    Main pipeline orchestrator.
    """
    
    def __init__(self):
        self.logger = pipeline_logger
        self.crawler = Crawler()
        self.queue_manager = QueueManager()
        self.storage = Storage()
        
        # Initialize parsers
        self.sector_parser = SectorParser()
        self.company_parser = CompanyParser()
        
        # Register section parsers (these would be implemented in sections.py)
        # For now, we'll use the company parser's built-in methods
        
        self.logger.info("Finance Data Pipeline initialized")
    
    def run_sector_discovery(self):
        """
        Run sector discovery to populate sectors queue.
        """
        self.logger.info("Starting sector discovery...")
        
        # Check if sectors queue already exists
        if Path(SECTORS_QUEUE_FILE).exists():
            self.logger.info("Sectors queue already exists, skipping discovery")
            return
        
        # Fetch explore page
        soup = self.crawler.fetch_url(EXPLORE_URL)
        if not soup:
            self.logger.error("Failed to fetch explore page")
            return
        
        # Extract sector links (this logic should be in SectorParser)
        sector_links = []
        sector_elements = soup.find_all('a', class_='bordered radius-6 padding-4-12 font-size-14 ink-700')
        
        for element in sector_elements:
            href = element.get('href')
            if href:
                full_url = f"https://www.screener.in{href}"
                sector_links.append(full_url)
        
        if not sector_links:
            self.logger.error("No sector links found")
            return
        
        # Save to queue
        self.queue_manager.save_sector_queue(sector_links)
        self.logger.info(f"Discovered {len(sector_links)} sectors")
    
    def run_company_discovery(self, timeout_minutes: int = 60):
        """
        Run company discovery by processing sectors.
        
        Args:
            timeout_minutes: Maximum time to run in minutes
        """
        self.logger.info("Starting company discovery...")
        
        # Load data
        sector_urls = self.queue_manager.load_sector_queue()
        visited_sectors = self.queue_manager.load_visited_sectors()
        companies_data = {}
        
        # Convert timeout to seconds
        timeout_seconds = timeout_minutes * 60
        start_time = time.time()
        
        for sector_url in sector_urls:
            # Check timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                self.logger.warning(f"Timeout reached after {timeout_minutes} minutes")
                break
            
            # Check if sector already visited
            # Fetch sector page to get name
            sector_soup = self.crawler.fetch_url(sector_url)
            if not sector_soup:
                continue
                
            sector_name = self.sector_parser.extract_sector_name(sector_soup)
            if not sector_name:
                continue
                
            if self.queue_manager.is_sector_visited(sector_name, visited_sectors):
                self.logger.info(f"Skipping already visited sector: {sector_name}")
                continue
            
            self.logger.info(f"Processing sector: {sector_name}")
            
            # Fetch sector page
            soup = self.crawler.fetch_url(sector_url)
            if not soup:
                continue
            
            # Parse sector and extract companies
            result = self.sector_parser.parse(soup)
            if result:
                companies_data[sector_name] = result['company_links']
                self.queue_manager.mark_sector_visited(sector_name, visited_sectors)
                
                # Save progress
                self.queue_manager.save_company_queue(companies_data)
        
        self.logger.info("Company discovery completed")
    
    def run_company_extraction(self, max_companies: int = None, sector_names: list[str] = None, company_urls: list[str] = None, skip_existing: bool = True):
        """
        Run company data extraction.
        
        Args:
            max_companies: Maximum number of companies to extract (None for all)
            sector_names: Only extract companies from these sectors
            company_urls: Only extract these specific company URLs
            skip_existing: Skip companies that already have data saved
        """
        self.logger.info("Starting company data extraction...")
        
        # Load company queue
        companies_data = self.queue_manager.load_company_queue()
        if not companies_data:
            self.logger.error("No companies in queue")
            return
        
        # Filter by sector names if provided
        if sector_names:
            companies_data = {s: u for s, u in companies_data.items() if s in sector_names}

        # Handle selective company URLs
        if company_urls:
            self.logger.info(f"Extracting {len(company_urls)} specific companies")
            for url in company_urls:
                soup = self.crawler.fetch_url(url)
                if not soup:
                    continue
                result = self.company_parser.parse(soup, company_url=url)
                if result:
                    company_name = result["company_name"]
                    if skip_existing and self.storage.company_exists(company_name):
                        self.logger.info(f"Skipping existing: {company_name}")
                        continue
                    self.storage.save_company_data(company_name, result)
                    processed_count += 1
            self.logger.info(f"Selective extraction completed. Processed {processed_count} companies")
            return

        # Track processed companies
        processed_count = 0
        
        for sector_name, urls_list in companies_data.items():
            self.logger.info(f"Processing sector: {sector_name} ({len(urls_list)} companies)")
            
            for company_url in urls_list:
                if max_companies and processed_count >= max_companies:
                    self.logger.info(f"Reached max companies limit: {max_companies}")
                    return
                
                # Fetch company page
                soup = self.crawler.fetch_url(company_url)
                if not soup:
                    continue
                
                # Check if company already exists
                if skip_existing:
                    from .utils.helpers import extract_company_name_from_url
                    guess = extract_company_name_from_url(company_url)
                    if guess and self.storage.company_exists(guess):
                        self.logger.info(f"Skipping existing: {guess}")
                        continue

                # Parse company data
                result = self.company_parser.parse(soup, company_url=company_url)
                if result:
                    # Save company data
                    company_name = result['company_name']
                    success = self.storage.save_company_data(company_name, result)
                    
                    if success:
                        processed_count += 1
                        self.logger.info(f"Processed {processed_count}: {company_name}")
                    else:
                        self.logger.error(f"Failed to save data for {company_name}")
                else:
                    self.logger.error(f"Failed to parse data for {company_url}")
        
        self.logger.info(f"Company extraction completed. Processed {processed_count} companies")
    
    def run_full_pipeline(self, timeout_minutes: int = 60, max_companies: int = None):
        """
        Run the complete pipeline.
        
        Args:
            timeout_minutes: Timeout for company discovery
            max_companies: Maximum companies to extract
        """
        self.logger.info("Starting full pipeline...")
        
        # Step 1: Sector discovery
        self.run_sector_discovery()
        
        # Step 2: Company discovery
        self.run_company_discovery(timeout_minutes)
        
        # Step 3: Company extraction
        self.run_company_extraction(max_companies)
        
        # Print final statistics
        self.print_statistics()
    
    def print_statistics(self):
        """Print pipeline statistics."""
        stats = self.queue_manager.get_statistics()
        storage_stats = self.storage.get_storage_stats()
        
        self.logger.info("=== Pipeline Statistics ===")
        self.logger.info(f"Sectors: {stats['total_sectors']} total, {stats['visited_sectors']} visited")
        self.logger.info(f"Companies in queue: {stats['total_companies']}")
        self.logger.info(f"Companies extracted: {storage_stats['total_companies']}")
        self.logger.info(f"Storage used: {storage_stats['total_size_mb']} MB")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Finance Data Crawler Pipeline')
    parser.add_argument('--mode', choices=['sectors', 'companies', 'extract', 'full'], 
                       default='full', help='Pipeline mode')
    parser.add_argument('--timeout', type=int, default=60, 
                       help='Timeout in minutes for company discovery')
    parser.add_argument('--max-companies', type=int, 
                       help='Maximum companies to extract')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = FinanceDataPipeline()
    
    # Run based on mode
    if args.mode == 'sectors':
        pipeline.run_sector_discovery()
    elif args.mode == 'companies':
        pipeline.run_company_discovery(args.timeout)
    elif args.mode == 'extract':
        pipeline.run_company_extraction(args.max_companies)
    elif args.mode == 'full':
        pipeline.run_full_pipeline(args.timeout, args.max_companies)

if __name__ == "__main__":
    main()