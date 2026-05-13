"""
Queue management for the Finance Data Crawler Pipeline.
Handles sector and company queues with persistence and progress tracking.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

from config import SECTORS_QUEUE_FILE, COMPANY_QUEUE_FILE, VISITED_SECTORS_FILE
from utils.logger import pipeline_logger
from utils.helpers import clean_text, extract_company_name_from_url

class QueueManager:
    """
    Manages sector and company queues with persistence.
    """
    
    def __init__(self):
        self.sectors_queue_file = SECTORS_QUEUE_FILE
        self.company_queue_file = COMPANY_QUEUE_FILE
        self.visited_sectors_file = VISITED_SECTORS_FILE
        
    def load_sector_queue(self) -> List[str]:
        """
        Load sector URLs from queue file.
        
        Returns:
            List of sector URLs
        """
        try:
            with open(self.sectors_queue_file, 'r', encoding='utf-8') as f:
                sectors = json.load(f)
                pipeline_logger.info(f"Loaded {len(sectors)} sectors from queue")
                return sectors
        except FileNotFoundError:
            pipeline_logger.info("Sectors queue file not found, creating new queue")
            return []
        except json.JSONDecodeError as e:
            pipeline_logger.error(f"Error parsing sectors queue: {e}")
            return []
    
    def save_sector_queue(self, sectors: List[str]):
        """
        Save sector URLs to queue file.
        
        Args:
            sectors: List of sector URLs
        """
        try:
            with open(self.sectors_queue_file, 'w', encoding='utf-8') as f:
                json.dump(sectors, f, indent=2, ensure_ascii=False)
            pipeline_logger.info(f"Saved {len(sectors)} sectors to queue")
        except Exception as e:
            pipeline_logger.error(f"Error saving sectors queue: {e}")
    
    def load_company_queue(self) -> Dict[str, List[str]]:
        """
        Load company URLs from queue file.
        
        Returns:
            Dictionary mapping sector names to company URLs
        """
        try:
            with open(self.company_queue_file, 'r', encoding='utf-8') as f:
                companies = json.load(f)
                total_companies = sum(len(urls) for urls in companies.values())
                pipeline_logger.info(f"Loaded {len(companies)} sectors with {total_companies} companies from queue")
                return companies
        except FileNotFoundError:
            pipeline_logger.info("Companies queue file not found, creating new queue")
            return {}
        except json.JSONDecodeError as e:
            pipeline_logger.error(f"Error parsing companies queue: {e}")
            return {}
    
    def save_company_queue(self, companies: Dict[str, List[str]]):
        """
        Save company URLs to queue file.
        
        Args:
            companies: Dictionary mapping sector names to company URLs
        """
        try:
            with open(self.company_queue_file, 'w', encoding='utf-8') as f:
                json.dump(companies, f, indent=2, ensure_ascii=False)
            total_companies = sum(len(urls) for urls in companies.values())
            pipeline_logger.info(f"Saved {len(companies)} sectors with {total_companies} companies to queue")
        except Exception as e:
            pipeline_logger.error(f"Error saving companies queue: {e}")
    
    def load_visited_sectors(self) -> Set[str]:
        """
        Load visited sectors from file.
        
        Returns:
            Set of visited sector names
        """
        try:
            with open(self.visited_sectors_file, 'r', encoding='utf-8') as f:
                visited = set(json.load(f))
                pipeline_logger.info(f"Loaded {len(visited)} visited sectors")
                return visited
        except FileNotFoundError:
            pipeline_logger.info("Visited sectors file not found, creating new file")
            return set()
        except json.JSONDecodeError as e:
            pipeline_logger.error(f"Error parsing visited sectors: {e}")
            return set()
    
    def save_visited_sectors(self, visited: Set[str]):
        """
        Save visited sectors to file.
        
        Args:
            visited: Set of visited sector names
        """
        try:
            with open(self.visited_sectors_file, 'w', encoding='utf-8') as f:
                json.dump(list(visited), f, indent=2, ensure_ascii=False)
            pipeline_logger.info(f"Saved {len(visited)} visited sectors")
        except Exception as e:
            pipeline_logger.error(f"Error saving visited sectors: {e}")
    
    def is_sector_visited(self, sector_name: str, visited_sectors: Set[str]) -> bool:
        """
        Check if a sector has been visited.
        
        Args:
            sector_name: Name of the sector
            visited_sectors: Set of visited sectors
            
        Returns:
            True if visited, False otherwise
        """
        return sector_name in visited_sectors
    
    def mark_sector_visited(self, sector_name: str, visited_sectors: Set[str]):
        """
        Mark a sector as visited.
        
        Args:
            sector_name: Name of the sector
            visited_sectors: Set of visited sectors to update
        """
        visited_sectors.add(sector_name)
        self.save_visited_sectors(visited_sectors)
        pipeline_logger.info(f"Marked sector as visited: {sector_name}")
    
    def add_sector_to_queue(self, url: str):
        """
        Add a sector URL to the queue.
        
        Args:
            url: Sector URL to add
        """
        sectors = self.load_sector_queue()
        if url not in sectors:
            sectors.append(url)
            self.save_sector_queue(sectors)
            pipeline_logger.info(f"Added sector to queue: {url}")
    
    def add_companies_to_queue(self, sector_name: str, company_urls: List[str]):
        """
        Add company URLs to the queue for a specific sector.
        
        Args:
            sector_name: Name of the sector
            company_urls: List of company URLs
        """
        companies = self.load_company_queue()
        if sector_name not in companies:
            companies[sector_name] = []
        
        # Add only new companies
        new_companies = [url for url in company_urls if url not in companies[sector_name]]
        companies[sector_name].extend(new_companies)
        
        self.save_company_queue(companies)
        pipeline_logger.info(f"Added {len(new_companies)} new companies to sector '{sector_name}'")
    
    def get_next_company(self, sector_name: str) -> Optional[str]:
        """
        Get the next company URL to process for a sector.
        
        Args:
            sector_name: Name of the sector
            
        Returns:
            Company URL or None if no more companies
        """
        companies = self.load_company_queue()
        if sector_name in companies and companies[sector_name]:
            return companies[sector_name].pop(0)
        return None
    
    def get_remaining_companies_count(self, sector_name: str) -> int:
        """
        Get the number of remaining companies to process for a sector.
        
        Args:
            sector_name: Name of the sector
            
        Returns:
            Number of remaining companies
        """
        companies = self.load_company_queue()
        return len(companies.get(sector_name, []))
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get queue statistics.
        
        Returns:
            Dictionary with queue statistics
        """
        sectors = self.load_sector_queue()
        companies = self.load_company_queue()
        visited_sectors = self.load_visited_sectors()
        
        total_companies = sum(len(urls) for urls in companies.values())
        
        return {
            'total_sectors': len(sectors),
            'total_companies': total_companies,
            'visited_sectors': len(visited_sectors),
            'unvisited_sectors': len(sectors) - len(visited_sectors)
        }