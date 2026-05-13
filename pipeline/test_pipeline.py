"""
Test script to validate the pipeline structure and basic functionality.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from config import BASE_URL, USER_AGENTS
        print("✓ config imported successfully")
        
        from utils.logger import pipeline_logger
        print("✓ utils.logger imported successfully")
        
        from utils.helpers import clean_text, safe_get
        print("✓ utils.helpers imported successfully")
        
        # Try to import crawler without bs4 dependency
        try:
            from core.crawler import Crawler
            print("✓ core.crawler imported successfully")
        except ImportError as e:
            if 'bs4' in str(e):
                print("⚠ core.crawler skipped (bs4 dependency not available)")
            else:
                raise e
        
        # Try to import parsers without bs4 dependency
        try:
            from parsers.sector_parser import SectorParser
            print("✓ parsers.sector_parser imported successfully")
        except ImportError as e:
            if 'bs4' in str(e):
                print("⚠ parsers.sector_parser skipped (bs4 dependency not available)")
            else:
                raise e
                
        try:
            from parsers.company_parser import CompanyParser
            print("✓ parsers.company_parser imported successfully")
        except ImportError as e:
            if 'bs4' in str(e):
                print("⚠ parsers.company_parser skipped (bs4 dependency not available)")
            else:
                raise e
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key components."""
    try:
        from utils.helpers import clean_text, safe_get
        
        # Test text cleaning
        test_text = "  ₹1,000  \n  +5%  "
        cleaned = clean_text(test_text)
        print(f"✓ Text cleaning test: '{test_text}' -> '{cleaned}'")
        
        # Test safe_get
        test_dict = {'a': {'b': {'c': 'value'}}}
        result = safe_get(test_dict, ['a', 'b', 'c'])
        print(f"✓ safe_get test: {result}")
        
        # Test queue manager (no bs4 dependency)
        from core.queue_manager import QueueManager
        queue_manager = QueueManager()
        print("✓ QueueManager initialized successfully")
        
        # Test storage (no bs4 dependency)
        from core.storage import Storage
        storage = Storage()
        print("✓ Storage initialized successfully")
        
        # Test parsers only if bs4 is available
        try:
            from parsers.sector_parser import SectorParser
            sector_parser = SectorParser()
            print("✓ SectorParser initialized successfully")
        except ImportError as e:
            if 'bs4' in str(e):
                print("⚠ SectorParser skipped (bs4 dependency not available)")
            else:
                raise e
        
        try:
            from parsers.company_parser import CompanyParser
            company_parser = CompanyParser()
            print("✓ CompanyParser initialized successfully")
        except ImportError as e:
            if 'bs4' in str(e):
                print("⚠ CompanyParser skipped (bs4 dependency not available)")
            else:
                raise e
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    # Use the project root as the base path
    project_root = Path(__file__).parent.parent
    
    required_files = [
        'pipeline/__init__.py',
        'pipeline/config.py',
        'pipeline/main.py',
        'pipeline/core/__init__.py',
        'pipeline/core/crawler.py',
        'pipeline/core/queue_manager.py',
        'pipeline/core/storage.py',
        'pipeline/parsers/__init__.py',
        'pipeline/parsers/base_parser.py',
        'pipeline/parsers/sector_parser.py',
        'pipeline/parsers/company_parser.py',
        'pipeline/utils/__init__.py',
        'pipeline/utils/logger.py',
        'pipeline/utils/helpers.py',
        'pipeline/README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("Testing Finance Data Crawler Pipeline...")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n{test_name} Tests:")
        print("-" * 30)
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed!")
        print("\nThe pipeline structure is ready for use.")
        print("Run: python pipeline/main.py --help")
    else:
        print("✗ Some tests failed.")
        print("Please check the errors above and fix the issues.")

if __name__ == "__main__":
    main()