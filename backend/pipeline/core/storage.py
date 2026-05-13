"""
Storage interface for the Finance Data Crawler Pipeline.
Handles saving and loading JSON data with proper error handling.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import COMPANIES_DIR
from ..utils.logger import pipeline_logger
from ..utils.helpers import validate_financial_data

class Storage:
    """
    Handles data storage operations for the pipeline.
    """
    
    def __init__(self):
        self.companies_dir = COMPANIES_DIR
        
    def save_json(self, data: Any, file_path: Path) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            file_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            pipeline_logger.info(f"Saved data to: {file_path}")
            return True
            
        except Exception as e:
            pipeline_logger.error(f"Error saving to {file_path}: {e}")
            return False
    
    def load_json(self, file_path: Path) -> Optional[Any]:
        """
        Load data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Loaded data or None if error
        """
        try:
            if not file_path.exists():
                pipeline_logger.warning(f"File not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pipeline_logger.debug(f"Loaded data from: {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            pipeline_logger.error(f"Error parsing JSON from {file_path}: {e}")
            return None
        except Exception as e:
            pipeline_logger.error(f"Error loading from {file_path}: {e}")
            return None
    
    def save_company_data(self, company_name: str, data: Dict[str, Any]) -> bool:
        """
        Save complete company data to a JSON file.
        
        Args:
            company_name: Name of the company
            data: Company data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        # Validate data before saving
        if not validate_financial_data(data):
            pipeline_logger.error(f"Invalid data structure for {company_name}")
            return False
        
        # Clean company name for filename
        safe_name = self._sanitize_filename(company_name)
        file_path = self.companies_dir / f"{safe_name}.json"
        
        return self.save_json(data, file_path)
    
    def load_company_data(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Load company data from JSON file.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Company data or None if not found
        """
        safe_name = self._sanitize_filename(company_name)
        file_path = self.companies_dir / f"{safe_name}.json"
        
        return self.load_json(file_path)
    
    def save_intermediate_data(self, section_name: str, data: Dict[str, Any], temp_dir: Path) -> bool:
        """
        Save intermediate data during processing.
        
        Args:
            section_name: Name of the data section
            data: Data to save
            temp_dir: Directory to save in
            
        Returns:
            True if successful, False otherwise
        """
        file_path = temp_dir / f"{section_name}.json"
        return self.save_json(data, file_path)
    
    def list_companies(self) -> List[str]:
        """
        List all companies that have been processed.
        
        Returns:
            List of company names
        """
        companies = []
        try:
            for file_path in self.companies_dir.glob("*.json"):
                company_name = file_path.stem
                companies.append(company_name)
        except Exception as e:
            pipeline_logger.error(f"Error listing companies: {e}")
        
        return companies
    
    def get_company_count(self) -> int:
        """
        Get the number of companies that have been processed.
        
        Returns:
            Number of companies
        """
        return len(self.list_companies())
    
    def company_exists(self, company_name: str) -> bool:
        safe_name = self._sanitize_filename(company_name)
        file_path = self.companies_dir / f"{safe_name}.json"
        return file_path.exists()

    def delete_company_data(self, company_name: str) -> bool:
        """
        Delete company data file.
        
        Args:
            company_name: Name of the company
            
        Returns:
            True if successful, False otherwise
        """
        safe_name = self._sanitize_filename(company_name)
        file_path = self.companies_dir / f"{safe_name}.json"
        
        try:
            if file_path.exists():
                file_path.unlink()
                pipeline_logger.info(f"Deleted company data: {company_name}")
                return True
            else:
                pipeline_logger.warning(f"Company data not found: {company_name}")
                return False
        except Exception as e:
            pipeline_logger.error(f"Error deleting {company_name}: {e}")
            return False
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize company name for use as filename.
        
        Args:
            name: Company name
            
        Returns:
            Safe filename
        """
        # Remove characters that are invalid in filenames
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        return safe_name
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            total_files = 0
            total_size = 0
            
            for file_path in self.companies_dir.glob("*.json"):
                total_files += 1
                total_size += file_path.stat().st_size
            
            return {
                'total_companies': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'companies_directory': str(self.companies_dir)
            }
        except Exception as e:
            pipeline_logger.error(f"Error getting storage stats: {e}")
            return {
                'total_companies': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'error': str(e)
            }