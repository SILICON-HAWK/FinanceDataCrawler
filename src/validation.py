"""
Data validation module for Finance Data Crawler
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates extracted financial data"""

    def __init__(self, config):
        """
        Initialize data validator.

        Args:
            config: Configuration object
        """
        self.config = config
        self.required_fields = config.REQUIRED_COMPANY_FIELDS

    def validate_company_data(self, data: Dict) -> tuple[bool, List[str]]:
        """
        Validate company data completeness and quality.

        Args:
            data (Dict): Company data dictionary

        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        for field in self.required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Validate company_data
        if 'company_data' in data:
            company_data = data['company_data']

            # Check company name
            if not company_data.get('company_name') or company_data.get('company_name') == "Company name not found.":
                errors.append("Invalid company name")

            # Check stock price
            if not company_data.get('stock_price') or company_data.get('stock_price') == "Stock price not found.":
                errors.append("Missing stock price")

            # Check ratios
            ratios = company_data.get('ratios', {})
            if not ratios or "Ratios not found." in ratios:
                errors.append("Missing ratios data")

        # Validate quarters_data
        if 'quarters_data' in data:
            if not data['quarters_data']:
                errors.append("Empty quarters data")

        # Validate profit_loss_data
        if 'profit_loss_data' in data:
            if not data['profit_loss_data']:
                errors.append("Empty profit & loss data")

        is_valid = len(errors) == 0
        return is_valid, errors

    def validate_and_log(self, company_name: str, data: Dict) -> bool:
        """
        Validate company data and log results.

        Args:
            company_name (str): Name of the company
            data (Dict): Company data dictionary

        Returns:
            bool: True if valid, False otherwise
        """
        is_valid, errors = self.validate_company_data(data)

        if is_valid:
            logger.info(f"Data validation passed for: {company_name}")
        else:
            logger.warning(f"Data validation failed for {company_name}: {', '.join(errors)}")

        return is_valid

    def get_data_quality_score(self, data: Dict) -> float:
        """
        Calculate a data quality score (0-100).

        Args:
            data (Dict): Company data dictionary

        Returns:
            float: Quality score between 0 and 100
        """
        score = 0
        max_score = 0

        # Check for presence of each data type (10 points each)
        data_types = [
            'company_data',
            'quarters_data',
            'profit_loss_data',
            'balance_sheet_data',
            'cash_flows_data',
            'ratios_data',
            'shareholding_data'
        ]

        for data_type in data_types:
            max_score += 10
            if data_type in data and data[data_type]:
                score += 10

        # Check company_data completeness (30 points)
        max_score += 30
        if 'company_data' in data:
            company_data = data['company_data']

            # Company name (10 points)
            if company_data.get('company_name') and company_data.get('company_name') != "Company name not found.":
                score += 10

            # Stock price (10 points)
            if company_data.get('stock_price') and company_data.get('stock_price') != "Stock price not found.":
                score += 10

            # Ratios (10 points)
            ratios = company_data.get('ratios', {})
            if ratios and "Ratios not found." not in ratios:
                score += 10

        # Normalize to 0-100
        if max_score > 0:
            return (score / max_score) * 100
        return 0

    def check_data_freshness(self, data: Dict) -> Optional[str]:
        """
        Check if data appears to be current/fresh.

        Args:
            data (Dict): Company data dictionary

        Returns:
            str: Status message or None if unable to determine
        """
        # Check quarters data for recent quarters
        if 'quarters_data' in data and data['quarters_data']:
            quarters = list(data['quarters_data'].keys())
            if quarters:
                latest_quarter = quarters[0]
                logger.info(f"Latest quarter data: {latest_quarter}")
                return f"Latest quarter: {latest_quarter}"

        return None

    def validate_batch(self, companies_data: List[Dict]) -> Dict:
        """
        Validate a batch of company data.

        Args:
            companies_data (List[Dict]): List of company data dictionaries

        Returns:
            dict: Validation summary
        """
        summary = {
            'total': len(companies_data),
            'valid': 0,
            'invalid': 0,
            'average_quality_score': 0,
            'errors_by_type': {}
        }

        total_quality = 0

        for company_data in companies_data:
            is_valid, errors = self.validate_company_data(company_data)

            if is_valid:
                summary['valid'] += 1
            else:
                summary['invalid'] += 1

                # Track error types
                for error in errors:
                    if error not in summary['errors_by_type']:
                        summary['errors_by_type'][error] = 0
                    summary['errors_by_type'][error] += 1

            quality_score = self.get_data_quality_score(company_data)
            total_quality += quality_score

        if summary['total'] > 0:
            summary['average_quality_score'] = total_quality / summary['total']

        return summary
