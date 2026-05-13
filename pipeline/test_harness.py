"""
Test harness for the Finance Data Crawler Pipeline.
Provides comprehensive testing for all pipeline components.
"""

import sys
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import modules using absolute imports for testing
try:
    from config import BASE_URL, USER_AGENTS, REQUEST_DELAY
    from utils.logger import pipeline_logger
    from utils.helpers import clean_text, safe_get
except ImportError:
    # Fallback to relative imports if running as module
    from .config import BASE_URL, USER_AGENTS, REQUEST_DELAY
    from .utils.logger import pipeline_logger
    from .utils.helpers import clean_text, safe_get

class TestInfrastructure:
    """Test infrastructure setup and utilities."""
    
    def __init__(self):
        self.temp_dir = None
        self.test_data_dir = Path(__file__).parent / "test_data"
        
    def setup_test_environment(self):
        """Setup test environment with temporary directories and test data."""
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="finance_crawler_test_"))
        
        # Create test data directory
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Create mock test data
        self._create_mock_test_data()
        
        print(f"✓ Test environment setup: {self.temp_dir}")
        
    def _create_mock_test_data(self):
        """Create mock test data for testing."""
        # Mock sector data
        sector_data = {
            "sectors": [
                "https://www.screener.in/company/compare/00000001/",
                "https://www.screener.in/company/compare/00000002/"
            ]
        }
        
        # Mock company data
        company_data = {
            "Pharmaceuticals": [
                "https://www.screener.in/company/SUNPHARMA/consolidated/",
                "https://www.screener.in/company/DRREDDY/consolidated/"
            ],
            "Technology": [
                "https://www.screener.in/company/TCS/consolidated/",
                "https://www.screener.in/company/INFY/consolidated/"
            ]
        }
        
        # Mock company profile data
        company_profile = {
            "company_name": "Test Company Ltd",
            "stock_price": "1500 INR",
            "percentage_change": "+2.5%",
            "ratios": {
                "Market Cap": "50,000 Cr. INR",
                "P/E Ratio": "25.5"
            },
            "about_and_key_points": "About: Test company Key_points: Test key points",
            "company_links": ["https://example.com"]
        }
        
        # Save mock data
        with open(self.test_data_dir / "sectors.json", 'w') as f:
            json.dump(sector_data, f)
            
        with open(self.test_data_dir / "companies.json", 'w') as f:
            json.dump(company_data, f)
            
        with open(self.test_data_dir / "company_profile.json", 'w') as f:
            json.dump(company_profile, f)
    
    def cleanup_test_environment(self):
        """Cleanup test environment."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"✓ Test environment cleaned up")
    
    def get_mock_soup(self, content_type: str = "sector"):
        """Get mock BeautifulSoup object for testing."""
        from bs4 import BeautifulSoup
        
        if content_type == "sector":
            html = """
            <html>
                <title>Pharmaceuticals - Screener</title>
                <a href="/company/SUNPHARMA/consolidated/" target="_blank">Sun Pharma</a>
                <a href="/company/DRREDDY/consolidated/" target="_blank">Dr. Reddy</a>
            </html>
            """
        elif content_type == "company":
            html = """
            <html>
                <title>Sun Pharmaceutical Industries Ltd - Screener</title>
                <div id="top">
                    <h1 class="margin-0">Sun Pharmaceutical Industries Ltd</h1>
                    <div class="font-size-18">
                        <span>₹1,500</span>
                        <span class="font-size-12">+2.5%</span>
                    </div>
                    <ul id="top-ratios">
                        <li><span class="name">Market Cap</span><span class="value">50,000 Cr.</span></li>
                        <li><span class="name">P/E Ratio</span><span class="value">25.5</span></li>
                    </ul>
                </div>
            </html>
            """
        else:
            html = "<html><body>Test</body></html>"
            
        return BeautifulSoup(html, 'html.parser')


class TestConfig(unittest.TestCase):
    """Test configuration and constants."""
    
    def setUp(self):
        from config import BASE_URL, USER_AGENTS, REQUEST_DELAY
        self.base_url = BASE_URL
        self.user_agents = USER_AGENTS
        self.request_delay = REQUEST_DELAY
    
    def test_base_url(self):
        """Test base URL configuration."""
        self.assertEqual(self.base_url, "https://www.screener.in")
        
    def test_user_agents(self):
        """Test user agent configuration."""
        self.assertIsInstance(self.user_agents, list)
        self.assertGreater(len(self.user_agents), 0)
        self.assertIn("Mozilla", self.user_agents[0])
        
    def test_request_delay(self):
        """Test request delay configuration."""
        self.assertIsInstance(self.request_delay, int)
        self.assertGreater(self.request_delay, 0)


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def setUp(self):
        from utils.helpers import clean_text, safe_get, extract_company_name_from_url
        self.clean_text = clean_text
        self.safe_get = safe_get
        self.extract_company_name_from_url = extract_company_name_from_url
    
    def test_clean_text(self):
        """Test text cleaning function."""
        test_cases = [
            ("  ₹1,000  \n  +5%  ", "1,000 +5%"),
            ("<span>Test</span>", "Test"),
            ("Â¹â‚¬", ""),
            ("   multiple   spaces   ", "multiple spaces")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.clean_text(input_text)
                self.assertEqual(result, expected)
    
    def test_safe_get(self):
        """Test safe dictionary access."""
        test_dict = {'a': {'b': {'c': 'value'}}}
        
        self.assertEqual(self.safe_get(test_dict, ['a', 'b', 'c']), 'value')
        self.assertEqual(self.safe_get(test_dict, ['a', 'b', 'd']), None)
        self.assertEqual(self.safe_get(test_dict, ['x', 'y'], 'default'), 'default')
    
    def test_extract_company_name_from_url(self):
        """Test company name extraction from URL."""
        test_cases = [
            ("/company/SUNPHARMA/consolidated/", "Sun Pharma"),
            ("/company/TCS/consolidated/", "Tcs"),
            ("/company/DR-REDDY/consolidated/", "Dr Reddy"),
            ("invalid-url", None)
        ]
        
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = self.extract_company_name_from_url(url)
                self.assertEqual(result, expected)


class TestQueueManager(unittest.TestCase):
    """Test queue management functionality."""
    
    def setUp(self):
        self.test_infra = TestInfrastructure()
        self.test_infra.setup_test_environment()
        
        # Mock file paths to use test directory
        with patch('config.DATA_DIR', self.test_infra.temp_dir):
            from core.queue_manager import QueueManager
            self.queue_manager = QueueManager()
    
    def tearDown(self):
        self.test_infra.cleanup_test_environment()
    
    def test_sector_queue_operations(self):
        """Test sector queue save and load operations."""
        test_sectors = [
            "https://www.screener.in/company/compare/00000001/",
            "https://www.screener.in/company/compare/00000002/"
        ]
        
        # Save sectors
        self.queue_manager.save_sector_queue(test_sectors)
        
        # Load sectors
        loaded_sectors = self.queue_manager.load_sector_queue()
        
        self.assertEqual(len(loaded_sectors), 2)
        self.assertIn(test_sectors[0], loaded_sectors)
    
    def test_visited_sectors_tracking(self):
        """Test visited sectors tracking."""
        test_sectors = {"Pharmaceuticals", "Technology"}
        
        # Initially empty
        self.assertEqual(len(self.queue_manager.load_visited_sectors()), 0)
        
        # Mark sectors as visited
        for sector in test_sectors:
            self.queue_manager.mark_sector_visited(sector, test_sectors)
        
        # Check visited sectors
        visited = self.queue_manager.load_visited_sectors()
        self.assertEqual(len(visited), 2)
        self.assertIn("Pharmaceuticals", visited)
    
    def test_statistics(self):
        """Test queue statistics."""
        # Add test data
        self.queue_manager.save_sector_queue(["sector1", "sector2"])
        self.queue_manager.save_company_queue({"Sector1": ["company1", "company2"]})
        
        stats = self.queue_manager.get_statistics()
        
        self.assertEqual(stats['total_sectors'], 2)
        self.assertEqual(stats['total_companies'], 2)


class TestStorage(unittest.TestCase):
    """Test storage functionality."""
    
    def setUp(self):
        self.test_infra = TestInfrastructure()
        self.test_infra.setup_test_environment()
        
        # Mock companies directory
        with patch('config.COMPANIES_DIR', self.test_infra.temp_dir):
            from core.storage import Storage
            self.storage = Storage()
    
    def tearDown(self):
        self.test_infra.cleanup_test_environment()
    
    def test_save_and_load_json(self):
        """Test JSON save and load operations."""
        test_data = {"test": "data", "number": 123}
        file_path = self.test_infra.temp_dir / "test.json"
        
        # Save data
        result = self.storage.save_json(test_data, file_path)
        self.assertTrue(result)
        self.assertTrue(file_path.exists())
        
        # Load data
        loaded_data = self.storage.load_json(file_path)
        self.assertEqual(loaded_data, test_data)
    
    def test_company_data_operations(self):
        """Test company data save and load operations."""
        test_company_data = {
            "company_name": "Test Company",
            "profile": {"stock_price": "1000 INR"}
        }
        
        # Save company data
        result = self.storage.save_company_data("Test Company", test_company_data)
        self.assertTrue(result)
        
        # Load company data
        loaded_data = self.storage.load_company_data("Test Company")
        self.assertEqual(loaded_data["company_name"], "Test Company")
    
    def test_storage_statistics(self):
        """Test storage statistics."""
        # Add test company data
        test_data = {"company_name": "Test Company"}
        self.storage.save_company_data("Test Company", test_data)
        
        stats = self.storage.get_storage_stats()
        
        self.assertEqual(stats['total_companies'], 1)
        self.assertGreater(stats['total_size_bytes'], 0)


class TestParsers(unittest.TestCase):
    """Test parser functionality."""
    
    def setUp(self):
        self.test_infra = TestInfrastructure()
        self.test_infra.setup_test_environment()
        self.mock_soup = self.test_infra.get_mock_soup()
    
    def tearDown(self):
        self.test_infra.cleanup_test_environment()
    
    @patch('bs4.BeautifulSoup')
    def test_sector_parser(self, mock_bs4):
        """Test sector parser functionality."""
        from parsers.sector_parser import SectorParser
        
        # Mock BeautifulSoup
        mock_soup = self.test_infra.get_mock_soup("sector")
        parser = SectorParser()
        
        # Test sector name extraction
        sector_name = parser.extract_sector_name(mock_soup)
        self.assertEqual(sector_name, "Pharmaceuticals")
        
        # Test company link extraction
        company_links = parser.extract_company_links(mock_soup)
        self.assertEqual(len(company_links), 2)
        self.assertIn("SUNPHARMA", company_links[0])
    
    @patch('bs4.BeautifulSoup')
    def test_company_parser(self, mock_bs4):
        """Test company parser functionality."""
        from parsers.company_parser import CompanyParser
        
        # Mock BeautifulSoup
        mock_soup = self.test_infra.get_mock_soup("company")
        parser = CompanyParser()
        
        # Test company profile parsing
        profile_data = parser.parse_company_profile(mock_soup)
        
        self.assertIsNotNone(profile_data)
        self.assertEqual(profile_data['company_name'], "Sun Pharmaceutical Industries Ltd")
        self.assertEqual(profile_data['stock_price'], "1500 INR")
        self.assertIn("Market Cap", profile_data['ratios'])


class TestCrawler(unittest.TestCase):
    """Test crawler functionality (mocked for testing)."""
    
    def setUp(self):
        from core.crawler import Crawler
        self.crawler = Crawler()
    
    @patch('requests.Session.get')
    def test_fetch_url_success(self, mock_get):
        """Test successful URL fetching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_get.return_value = mock_response
        
        result = self.crawler.fetch_url("https://example.com")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.find('body').text, "Test")
    
    @patch('requests.Session.get')
    def test_fetch_url_failure(self, mock_get):
        """Test URL fetching failure."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.crawler.fetch_url("https://example.com")
        
        self.assertIsNone(result)


class TestPipelineIntegration(unittest.TestCase):
    """Test pipeline integration."""
    
    def setUp(self):
        self.test_infra = TestInfrastructure()
        self.test_infra.setup_test_environment()
    
    def tearDown(self):
        self.test_infra.cleanup_test_environment()
    
    def test_full_pipeline_simulation(self):
        """Test complete pipeline simulation with mocked components."""
        # Mock all external dependencies
        with patch('core.crawler.Crawler') as mock_crawler_class, \
             patch('core.queue_manager.QueueManager') as mock_queue_manager_class, \
             patch('core.storage.Storage') as mock_storage_class, \
             patch('parsers.sector_parser.SectorParser') as mock_sector_parser_class, \
             patch('parsers.company_parser.CompanyParser') as mock_company_parser_class:
            
            # Setup mocks
            mock_crawler = Mock()
            mock_crawler.fetch_url.return_value = self.test_infra.get_mock_soup("sector")
            mock_crawler_class.return_value = mock_crawler
            
            mock_queue_manager = Mock()
            mock_queue_manager.load_sector_queue.return_value = ["https://example.com/sector"]
            mock_queue_manager.load_visited_sectors.return_value = set()
            mock_queue_manager_class.return_value = mock_queue_manager
            
            mock_storage = Mock()
            mock_storage.save_company_data.return_value = True
            mock_storage_class.return_value = mock_storage
            
            mock_sector_parser = Mock()
            mock_sector_parser.parse.return_value = {
                'sector_name': 'Test Sector',
                'company_links': ['https://example.com/company']
            }
            mock_sector_parser_class.return_value = mock_sector_parser
            
            mock_company_parser = Mock()
            mock_company_parser.parse.return_value = {
                'company_name': 'Test Company',
                'profile': {'stock_price': '1000 INR'}
            }
            mock_company_parser_class.return_value = mock_company_parser
            
            # Import and test pipeline
            from main import FinanceDataPipeline
            pipeline = FinanceDataPipeline()
            
            # Test sector discovery
            pipeline.run_sector_discovery()
            
            # Test company discovery
            pipeline.run_company_discovery(timeout_minutes=1)
            
            # Test company extraction
            pipeline.run_company_extraction(max_companies=1)
            
            # Verify calls were made
            mock_crawler.fetch_url.assert_called()
            mock_sector_parser.parse.assert_called()
            mock_company_parser.parse.assert_called()
            mock_storage.save_company_data.assert_called()


def run_all_tests():
    """Run all test suites."""
    print("=" * 60)
    print("Finance Data Crawler Pipeline - Test Harness")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestConfig,
        TestUtils,
        TestQueueManager,
        TestStorage,
        TestParsers,
        TestCrawler,
        TestPipelineIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)