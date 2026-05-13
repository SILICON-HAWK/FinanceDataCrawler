"""
Core HTTP client for the Finance Data Crawler Pipeline.
Handles requests with UA rotation, rate limiting, and retry logic.
"""

import time
import random
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

from config import USER_AGENTS, REQUEST_DELAY, MAX_RETRIES, REQUEST_TIMEOUT
from utils.logger import pipeline_logger
from utils.helpers import clean_text

class Crawler:
    """
    HTTP client with rate limiting, user-agent rotation, and retry logic.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        
    def _wait_for_rate_limit(self):
        """Ensure minimum time between requests."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < REQUEST_DELAY:
            wait_time = REQUEST_DELAY - elapsed
            pipeline_logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Get random user-agent for headers."""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def fetch_url(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a URL with retry logic.
        
        Args:
            url: URL to fetch
            headers: Optional headers (will use random UA if None)
            
        Returns:
            BeautifulSoup object or None if failed
        """
        if headers is None:
            headers = self._get_random_headers()
        
        self._wait_for_rate_limit()
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    pipeline_logger.debug(f"Successfully fetched: {url}")
                    return soup
                
                elif response.status_code == 429:
                    wait_time = 60 * (attempt + 1)  # Exponential backoff
                    pipeline_logger.warning(f"Rate limited on {url}. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    pipeline_logger.warning(f"HTTP {response.status_code} for {url}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(5 * (attempt + 1))
                        continue
                    
            except requests.exceptions.RequestException as e:
                pipeline_logger.error(f"Request failed for {url} (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
        
        pipeline_logger.error(f"Failed to fetch {url} after {MAX_RETRIES} attempts")
        return None
    
    def post_request(self, url: str, data: Dict[str, str], headers: Optional[Dict[str, str]] = None) -> Optional[BeautifulSoup]:
        """
        Make a POST request with retry logic.
        
        Args:
            url: URL to POST to
            data: Form data
            headers: Optional headers
            
        Returns:
            BeautifulSoup object or None if failed
        """
        if headers is None:
            headers = self._get_random_headers()
        
        self._wait_for_rate_limit()
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.post(
                    url,
                    data=data,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    return soup
                else:
                    pipeline_logger.warning(f"POST failed for {url}: HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                pipeline_logger.error(f"POST request failed for {url}: {e}")
                
            if attempt < MAX_RETRIES - 1:
                time.sleep(5 * (attempt + 1))
        
        return None
    
    def close(self):
        """Close the session."""
        self.session.close()