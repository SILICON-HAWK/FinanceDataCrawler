"""
Data validation and quality checking
"""
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Validator for scraped financial data"""

    REQUIRED_FIELDS = {
        'company': ['company_name', 'stock_price'],
        'ratios': ['Market Cap', 'ROE', 'ROCE'],
        'balance_sheet': ['period', 'total_assets', 'total_liabilities'],
        'profit_loss': ['period', 'sales', 'net_profit']
    }

    @staticmethod
    def validate_company(data: Dict[str, Any]) -> Tuple[bool, List[str], int]:
        """
        Validate company data

        Returns:
            (is_valid, errors, quality_score)
        """
        errors = []
        score = 100

        # Check required fields
        if not data.get('company_name'):
            errors.append("Missing company_name")
            score -= 30

        if not data.get('stock_price'):
            errors.append("Missing stock_price")
            score -= 20

        # Check ratios
        ratios = data.get('ratios', {})
        if not ratios:
            errors.append("Missing ratios data")
            score -= 30
        else:
            required_ratios = ['Market Cap', 'ROE', 'ROCE']
            for ratio in required_ratios:
                if not ratios.get(ratio):
                    errors.append(f"Missing ratio: {ratio}")
                    score -= 5

        # Check optional but important fields
        if not data.get('percentage_change'):
            score -= 5

        if not data.get('about_and_key_points'):
            score -= 10

        is_valid = score >= 70  # Minimum 70% score to be valid
        return is_valid, errors, max(0, score)

    @staticmethod
    def validate_financial_data(data_type: str, data: Dict[str, Any]) -> Tuple[bool, List[str], int]:
        """
        Validate financial data (balance sheet, P&L, etc.)

        Args:
            data_type: Type of financial data (balance_sheet, profit_loss, etc.)
            data: Financial data dictionary

        Returns:
            (is_valid, errors, quality_score)
        """
        errors = []
        score = 100

        if not data:
            return False, ["Empty data"], 0

        required = DataValidator.REQUIRED_FIELDS.get(data_type, [])

        # Check if data has multiple periods
        if len(data) == 0:
            errors.append("No time periods found")
            return False, errors, 0

        # Validate each period
        for period, values in data.items():
            if not isinstance(values, dict):
                errors.append(f"Invalid data format for period {period}")
                score -= 20
                continue

            for field in required:
                if field == 'period':
                    continue
                if not values.get(field):
                    errors.append(f"Missing {field} for period {period}")
                    score -= 5

        # Check data completeness
        period_count = len(data)
        if period_count < 3:
            errors.append(f"Insufficient historical data ({period_count} periods)")
            score -= 20

        is_valid = score >= 60
        return is_valid, errors, max(0, score)

    @staticmethod
    def batch_validate(companies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate multiple companies

        Returns:
            Statistics about validation results
        """
        stats = {
            'total': len(companies),
            'valid': 0,
            'invalid': 0,
            'average_score': 0,
            'errors': []
        }

        total_score = 0

        for company in companies:
            is_valid, errors, score = DataValidator.validate_company(company)

            if is_valid:
                stats['valid'] += 1
            else:
                stats['invalid'] += 1
                stats['errors'].append({
                    'company': company.get('company_name', 'Unknown'),
                    'errors': errors,
                    'score': score
                })

            total_score += score

        if companies:
            stats['average_score'] = total_score / len(companies)

        return stats

    @staticmethod
    def check_freshness(data: Dict[str, Any], max_age_days: int = 90) -> bool:
        """
        Check if data is fresh (not too old)

        Args:
            data: Company data with created_at or updated_at field
            max_age_days: Maximum age in days

        Returns:
            True if data is fresh
        """
        timestamp_field = data.get('created_at') or data.get('updated_at')

        if not timestamp_field:
            return False  # Can't determine age

        try:
            if isinstance(timestamp_field, str):
                data_date = datetime.fromisoformat(timestamp_field.replace('Z', '+00:00'))
            else:
                data_date = timestamp_field

            age_days = (datetime.now() - data_date).days
            return age_days <= max_age_days

        except Exception as e:
            logger.error(f"Error checking freshness: {e}")
            return False

    @staticmethod
    def generate_report(validation_results: Dict[str, Any]) -> str:
        """Generate a human-readable validation report"""
        report = []
        report.append("=" * 60)
        report.append("DATA VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Total Companies: {validation_results['total']}")
        report.append(f"Valid: {validation_results['valid']}")
        report.append(f"Invalid: {validation_results['invalid']}")
        report.append(f"Average Quality Score: {validation_results['average_score']:.2f}/100")
        report.append("")

        if validation_results['errors']:
            report.append("ERRORS:")
            report.append("-" * 60)
            for error_info in validation_results['errors'][:10]:  # Show first 10
                report.append(f"\nCompany: {error_info['company']}")
                report.append(f"Score: {error_info['score']}/100")
                report.append("Issues:")
                for error in error_info['errors']:
                    report.append(f"  - {error}")

        report.append("=" * 60)
        return "\n".join(report)
