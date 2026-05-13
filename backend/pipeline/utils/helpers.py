"""
Utility functions for data cleaning and processing.
"""

import re
from typing import Any, Dict, List, Optional, Union

from ..config import CURRENCY_SYMBOLS, ENCODING_ERRORS, SPACE_CHARS, SPECIAL_CHARS

def clean_text(text: str) -> str:
    """
    Clean and normalize text extracted from HTML.
    
    Args:
        text: Raw text from HTML parsing
        
    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""
    
    # Remove special characters and symbols
    for char in SPECIAL_CHARS:
        text = text.replace(char, '')
    
    # Remove currency symbols
    for symbol in CURRENCY_SYMBOLS:
        text = text.replace(symbol, '')
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Handle encoding issues
    try:
        text = text.encode('ascii', ENCODING_ERRORS).decode('ascii')
    except:
        pass
    
    return text.strip()

def clean_numeric_value(text: str) -> str:
    """
    Clean numeric values and add appropriate units.
    
    Args:
        text: Raw numeric text from HTML
        
    Returns:
        Cleaned numeric string with units
    """
    if not text:
        return "0"
    
    cleaned = clean_text(text)
    
    # Remove commas
    cleaned = cleaned.replace(',', '')
    
    # Add 'INR' currency if it seems to be a financial value
    if cleaned and not cleaned.lower().endswith(('inr', '%', 'cr', 'lacs', 'k')):
        # Check if it looks like a currency value
        if cleaned.replace('.', '', 1).isdigit():
            cleaned = f"{cleaned} INR"
        # Check if it's a percentage
        elif '%' in cleaned:
            cleaned = cleaned.replace('%', '').strip()
    
    return cleaned

def extract_company_name_from_url(url: str) -> Optional[str]:
    """
    Extract company name from Screener.in URL.
    
    Args:
        url: Company URL from Screener.in
        
    Returns:
        Company name or None if cannot be extracted
    """
    try:
        # Extract the part after /company/ and before /
        parts = url.split('/')
        company_part = None
        
        for part in parts:
            if part and not part.startswith(('http', 'https', 'www', 'company', 'consolidated')):
                company_part = part
                break
        
        if company_part:
            # Clean up and return
            return company_part.replace('-', ' ').replace('_', ' ').title()
        
        return None
    except Exception:
        return None

def safe_get(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """
    Safely get nested dictionary values using a list of keys.
    
    Args:
        data: Dictionary to search
        keys: List of keys to traverse
        default: Default value if not found
        
    Returns:
        Value or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def flatten_nested_dict(nested_dict: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested dictionary into a single-level dictionary.
    
    Args:
        nested_dict: Nested dictionary to flatten
        parent_key: Parent key for nested items
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_nested_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

def validate_financial_data(data: Dict[str, Any]) -> bool:
    """
    Basic validation to ensure financial data structure is valid.
    
    Args:
        data: Financial data dictionary
        
    Returns:
        True if data appears valid, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    # Check for required top-level keys
    required_keys = ['company_name']
    for key in required_keys:
        if key not in data:
            return False
    
    return True