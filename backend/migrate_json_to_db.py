"""
Migration script to import existing JSON data into PostgreSQL database
"""
import json
import os
from pathlib import Path
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import crud

# Create all tables
models.Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).parent.parent
COMPANIES_DIR = BASE_DIR / "companies"
JSON_DIR = BASE_DIR / "json"

def parse_numeric(value):
    """Parse numeric value from string, handling commas and special characters"""
    if value is None or value == "" or value == "-":
        return None
    try:
        # Remove commas and convert to float
        return float(str(value).replace(",", "").replace("₹", "").strip())
    except (ValueError, AttributeError):
        return None

def migrate_companies(db: Session):
    """Migrate company data from JSON files"""
    if not COMPANIES_DIR.exists():
        print("Companies directory not found")
        return

    company_files = list(COMPANIES_DIR.glob("*.json"))
    print(f"Found {len(company_files)} company files")

    for company_file in company_files:
        try:
            with open(company_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            company_name = data.get("company_name", company_file.stem)

            # Check if company already exists
            existing = crud.get_company_by_name(db, company_name)
            if existing:
                print(f"Company '{company_name}' already exists, skipping...")
                continue

            # Extract ratios
            ratios = data.get("ratios", {})

            # Create company
            company_data = {
                "name": company_name,
                "stock_price": data.get("stock_price"),
                "percentage_change": data.get("percentage_change"),
                "market_cap": ratios.get("Market Cap"),
                "current_price": ratios.get("Current Price"),
                "high_low": ratios.get("High / Low"),
                "stock_pe": ratios.get("Stock P/E"),
                "book_value": ratios.get("Book Value"),
                "dividend_yield": ratios.get("Dividend Yield"),
                "roce": ratios.get("ROCE"),
                "roe": ratios.get("ROE"),
                "face_value": ratios.get("Face Value"),
                "about": data.get("about_and_key_points"),
            }

            company = crud.create_company(db, company_data)
            print(f"Created company: {company_name} (ID: {company.id})")

        except Exception as e:
            print(f"Error migrating {company_file}: {e}")
            continue

def migrate_financial_data(db: Session):
    """Migrate financial data from JSON files in json/ directory"""
    if not JSON_DIR.exists():
        print("JSON directory not found")
        return

    # Get the latest company (assuming it's the most recent scrape)
    companies = crud.get_companies(db, limit=1)
    if not companies:
        print("No companies found in database")
        return

    company = companies[0]
    print(f"Migrating financial data for: {company.name}")

    # Migrate Balance Sheet
    balance_sheet_file = JSON_DIR / "balance_sheet_data.json"
    if balance_sheet_file.exists():
        try:
            with open(balance_sheet_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Data structure varies, handle both list and dict
            if isinstance(data, dict):
                for period, values in data.items():
                    if isinstance(values, dict):
                        bs_data = {
                            "period": period,
                            "equity_capital": parse_numeric(values.get("Equity Capital")),
                            "reserves": parse_numeric(values.get("Reserves")),
                            "borrowings": parse_numeric(values.get("Borrowings")),
                            "total_liabilities": parse_numeric(values.get("Total Liabilities")),
                            "fixed_assets": parse_numeric(values.get("Fixed Assets")),
                            "investments": parse_numeric(values.get("Investments")),
                            "total_assets": parse_numeric(values.get("Total Assets")),
                        }
                        crud.create_balance_sheet(db, company.id, bs_data)

            print(f"Migrated balance sheet data")
        except Exception as e:
            print(f"Error migrating balance sheet: {e}")

    # Migrate Profit & Loss
    pl_file = JSON_DIR / "profit_loss_data.json"
    if pl_file.exists():
        try:
            with open(pl_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict):
                for period, values in data.items():
                    if isinstance(values, dict):
                        pl_data = {
                            "period": period,
                            "sales": parse_numeric(values.get("Sales")),
                            "expenses": parse_numeric(values.get("Expenses")),
                            "operating_profit": parse_numeric(values.get("Operating Profit")),
                            "opm_percent": parse_numeric(values.get("OPM %")),
                            "net_profit": parse_numeric(values.get("Net Profit")),
                            "eps": parse_numeric(values.get("EPS in Rs")),
                        }
                        crud.create_profit_loss(db, company.id, pl_data)

            print(f"Migrated profit & loss data")
        except Exception as e:
            print(f"Error migrating profit & loss: {e}")

    # Migrate Cash Flows
    cf_file = JSON_DIR / "cash_flows_data.json"
    if cf_file.exists():
        try:
            with open(cf_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict):
                for period, values in data.items():
                    if isinstance(values, dict):
                        cf_data = {
                            "period": period,
                            "operating_activities": parse_numeric(values.get("Cash from Operating Activity")),
                            "investing_activities": parse_numeric(values.get("Cash from Investing Activity")),
                            "financing_activities": parse_numeric(values.get("Cash from Financing Activity")),
                            "net_cash_flow": parse_numeric(values.get("Net Cash Flow")),
                        }
                        crud.create_cash_flow(db, company.id, cf_data)

            print(f"Migrated cash flows data")
        except Exception as e:
            print(f"Error migrating cash flows: {e}")

    # Migrate Quarterly Data
    quarters_file = JSON_DIR / "quarters_data.json"
    if quarters_file.exists():
        try:
            with open(quarters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict):
                for quarter, values in data.items():
                    if isinstance(values, dict):
                        qd_data = {
                            "quarter": quarter,
                            "sales": parse_numeric(values.get("Sales")),
                            "expenses": parse_numeric(values.get("Expenses")),
                            "operating_profit": parse_numeric(values.get("Operating Profit")),
                            "opm_percent": parse_numeric(values.get("OPM %")),
                            "net_profit": parse_numeric(values.get("Net Profit")),
                            "eps": parse_numeric(values.get("EPS in Rs")),
                        }
                        crud.create_quarterly_data(db, company.id, qd_data)

            print(f"Migrated quarterly data")
        except Exception as e:
            print(f"Error migrating quarterly data: {e}")

def main():
    """Run migration"""
    print("Starting migration from JSON to PostgreSQL...")
    print("=" * 60)

    db = SessionLocal()
    try:
        migrate_companies(db)
        print("\n" + "=" * 60)
        migrate_financial_data(db)
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
