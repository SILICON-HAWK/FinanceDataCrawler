"""
Company parser for the Finance Data Crawler Pipeline.
Orchestrates the extraction of all company sections.
"""

from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from parsers.base_parser import BaseParser
from utils.logger import pipeline_logger
from utils.helpers import clean_text, safe_get

class CompanyParser(BaseParser):
    """
    Parser for company pages that orchestrates section extraction.
    """
    
    def __init__(self):
        super().__init__("company_parser")
        self.section_parsers = {}
    
    def register_section_parser(self, section_name: str, parser):
        """
        Register a section parser.
        
        Args:
            section_name: Name of the section
            parser: Section parser instance
        """
        self.section_parsers[section_name] = parser
        self.logger.info(f"Registered section parser: {section_name}")
    
    def parse_company_profile(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Parse basic company profile information.
        
        Args:
            soup: BeautifulSoup object of the company page
            
        Returns:
            Company profile data
        """
        try:
            company_info_div = soup.find('div', id='top')
            if not company_info_div:
                self.log_warning("Company info div not found")
                return None
            
            # Extract company name
            company_name = self.safe_extract_text(
                company_info_div.find('h1', class_='margin-0'),
                "Company name not found"
            )
            
            # Extract stock price and percentage change
            stock_price_div = company_info_div.find('div', class_='font-size-18')
            if stock_price_div:
                stock_price_span = stock_price_div.find('span')
                stock_price = self.safe_extract_text(stock_price_span, "0")
                stock_price = f"{stock_price} INR"
                
                percentage_change_span = stock_price_div.find('span', class_='font-size-12')
                percentage_change = self.safe_extract_text(percentage_change_span, "0%")
            else:
                stock_price = "Stock price not found"
                percentage_change = "Percentage change not found"
            
            # Extract ratios
            ratios_div = company_info_div.find('ul', id='top-ratios')
            ratios = {}
            if ratios_div:
                for ratio in ratios_div.find_all('li'):
                    name = self.safe_extract_text(ratio.find('span', class_='name'), "")
                    value = self.safe_extract_text(ratio.find('span', class_='value'), "0")
                    
                    # Clean and format value
                    cleaned_value = self._clean_ratio_value(value)
                    if name and cleaned_value:
                        ratios[name] = cleaned_value
            
            # Extract about and key points
            company_profile_div = company_info_div.find('div', class_='company-profile')
            about_and_key_points = ""
            company_links = []
            
            if company_profile_div:
                about = self.safe_extract_text(
                    company_profile_div.find('div', class_='sub'),
                    "About not found"
                )
                
                key_points = self.safe_extract_text(
                    company_profile_div.find('div', class_='sub commentary'),
                    "Key points not found"
                )
                
                about_and_key_points = f"About: {about} Key_points: {key_points}"
                
                # Extract company links
                links = company_profile_div.find_all('a', href=True)
                company_links = [link.get('href') for link in links]
            
            return {
                'company_name': company_name,
                'stock_price': stock_price,
                'percentage_change': percentage_change,
                'ratios': ratios,
                'about_and_key_points': about_and_key_points,
                'company_links': company_links
            }
            
        except Exception as e:
            self.log_error("Error parsing company profile", e)
            return None
    
    def _clean_ratio_value(self, value: str) -> str:
        """
        Clean ratio values and add appropriate units.
        
        Args:
            value: Raw ratio value
            
        Returns:
            Cleaned ratio value
        """
        cleaned = clean_text(value)
        
        # Remove commas and other formatting
        cleaned = cleaned.replace(',', '').replace('¹', '').replace('â‚', '')
        
        # Add 'INR' for currency values
        if cleaned and any(indicator in cleaned.lower() for indicator in ['cr', 'lacs', 'k']):
            cleaned = f"{cleaned} INR"
        elif cleaned and cleaned.replace('.', '', 1).isdigit():
            cleaned = f"{cleaned} INR"
        
        return cleaned
    
    def parse_section(self, soup: BeautifulSoup, section_id: str) -> Optional[Dict[str, Any]]:
        """
        Parse a specific section of the company page.
        
        Args:
            soup: BeautifulSoup object
            section_id: ID of the section to parse
            
        Returns:
            Section data or None if failed
        """
        try:
            if section_id in self.section_parsers:
                parser = self.section_parsers[section_id]
                return parser.parse(soup)
            else:
                # Use default section parsing
                section = soup.find('section', id=section_id)
                if not section:
                    self.log_warning(f"Section {section_id} not found")
                    return None
                
                # Generic table parsing
                table = section.find('table', class_='data-table')
                if table:
                    headers = [th.text.strip() for th in table.find_all('th')]
                    data = []
                    
                    for row in table.find_all('tr')[1:]:
                        cols = row.find_all('td')
                        row_data = [clean_text(col.text.strip()) for col in cols]
                        data.append(row_data)
                    
                    return {
                        'headers': headers,
                        'data': data
                    }
                else:
                    self.log_warning(f"No data table found in section {section_id}")
                    return None
                    
        except Exception as e:
            self.log_error(f"Error parsing section {section_id}", e)
            return None
    
    def parse(self, soup: BeautifulSoup, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Parse complete company page.
        
        Args:
            soup: BeautifulSoup object of the company page
            **kwargs: Additional parameters including company_url
            
        Returns:
            Complete company data or None if failed
        """
        try:
            company_url = kwargs.get('company_url', '')
            self.logger.info(f"Parsing company page: {company_url}")
            
            # Parse company profile first
            profile_data = self.parse_company_profile(soup)
            if not profile_data:
                self.log_error("Failed to parse company profile")
                return None
            
            # Parse other sections
            company_data = {
                'company_name': profile_data['company_name'],
                'profile': profile_data
            }
            
            # Parse registered sections
            for section_id, parser in self.section_parsers.items():
                self.logger.info(f"Parsing section: {section_id}")
                section_data = self.parse_section(soup, section_id)
                if section_data:
                    company_data[section_id] = section_data
                else:
                    self.log_warning(f"Failed to parse section: {section_id}")
            
            self.log_success(f"Successfully parsed company: {profile_data['company_name']}")
            return company_data
            
        except Exception as e:
            self.log_error("Error parsing company page", e)
            return None