"""
Command-line interface for Finance Data Crawler
"""
import sys
import argparse
import json
from pathlib import Path
from typing import Optional

from .config import Config
from .validation import DataValidator

def load_companies() -> list:
    """Load all companies from JSON files"""
    companies = []
    if Config.COMPANIES_DIR.exists():
        for company_file in Config.COMPANIES_DIR.glob("*.json"):
            try:
                with open(company_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['file'] = company_file.name
                    companies.append(data)
            except Exception as e:
                print(f"Error loading {company_file}: {e}")
    return companies

def cmd_status(args):
    """Show crawler status and statistics"""
    print("=" * 60)
    print("FINANCE DATA CRAWLER - STATUS")
    print("=" * 60)

    # Count companies
    companies = load_companies()
    print(f"\nTotal Companies: {len(companies)}")

    # Check queue status
    if Config.COMPANY_QUEUE_FILE.exists():
        with open(Config.COMPANY_QUEUE_FILE, 'r') as f:
            queue = json.load(f)
            print(f"Companies in Queue: {len(queue) if isinstance(queue, list) else 0}")

    if Config.SECTORS_QUEUE_FILE.exists():
        with open(Config.SECTORS_QUEUE_FILE, 'r') as f:
            sectors = json.load(f)
            print(f"Sectors in Queue: {len(sectors) if isinstance(sectors, list) else 0}")

    # Check visited tracking
    if Config.VISITED_SECTORS_FILE.exists():
        with open(Config.VISITED_SECTORS_FILE, 'r') as f:
            visited = json.load(f)
            print(f"Visited Sectors: {len(visited) if isinstance(visited, list) else 0}")

    # Database info
    print(f"\nDatabase Type: {Config.DB_TYPE}")
    if Config.DB_TYPE == "sqlite":
        print(f"Database File: {Config.SQLITE_DB_PATH}")
        print(f"Database Exists: {Config.SQLITE_DB_PATH.exists()}")
    else:
        print(f"Database URL: {Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}")

    print(f"\nData Directory: {Config.COMPANIES_DIR}")
    print(f"JSON Directory: {Config.JSON_DIR}")
    print("=" * 60)

def cmd_list(args):
    """List all crawled companies"""
    companies = load_companies()

    if not companies:
        print("No companies found.")
        return

    print(f"\nFound {len(companies)} companies:\n")
    print(f"{'#':<5} {'Company Name':<50} {'Stock Price':<15}")
    print("-" * 70)

    for i, company in enumerate(companies, 1):
        name = company.get('company_name', 'Unknown')[:48]
        price = company.get('stock_price', 'N/A')
        print(f"{i:<5} {name:<50} {price:<15}")

    if args.detail:
        print("\nDetailed View:")
        print("=" * 70)
        for company in companies[:args.limit if args.limit else len(companies)]:
            print(f"\nCompany: {company.get('company_name', 'Unknown')}")
            print(f"Stock Price: {company.get('stock_price', 'N/A')}")
            print(f"Change: {company.get('percentage_change', 'N/A')}")
            if 'ratios' in company:
                print("Key Ratios:")
                for key, value in list(company['ratios'].items())[:5]:
                    print(f"  {key}: {value}")

def cmd_validate(args):
    """Validate data quality"""
    companies = load_companies()

    if not companies:
        print("No companies to validate.")
        return

    print(f"Validating {len(companies)} companies...\n")

    results = DataValidator.batch_validate(companies)
    report = DataValidator.generate_report(results)

    print(report)

    if args.save:
        report_file = Config.LOGS_DIR / "validation_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")

def cmd_reset(args):
    """Reset tracking data"""
    files_to_reset = []

    if args.all or args.sectors:
        if Config.VISITED_SECTORS_FILE.exists():
            files_to_reset.append(('Visited Sectors', Config.VISITED_SECTORS_FILE))

    if args.all or args.companies:
        if Config.VISITED_COMPANIES_FILE.exists():
            files_to_reset.append(('Visited Companies', Config.VISITED_COMPANIES_FILE))

    if args.all or args.queue:
        if Config.COMPANY_QUEUE_FILE.exists():
            files_to_reset.append(('Company Queue', Config.COMPANY_QUEUE_FILE))
        if Config.SECTORS_QUEUE_FILE.exists():
            files_to_reset.append(('Sectors Queue', Config.SECTORS_QUEUE_FILE))

    if not files_to_reset:
        print("No files to reset.")
        return

    print("Files to be reset:")
    for name, _ in files_to_reset:
        print(f"  - {name}")

    if not args.force:
        confirm = input("\nAre you sure? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Reset cancelled.")
            return

    for name, file_path in files_to_reset:
        try:
            # Reset to empty list or dict
            with open(file_path, 'w') as f:
                json.dump([], f)
            print(f"✓ Reset {name}")
        except Exception as e:
            print(f"✗ Error resetting {name}: {e}")

    print("\nReset complete!")

def cmd_config(args):
    """Manage configuration"""
    if args.show:
        print("=" * 60)
        print("CURRENT CONFIGURATION")
        print("=" * 60)
        print(f"Rate Limit Interval: {Config.RATE_LIMIT_INTERVAL}s")
        print(f"Request Timeout: {Config.REQUEST_TIMEOUT}s")
        print(f"Max Retries: {Config.MAX_RETRIES}")
        print(f"Database Type: {Config.DB_TYPE}")
        print(f"Log Level: {Config.LOG_LEVEL}")
        print(f"Sector Page Limit: {Config.SECTOR_PAGE_LIMIT}")
        print(f"Min Quality Score: {Config.MIN_QUALITY_SCORE}")
        print("=" * 60)

    if args.save:
        Config.save_config(args.save)
        print(f"Configuration saved to: {args.save}")

    if args.load:
        Config.load_custom_config(args.load)
        print(f"Configuration loaded from: {args.load}")

def cmd_info(args):
    """Show information about a specific company"""
    companies = load_companies()

    # Find company by name (case-insensitive partial match)
    search_term = args.name.lower()
    matches = [c for c in companies if search_term in c.get('company_name', '').lower()]

    if not matches:
        print(f"No company found matching: {args.name}")
        return

    if len(matches) > 1:
        print(f"Multiple companies found:")
        for i, company in enumerate(matches, 1):
            print(f"{i}. {company.get('company_name')}")
        return

    company = matches[0]

    print("=" * 70)
    print(f"COMPANY INFORMATION")
    print("=" * 70)
    print(f"\nName: {company.get('company_name', 'Unknown')}")
    print(f"Stock Price: {company.get('stock_price', 'N/A')}")
    print(f"Change: {company.get('percentage_change', 'N/A')}")

    if 'ratios' in company:
        print("\nFinancial Ratios:")
        print("-" * 70)
        for key, value in company['ratios'].items():
            print(f"  {key:<30} : {value}")

    if 'about_and_key_points' in company:
        print(f"\nAbout:")
        print("-" * 70)
        print(company['about_and_key_points'][:500])

    # Validate this company
    is_valid, errors, score = DataValidator.validate_company(company)
    print(f"\nData Quality Score: {score}/100")
    if not is_valid:
        print("Issues:")
        for error in errors:
            print(f"  - {error}")

    print("=" * 70)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Finance Data Crawler - CLI Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show crawler status')

    # List command
    list_parser = subparsers.add_parser('list', help='List all companies')
    list_parser.add_argument('--detail', action='store_true', help='Show detailed information')
    list_parser.add_argument('--limit', type=int, help='Limit number of companies shown in detail')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate data quality')
    validate_parser.add_argument('--save', action='store_true', help='Save validation report')

    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset tracking data')
    reset_parser.add_argument('--all', action='store_true', help='Reset all tracking data')
    reset_parser.add_argument('--sectors', action='store_true', help='Reset visited sectors')
    reset_parser.add_argument('--companies', action='store_true', help='Reset visited companies')
    reset_parser.add_argument('--queue', action='store_true', help='Reset queues')
    reset_parser.add_argument('--force', action='store_true', help='Skip confirmation')

    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--save', type=str, help='Save configuration to file')
    config_parser.add_argument('--load', type=str, help='Load configuration from file')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show company information')
    info_parser.add_argument('name', type=str, help='Company name (partial match)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Route to appropriate command
    commands = {
        'status': cmd_status,
        'list': cmd_list,
        'validate': cmd_validate,
        'reset': cmd_reset,
        'config': cmd_config,
        'info': cmd_info
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
