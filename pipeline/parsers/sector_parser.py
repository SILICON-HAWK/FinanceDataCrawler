"""
Sector parser for the Finance Data Crawler Pipeline.
Handles parsing sector pages and extracting company links.
"""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup

from config import BASE_URL
from parsers.base_parser import BaseParser
from utils.helpers import clean_text, extract_company_name_from_url

class SectorParser(BaseParser):
    """
    Parser for sector pages to extract company links.
    """
    
    def __init__(self):
        super().__init__("sector_parser")
    
    def extract_sector_name(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract sector name from the page title.
        
        Args:
            soup: BeautifulSoup object of the sector page
            
        Returns:
            Sector name or None if not found
        """
        try:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()
                # Remove " - Screener" from the title
                sector_name = title.replace("- Screener", "").strip()
                return sector_name
            else:
                self.log_warning("Sector name not found - no title tag")
                return None
        except Exception as e:
            self.log_error("Error extracting sector name", e)
            return None
    
    def extract_company_links(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract company URLs from a sector page.
        
        Args:
            soup: BeautifulSoup object of the sector page
            
        Returns:
            List of company URLs
        """
        try:
            company_links = []
            
            # Find all links that look like company links
            # These typically have target="_blank" and contain company names
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                
                # Check if it's a company link
                if self._is_company_link(href):
                    absolute_url = self._make_absolute_url(href)
                    if absolute_url:
                        company_links.append(absolute_url)
                        self.logger.debug(f"Found company link: {absolute_url}")
            
            self.log_success(f"Extracted {len(company_links)} company links")
            return company_links
            
        except Exception as e:
            self.log_error("Error extracting company links", e)
            return []
    
    def _is_company_link(self, href: str) -> bool:
        """
        Check if a href is a company link.
        
        Args:
            href: The href to check
            
        Returns:
            True if it's a company link
        """
        # Company links typically contain "/company/" and don't contain common non-company patterns
        if not href:
            return False
        
        href = href.lower().strip()
        
        # Must contain /company/
        if '/company/' not in href:
            return False
        
        # Should not contain these patterns (usually not company pages)
        exclude_patterns = [
            '/explore/',
            '/company/compare/',
            '/sector/',
            '/industry/',
            '/watchlist/',
            '/portfolio/'
        ]
        
        for pattern in exclude_patterns:
            if pattern in href:
                return False
        
        # Should contain at least one company identifier
        company_indicators = ['consolidated/', '/', '/5', '/6', '/7', '/8', '/9']
        return any(indicator in href for indicator in company_indicators)
    
    def _make_absolute_url(self, href: str) -> Optional[str]:
        """
        Convert relative URL to absolute URL.
        
        Args:
            href: Relative URL
            
        Returns:
            Absolute URL or None
        """
        if href.startswith('http'):
            return href
        
        if href.startswith('/'):
            return f"{BASE_URL}{href}"
        
        # Handle relative URLs
        if not href.startswith('#'):
            return f"{BASE_URL}/{href}"
        
        return None
    
    def parse(self, soup: BeautifulSoup, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Parse sector page and extract company data.
        
        Args:
            soup: BeautifulSoup object of the sector page
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with sector name and company links
        """
        try:
            # Extract sector name
            sector_name = self.extract_sector_name(soup)
            if not sector_name:
                self.log_error("Could not extract sector name")
                return None
            
            # Extract company links
            company_links = self.extract_company_links(soup)
            
            # Filter out invalid links
            valid_links = [link for link in company_links if link]
            
            result = {
                'sector_name': sector_name,
                'company_links': valid_links,
                'total_companies': len(valid_links)
            }
            
            self.log_success(f"Parsed sector: {sector_name}", result)
            return result
            
        except Exception as e:
            self.log_error("Error parsing sector page", e)
            return None