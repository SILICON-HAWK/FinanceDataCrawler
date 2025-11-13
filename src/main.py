#!/usr/bin/env python3
"""
Finance Data Crawler - CLI Interface
Command-line interface for crawling Indian stock market financial data
"""
import sys
import json
import logging
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.crawler import FinanceCrawler
from src.storage import StorageManager
from src.deduplication import DeduplicationManager
from src.progress import ProgressTracker
from src.validation import DataValidator


def setup_logging(log_level: str):
    """Setup logging configuration"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    Config.ensure_directories()

    logging.basicConfig(
        level=numeric_level,
        format=Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def cmd_crawl(args):
    """Handle crawl command"""
    logger = logging.getLogger(__name__)
    logger.info("Starting crawl operation...")

    # Initialize components
    storage_manager = StorageManager(Config)
    dedup_manager = DeduplicationManager(Config.VISITED_SECTORS_FILE, Config.VISITED_COMPANIES_FILE)
    progress_tracker = ProgressTracker(Config.PROGRESS_FILE)
    crawler = FinanceCrawler(Config, storage_manager, dedup_manager, progress_tracker)

    try:
        # Load or fetch sector URLs
        if args.sectors_file and Path(args.sectors_file).exists():
            logger.info(f"Loading sectors from {args.sectors_file}")
            with open(args.sectors_file, 'r') as f:
                sector_urls = json.load(f)
        else:
            logger.info("Fetching sector URLs from explore page...")
            sector_urls = crawler.fetch_sector_urls()

            # Save sector URLs
            with open(Config.SECTORS_QUEUE_FILE, 'w') as f:
                json.dump(sector_urls, f, indent=4)
            logger.info(f"Saved {len(sector_urls)} sector URLs to {Config.SECTORS_QUEUE_FILE}")

        if not sector_urls:
            logger.error("No sector URLs available")
            return

        # Filter unvisited sectors if requested
        if args.skip_visited:
            original_count = len(sector_urls)
            # We need to fetch and check sector names (this is expensive, so we'll skip this optimization for now)
            logger.info(f"Processing {original_count} sectors (skip_visited requires fetching each sector)")

        # Apply limit
        if args.limit:
            sector_urls = sector_urls[:args.limit]
            logger.info(f"Limited to {len(sector_urls)} sectors")

        # Crawl sectors
        logger.info(f"Starting to crawl {len(sector_urls)} sectors...")
        results = crawler.crawl_sectors(sector_urls, timeout=args.timeout)

        # Print summary
        print("\n" + "="*60)
        print("CRAWL COMPLETED")
        print("="*60)
        print(f"Sectors processed: {results['sectors_processed']}")
        print(f"Sectors skipped: {results['sectors_skipped']}")
        print(f"Companies found: {results['companies_found']}")
        print(f"Companies processed: {results['companies_processed']}")
        print(f"Companies failed: {results['companies_failed']}")
        if results['timeout_reached']:
            print(f"⚠ Timeout reached: {args.timeout}s")
        print("="*60 + "\n")

        # Show progress
        progress_tracker.print_summary()

    except KeyboardInterrupt:
        logger.info("Crawl interrupted by user")
        print("\nCrawl interrupted by user")
    except Exception as e:
        logger.error(f"Error during crawl: {e}", exc_info=True)
        print(f"\nError: {e}")
    finally:
        crawler.close()
        storage_manager.close()


def cmd_status(args):
    """Handle status command"""
    progress_tracker = ProgressTracker(Config.PROGRESS_FILE)
    dedup_manager = DeduplicationManager(Config.VISITED_SECTORS_FILE, Config.VISITED_COMPANIES_FILE)
    storage_manager = StorageManager(Config)

    print("\n" + "="*60)
    print("CRAWLER STATUS")
    print("="*60)

    # Progress statistics
    progress_tracker.print_summary()

    # Deduplication statistics
    dedup_stats = dedup_manager.get_statistics()
    print("\nDEDUPLICATION STATUS")
    print("-"*60)
    print(f"Visited sectors: {dedup_stats['visited_sectors']}")
    print(f"Visited companies: {dedup_stats['visited_companies']}")

    # Storage statistics
    storage_stats = storage_manager.get_statistics()
    print("\nSTORAGE STATUS")
    print("-"*60)
    print(f"JSON companies: {storage_stats['json_companies']}")
    if 'total_companies' in storage_stats:
        print(f"Database companies: {storage_stats['total_companies']}")
        print(f"Successful crawls: {storage_stats['successful_crawls']}")
        print(f"Failed crawls: {storage_stats['failed_crawls']}")

    # Show recent errors if requested
    if args.show_errors:
        errors = progress_tracker.get_recent_errors(args.error_limit)
        if errors:
            print(f"\nRECENT ERRORS (last {len(errors)})")
            print("-"*60)
            for error in errors:
                print(f"Company: {error['company']}")
                print(f"Error: {error['error']}")
                print(f"Time: {error['timestamp']}")
                print()

    storage_manager.close()


def cmd_list(args):
    """Handle list command"""
    storage_manager = StorageManager(Config)

    companies = storage_manager.list_companies(from_db=args.from_db)

    print(f"\nFound {len(companies)} companies:\n")
    for i, company in enumerate(companies, 1):
        print(f"{i}. {company}")

    storage_manager.close()


def cmd_validate(args):
    """Handle validate command"""
    storage_manager = StorageManager(Config)
    validator = DataValidator(Config)

    if args.company:
        # Validate single company
        company_data = storage_manager.load_company_data(args.company, from_db=args.from_db)

        if not company_data:
            print(f"Company not found: {args.company}")
            return

        is_valid, errors = validator.validate_company_data(company_data)
        quality_score = validator.get_data_quality_score(company_data)

        print(f"\nValidation Results for: {args.company}")
        print("="*60)
        print(f"Status: {'✓ VALID' if is_valid else '✗ INVALID'}")
        print(f"Quality Score: {quality_score:.1f}/100")

        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"  - {error}")

        freshness = validator.check_data_freshness(company_data)
        if freshness:
            print(f"\n{freshness}")

    else:
        # Validate all companies
        companies = storage_manager.list_companies(from_db=args.from_db)
        print(f"Validating {len(companies)} companies...\n")

        companies_data = []
        for company in companies:
            company_data = storage_manager.load_company_data(company, from_db=args.from_db)
            if company_data:
                companies_data.append(company_data)

        summary = validator.validate_batch(companies_data)

        print("Validation Summary")
        print("="*60)
        print(f"Total companies: {summary['total']}")
        print(f"Valid: {summary['valid']}")
        print(f"Invalid: {summary['invalid']}")
        print(f"Average quality score: {summary['average_quality_score']:.1f}/100")

        if summary['errors_by_type']:
            print("\nCommon Errors:")
            for error, count in summary['errors_by_type'].items():
                print(f"  - {error}: {count} occurrences")

    storage_manager.close()


def cmd_reset(args):
    """Handle reset command"""
    dedup_manager = DeduplicationManager(Config.VISITED_SECTORS_FILE, Config.VISITED_COMPANIES_FILE)
    progress_tracker = ProgressTracker(Config.PROGRESS_FILE)

    if args.all:
        print("Resetting all data (visited sectors, companies, and progress)...")
        dedup_manager.reset_all()
        progress_tracker.reset()
        print("✓ All data reset")

    elif args.sectors:
        print("Resetting visited sectors...")
        dedup_manager.reset_sectors()
        print("✓ Visited sectors reset")

    elif args.companies:
        print("Resetting visited companies...")
        dedup_manager.reset_companies()
        print("✓ Visited companies reset")

    elif args.progress:
        print("Resetting progress data...")
        progress_tracker.reset()
        print("✓ Progress data reset")

    elif args.errors:
        print("Clearing error log...")
        progress_tracker.clear_errors()
        print("✓ Error log cleared")

    else:
        print("Please specify what to reset: --all, --sectors, --companies, --progress, or --errors")


def cmd_config(args):
    """Handle config command"""
    if args.show:
        print("\nCurrent Configuration")
        print("="*60)
        print(f"Rate limit interval: {Config.RATE_LIMIT_INTERVAL}s")
        print(f"Request timeout: {Config.REQUEST_TIMEOUT}s")
        print(f"Max retries: {Config.MAX_RETRIES}")
        print(f"Sector page limit: {Config.SECTOR_PAGE_LIMIT}")
        print(f"Database type: {Config.DB_TYPE}")
        print(f"Log level: {Config.LOG_LEVEL}")
        print("\nPaths:")
        print(f"  Companies dir: {Config.COMPANIES_DIR}")
        print(f"  Database: {Config.SQLITE_DB_PATH}")
        print(f"  Log file: {Config.LOG_FILE}")

    elif args.save:
        Config.save_config(args.save)
        print(f"✓ Configuration saved to {args.save}")

    elif args.load:
        Config.load_custom_config(args.load)
        print(f"✓ Configuration loaded from {args.load}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Finance Data Crawler - Indian Stock Market Data Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging level')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Crawl command
    crawl_parser = subparsers.add_parser('crawl', help='Start crawling data')
    crawl_parser.add_argument('--timeout', type=int, default=None,
                             help='Maximum crawl time in seconds')
    crawl_parser.add_argument('--limit', type=int, default=None,
                             help='Limit number of sectors to process')
    crawl_parser.add_argument('--sectors-file', type=str, default=None,
                             help='Path to sectors queue JSON file')
    crawl_parser.add_argument('--skip-visited', action='store_true',
                             help='Skip already visited sectors')
    crawl_parser.set_defaults(func=cmd_crawl)

    # Status command
    status_parser = subparsers.add_parser('status', help='Show crawler status and statistics')
    status_parser.add_argument('--show-errors', action='store_true',
                              help='Show recent errors')
    status_parser.add_argument('--error-limit', type=int, default=10,
                              help='Number of recent errors to show')
    status_parser.set_defaults(func=cmd_status)

    # List command
    list_parser = subparsers.add_parser('list', help='List all crawled companies')
    list_parser.add_argument('--from-db', action='store_true',
                            help='List from database instead of JSON')
    list_parser.set_defaults(func=cmd_list)

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate crawled data')
    validate_parser.add_argument('--company', type=str, default=None,
                                help='Validate specific company')
    validate_parser.add_argument('--from-db', action='store_true',
                                help='Validate from database instead of JSON')
    validate_parser.set_defaults(func=cmd_validate)

    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset tracking data')
    reset_parser.add_argument('--all', action='store_true',
                            help='Reset all data')
    reset_parser.add_argument('--sectors', action='store_true',
                            help='Reset visited sectors')
    reset_parser.add_argument('--companies', action='store_true',
                            help='Reset visited companies')
    reset_parser.add_argument('--progress', action='store_true',
                            help='Reset progress data')
    reset_parser.add_argument('--errors', action='store_true',
                            help='Clear error log')
    reset_parser.set_defaults(func=cmd_reset)

    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--show', action='store_true',
                              help='Show current configuration')
    config_parser.add_argument('--save', type=str, default=None,
                              help='Save configuration to file')
    config_parser.add_argument('--load', type=str, default=None,
                              help='Load configuration from file')
    config_parser.set_defaults(func=cmd_config)

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Ensure directories exist
    Config.ensure_directories()

    # Execute command
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
