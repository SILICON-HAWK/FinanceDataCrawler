"""
Progress tracking module for Finance Data Crawler
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Tracks crawler progress and statistics"""

    def __init__(self, progress_file: Path):
        """
        Initialize progress tracker.

        Args:
            progress_file (Path): Path to progress JSON file
        """
        self.progress_file = progress_file
        self.progress_data = {
            'session_start': None,
            'session_end': None,
            'total_sectors': 0,
            'sectors_processed': 0,
            'total_companies': 0,
            'companies_processed': 0,
            'companies_failed': 0,
            'errors': [],
            'current_sector': None,
            'last_company': None,
            'statistics': {}
        }
        self._load_progress()

    def _load_progress(self):
        """Load progress from disk"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    saved_data = json.load(f)
                    self.progress_data.update(saved_data)
                logger.info("Loaded progress data")
            except Exception as e:
                logger.error(f"Error loading progress: {e}")

    def save_progress(self):
        """Save progress to disk"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress_data, f, indent=4)
            logger.debug("Progress saved")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")

    def start_session(self, total_sectors: int = 0):
        """
        Start a new crawling session.

        Args:
            total_sectors (int): Total number of sectors to process
        """
        self.progress_data['session_start'] = datetime.now().isoformat()
        self.progress_data['session_end'] = None
        self.progress_data['total_sectors'] = total_sectors
        self.save_progress()
        logger.info(f"Started new session with {total_sectors} sectors")

    def end_session(self):
        """End the current crawling session"""
        self.progress_data['session_end'] = datetime.now().isoformat()
        self.save_progress()
        logger.info("Ended session")

    def update_sector(self, sector_name: str, total_companies: int = 0):
        """
        Update current sector being processed.

        Args:
            sector_name (str): Name of the sector
            total_companies (int): Total companies in this sector
        """
        self.progress_data['current_sector'] = sector_name
        self.progress_data['sectors_processed'] += 1
        if total_companies > 0:
            self.progress_data['total_companies'] += total_companies
        self.save_progress()
        logger.info(f"Processing sector: {sector_name} ({total_companies} companies)")

    def update_company(self, company_name: str, company_url: str, success: bool = True, error: str = None):
        """
        Update company processing status.

        Args:
            company_name (str): Name of the company
            company_url (str): URL of the company
            success (bool): Whether processing was successful
            error (str, optional): Error message if failed
        """
        self.progress_data['last_company'] = {
            'name': company_name,
            'url': company_url,
            'timestamp': datetime.now().isoformat(),
            'success': success
        }

        if success:
            self.progress_data['companies_processed'] += 1
        else:
            self.progress_data['companies_failed'] += 1
            if error:
                self.progress_data['errors'].append({
                    'company': company_name,
                    'url': company_url,
                    'error': error,
                    'timestamp': datetime.now().isoformat()
                })

        self.save_progress()
        logger.info(f"{'Successfully processed' if success else 'Failed to process'} company: {company_name}")

    def get_statistics(self) -> Dict:
        """
        Get current progress statistics.

        Returns:
            Dict: Statistics dictionary
        """
        stats = {
            'session_start': self.progress_data.get('session_start'),
            'session_end': self.progress_data.get('session_end'),
            'total_sectors': self.progress_data.get('total_sectors', 0),
            'sectors_processed': self.progress_data.get('sectors_processed', 0),
            'total_companies': self.progress_data.get('total_companies', 0),
            'companies_processed': self.progress_data.get('companies_processed', 0),
            'companies_failed': self.progress_data.get('companies_failed', 0),
            'current_sector': self.progress_data.get('current_sector'),
            'last_company': self.progress_data.get('last_company'),
            'error_count': len(self.progress_data.get('errors', []))
        }

        # Calculate progress percentages
        if stats['total_sectors'] > 0:
            stats['sectors_progress'] = (stats['sectors_processed'] / stats['total_sectors']) * 100
        else:
            stats['sectors_progress'] = 0

        if stats['total_companies'] > 0:
            stats['companies_progress'] = (stats['companies_processed'] / stats['total_companies']) * 100
        else:
            stats['companies_progress'] = 0

        # Calculate success rate
        total_attempts = stats['companies_processed'] + stats['companies_failed']
        if total_attempts > 0:
            stats['success_rate'] = (stats['companies_processed'] / total_attempts) * 100
        else:
            stats['success_rate'] = 0

        return stats

    def get_recent_errors(self, limit: int = 10) -> list:
        """
        Get recent errors.

        Args:
            limit (int): Maximum number of errors to return

        Returns:
            list: List of recent errors
        """
        errors = self.progress_data.get('errors', [])
        return errors[-limit:]

    def clear_errors(self):
        """Clear all recorded errors"""
        self.progress_data['errors'] = []
        self.save_progress()
        logger.info("Cleared error log")

    def reset(self):
        """Reset all progress data"""
        self.progress_data = {
            'session_start': None,
            'session_end': None,
            'total_sectors': 0,
            'sectors_processed': 0,
            'total_companies': 0,
            'companies_processed': 0,
            'companies_failed': 0,
            'errors': [],
            'current_sector': None,
            'last_company': None,
            'statistics': {}
        }
        self.save_progress()
        logger.info("Reset all progress data")

    def print_summary(self):
        """Print a summary of the current progress"""
        stats = self.get_statistics()

        print("\n" + "="*60)
        print("CRAWLER PROGRESS SUMMARY")
        print("="*60)

        if stats['session_start']:
            print(f"Session Start: {stats['session_start']}")
        if stats['session_end']:
            print(f"Session End: {stats['session_end']}")

        print(f"\nSectors: {stats['sectors_processed']}/{stats['total_sectors']} ({stats['sectors_progress']:.1f}%)")
        print(f"Companies: {stats['companies_processed']}/{stats['total_companies']} ({stats['companies_progress']:.1f}%)")
        print(f"Failed: {stats['companies_failed']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")

        if stats['current_sector']:
            print(f"\nCurrently processing: {stats['current_sector']}")

        if stats['last_company']:
            last = stats['last_company']
            print(f"Last company: {last['name']} ({'Success' if last['success'] else 'Failed'})")

        if stats['error_count'] > 0:
            print(f"\nTotal Errors: {stats['error_count']}")
            print("Recent errors available with --show-errors flag")

        print("="*60 + "\n")
