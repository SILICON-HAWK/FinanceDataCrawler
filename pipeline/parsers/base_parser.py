"""
Base parser class for the Finance Data Crawler Pipeline.
Provides common functionality for all parsers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from utils.logger import pipeline_logger
from utils.helpers import clean_text, safe_get

class BaseParser(ABC):
    """
    Abstract base class for all parsers.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = pipeline_logger.getChild(name)
    
    @abstractmethod
    def parse(self, soup: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Parse HTML content and extract data.
        
        Args:
            soup: BeautifulSoup object containing HTML
            **kwargs: Additional parsing parameters
            
        Returns:
            Extracted data or None if failed
        """
        pass
    
    def log_success(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log successful parsing."""
        self.logger.info(message)
        if data:
            self.logger.debug(f"Extracted data: {data}")
    
    def log_error(self, message: str, error: Optional[Exception] = None):
        """Log parsing errors."""
        self.logger.error(message)
        if error:
            self.logger.error(f"Error details: {error}")
    
    def log_warning(self, message: str):
        """Log warnings."""
        self.logger.warning(message)
    
    def safe_extract_text(self, element, default: str = "") -> str:
        """
        Safely extract text from an HTML element.
        
        Args:
            element: BeautifulSoup element
            default: Default value if element is None
            
        Returns:
            Extracted text or default
        """
        if element:
            text = element.get_text(strip=True)
            return clean_text(text)
        return default
    
    def safe_extract_attribute(self, element, attribute: str, default: str = "") -> str:
        """
        Safely extract attribute from an HTML element.
        
        Args:
            element: BeautifulSoup element
            attribute: Attribute name
            default: Default value if element/attribute not found
            
        Returns:
            Attribute value or default
        """
        if element and hasattr(element, 'get'):
            value = element.get(attribute, default)
            return clean_text(value) if value else default
        return default