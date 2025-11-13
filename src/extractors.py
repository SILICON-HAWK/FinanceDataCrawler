"""
Data extraction functions for Finance Data Crawler
"""
import json
import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


def extract_company_data(html: str) -> Optional[Dict]:
    """
    Extract company data from the given HTML.

    Args:
        html (str): The HTML content to parse.

    Returns:
        dict: A dictionary containing the extracted company data, or None if extraction fails.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Find the company-info div
        company_info_div = soup.find('div', id='top')
        if company_info_div is None:
            logger.warning("Company info div not found.")
            return None

        # Extract company information
        company_name = company_info_div.find('h1', class_='margin-0')
        company_name = company_name.text.strip() if company_name else "Company name not found."

        # Extract stock price and percentage change
        stock_price_div = company_info_div.find('div', class_='font-size-18')
        if stock_price_div:
            stock_price = stock_price_div.find('span').text.strip().replace('\n', '').replace('₹', '').replace('¹', '').replace('�','').replace('â‚', '').strip() + ' INR'
            percentage_change = stock_price_div.find('span', class_='font-size-12').text.strip()
        else:
            stock_price = "Stock price not found."
            percentage_change = "Percentage change not found."

        # Extract ratios
        ratios_div = company_info_div.find('ul', id='top-ratios')
        if ratios_div:
            ratios = {}
            for ratio in ratios_div.find_all('li'):
                name = ratio.find('span', class_='name').text.strip()
                value = ratio.find('span', class_='value').text.strip().replace('\n', '').replace('₹', '').replace('¹', '').replace('�','').replace('â‚', '').strip()
                value = ' '.join(value.split())
                if 'Cr' in value:
                    value = value + ' INR'
                elif value.replace('.','',1).isdigit():
                    value = value + ' INR'
                ratios[name] = value
        else:
            ratios = {"Ratios not found." : "No data available."}

        # Extract company profile
        company_data = {}
        company_profile_div = company_info_div.find('div', class_='company-profile')
        if company_profile_div:
            about = company_profile_div.find('div', class_='sub').text.strip().replace('\n', ' ') if company_profile_div.find('div', class_='sub') else "About not found."
            key_points = company_profile_div.find('div', class_='sub commentary').text.strip() if company_profile_div.find('div', class_='sub commentary') else "Key points not found."
            company_links = [link.get('href') for link in company_profile_div.find_all('a')]
            company_data["about_and_key_points"] = f"About: {about} Key_points: {key_points}"
            company_data["company_links"] = company_links
        else:
            company_data["about_and_key_points"] = "About not found. Key_points not found."
            company_data["company_links"] = []

        return {
            'company_name': company_name,
            'stock_price': stock_price,
            'percentage_change': percentage_change,
            'ratios': ratios,
            **company_data
        }
    except Exception as e:
        logger.error(f"Error extracting company data: {e}")
        return None


def extract_quarters_data(html: str) -> Optional[Dict]:
    """
    Extract quarters data from the given HTML.

    Args:
        html (str): The HTML content to parse.

    Returns:
        dict: A dictionary containing the extracted quarters data, or None if extraction fails.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        quarters_section = soup.find('section', id='quarters')
        if quarters_section is None:
            logger.warning("Quarters section not found.")
            return None

        table = quarters_section.find('table', class_='data-table')
        if table is None:
            logger.warning("Quarters table not found.")
            return None

        headers = [th.text.strip() for th in table.find_all('th')][1:]

        data = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            cols = [col.text.strip().replace(' ', '').replace('+', '').replace('<span class="blue-icon">', '').replace('</span>', '').encode('ascii', 'ignore').decode('ascii') for col in cols][1:]
            data.append([col for col in cols if col])

        categories = ['Sales', 'Expenses', 'Operating Profit', 'OPM %', 'Other Income', 'Interest', 'Depreciation', 'Profit before tax', 'Tax %', 'Net Profit', 'EPS in Rs']
        quarters_data = {}
        for i, header in enumerate(headers):
            quarters_data[header] = {}
            for j, category in enumerate(categories):
                if j < len(data) and i < len(data[j]):
                    quarters_data[header][category] = data[j][i]
                else:
                    quarters_data[header][category] = 'null'

        return quarters_data
    except Exception as e:
        logger.error(f"Error extracting quarters data: {e}")
        return None


def extract_profit_loss_data(html: str) -> Optional[Dict]:
    """
    Extract Profit & Loss and Compounded Growth data from the given HTML.

    Args:
        html (str): The HTML content to parse.

    Returns:
        dict: A dictionary containing the extracted profit & loss data, or None if extraction fails.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        profit_loss_section = soup.find('section', id='profit-loss')
        if profit_loss_section is None:
            logger.warning("Profit & Loss section not found.")
            return None

        table = profit_loss_section.find('table', class_='data-table')
        if table is None:
            logger.warning("Profit & Loss table not found.")
            return None

        headers = [th.text.strip() for th in table.find_all('th')][1:]
        data = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            cols = [col.text.strip().replace(' ', '').replace('+', '').replace('<span class="blue-icon">', '').replace('</span>', '').encode('ascii', 'ignore').decode('ascii') for col in cols][1:]
            data.append([col for col in cols if col])

        categories = ['Sales', 'Expenses', 'Operating Profit', 'OPM %', 'Other Income', 'Interest', 'Depreciation', 'Profit before tax', 'Tax %', 'Net Profit', 'EPS in Rs']
        profit_loss_data = {}
        for i, header in enumerate(headers):
            profit_loss_data[header] = {}
            for j, category in enumerate(categories):
                if j < len(data) and i < len(data[j]):
                    profit_loss_data[header][category] = data[j][i]
                else:
                    profit_loss_data[header][category] = 'null'

        # Extract Compounded Growth data
        growth_tables = soup.find_all('table', class_='ranges-table')
        if not growth_tables:
            logger.warning("Growth tables not found.")
            compounded_growth_data = {}
        else:
            compounded_sales_growth = {}
            compounded_profit_growth = {}
            stock_price_cagr = {}
            return_on_equity = {}

            for i, table in enumerate(growth_tables):
                rows = table.find_all('tr')[1:]
                for row in rows:
                    cols = row.find_all('td')
                    metric = cols[0].text.strip()
                    value = cols[1].text.strip()
                    if i == 0:
                        compounded_sales_growth[metric] = value
                    elif i == 1:
                        compounded_profit_growth[metric] = value
                    elif i == 2:
                        stock_price_cagr[metric] = value
                    elif i == 3:
                        return_on_equity[metric] = value

            compounded_growth_data = {
                'Compounded Sales Growth': compounded_sales_growth,
                'Compounded Profit Growth': compounded_profit_growth,
                'Stock Price CAGR': stock_price_cagr,
                'Return on Equity': return_on_equity
            }

        return {
            'Profit & Loss': profit_loss_data,
            'Compounded Growth': compounded_growth_data
        }
    except Exception as e:
        logger.error(f"Error extracting profit & loss data: {e}")
        return None


def extract_balance_sheet_data(html: str) -> Optional[Dict]:
    """
    Extract balance sheet data from the given HTML.

    Args:
        html (str): The HTML content to parse.

    Returns:
        dict: A dictionary containing the extracted balance sheet data, or None if extraction fails.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        balance_sheet_section = soup.find('section', id='balance-sheet')
        if balance_sheet_section is None:
            logger.warning("Balance Sheet section not found.")
            return None

        table = balance_sheet_section.find('table', class_='data-table')
        if table is None:
            logger.warning("Balance Sheet table not found.")
            return None

        headers = [th.text.strip() for th in table.find_all('th')][1:]

        data = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            cols = [col.text.strip().replace(' ', '').replace('+', '').replace('<span class="blue-icon">', '').replace('</span>', '').replace('\u00a0+', '').encode('ascii', 'ignore').decode('ascii') for col in cols][1:]
            data.append([col for col in cols if col])

        balance_sheet_data = {}
        categories = [row.find_all('td')[0].text.strip().replace('\u00a0+', '') for row in table.find_all('tr')[1:]]
        for i, header in enumerate(headers):
            balance_sheet_data[header] = {}
            for j, category in enumerate(categories):
                if j < len(data) and i < len(data[j]):
                    balance_sheet_data[header][category] = data[j][i]
                else:
                    balance_sheet_data[header][category] = 'null'

        return balance_sheet_data
    except Exception as e:
        logger.error(f"Error extracting balance sheet data: {e}")
        return None


def extract_cash_flows_data(html: str) -> Optional[Dict]:
    """
    Extract cash flows data from the given HTML.

    Args:
        html (str): The HTML content to parse.

    Returns:
        dict: A dictionary containing the extracted cash flows data, or None if extraction fails.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        cash_flows_section = soup.find('section', id='cash-flow')
        if cash_flows_section is None:
            logger.warning("Cash Flows section not found.")
            return None

        table = cash_flows_section.find('table', class_='data-table')
        if table is None:
            logger.warning("Cash Flows table not found.")
            return None

        headers = [th.text.strip() for th in table.find_all('th')][1:]

        data = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            cols = [col.text.strip().replace(' ', '').replace('+', '').replace('<span class="blue-icon">', '').replace('</span>', '').replace('\u00a0+', '').encode('ascii', 'ignore').decode('ascii') for col in cols][1:]
            data.append([col for col in cols if col])

        cash_flows_data = {}
        categories = [row.find_all('td')[0].text.strip().replace('\u00a0+', '') for row in table.find_all('tr')[1:]]
        for i, header in enumerate(headers):
            cash_flows_data[header] = {}
            for j, category in enumerate(categories):
                if j < len(data) and i < len(data[j]):
                    cash_flows_data[header][category] = data[j][i]
                else:
                    cash_flows_data[header][category] = 'null'

        return cash_flows_data
    except Exception as e:
        logger.error(f"Error extracting cash flows data: {e}")
        return None


def extract_ratios_data(html: str) -> Optional[Dict]:
    """
    Extract ratios data from the given HTML.

    Args:
        html (str): The HTML content to parse.

    Returns:
        dict: A dictionary containing the extracted ratios data, or None if extraction fails.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        ratios_section = soup.find('section', id='ratios')
        if ratios_section is None:
            logger.warning("Ratios section not found.")
            return None

        table = ratios_section.find('table', class_='data-table')
        if table is None:
            logger.warning("Ratios table not found.")
            return None

        headers = [th.text.strip() for th in table.find_all('th')][1:]

        data = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            cols = [col.text.strip().replace(' ', '').replace('%', '').encode('ascii', 'ignore').decode('ascii') for col in cols][1:]
            data.append([col for col in cols if col])

        ratios_data = {}
        categories = [row.find_all('td')[0].text.strip() for row in table.find_all('tr')[1:]]
        for i, header in enumerate(headers):
            ratios_data[header] = {}
            for j, category in enumerate(categories):
                if j < len(data) and i < len(data[j]):
                    ratios_data[header][category] = data[j][i]
                else:
                    ratios_data[header][category] = 'null'

        return ratios_data
    except Exception as e:
        logger.error(f"Error extracting ratios data: {e}")
        return None


def extract_shareholding_data(html: str) -> Optional[Dict]:
    """
    Extract shareholding data from the given HTML.

    Args:
        html (str): The HTML content to parse.

    Returns:
        dict: A dictionary containing the extracted shareholding data, or None if extraction fails.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        shareholding_section = soup.find('section', id='shareholding')
        if shareholding_section is None:
            logger.warning("Shareholding section not found.")
            return None

        quarterly_table = shareholding_section.find('div', id='quarterly-shp').find('table')
        yearly_table = shareholding_section.find('div', id='yearly-shp').find('table')

        # Extract quarterly data
        quarterly_data = {}
        quarterly_headers = [th.text.strip() for th in quarterly_table.find_all('th')][1:]
        quarterly_rows = quarterly_table.find_all('tr')[1:]
        for row in quarterly_rows:
            cols = row.find_all('td')
            category = cols[0].text.strip().replace('-', '').replace('+', '').replace('\u00a0', '')
            data = [col.text.strip().replace('-', '').replace('+', '').replace('\u00a0', '') for col in cols[1:]]
            quarterly_data[category] = {}
            for i, header in enumerate(quarterly_headers):
                quarterly_data[category][header] = data[i]

        # Extract yearly data
        yearly_data = {}
        yearly_headers = [th.text.strip() for th in yearly_table.find_all('th')][1:]
        yearly_rows = yearly_table.find_all('tr')[1:]
        for row in yearly_rows:
            cols = row.find_all('td')
            category = cols[0].text.strip().replace('-', '').replace('+', '').replace('\u00a0', '')
            data = [col.text.strip().replace('-', '').replace('+', '').replace('\u00a0', '') for col in cols[1:]]
            yearly_data[category] = {}
            for i, header in enumerate(yearly_headers):
                yearly_data[category][header] = data[i]

        return {
            'Quarterly': quarterly_data,
            'Yearly': yearly_data
        }
    except Exception as e:
        logger.error(f"Error extracting shareholding data: {e}")
        return None


def extract_company_links(html: str, base_url: str = "https://www.screener.in") -> List[str]:
    """
    Extract company links from sector comparison page.

    Args:
        html (str): The HTML content to parse.
        base_url (str): Base URL for constructing absolute URLs.

    Returns:
        list: A list of company URLs.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        company_links = soup.find_all('a', target="_blank")

        company_urls = []
        for link in company_links:
            company_url = link.get('href')
            if company_url:
                # Convert to absolute URL if needed
                if not company_url.startswith('http'):
                    company_url = urljoin(base_url, company_url)
                company_urls.append(company_url)

        logger.info(f"Extracted {len(company_urls)} company URLs")
        return company_urls
    except Exception as e:
        logger.error(f"Error extracting company links: {e}")
        return []


def extract_sector_name(html: str) -> Optional[str]:
    """
    Extract sector name from page title.

    Args:
        html (str): The HTML content to parse.

    Returns:
        str: The sector name, or None if not found.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text
            sector_name = title.replace("- Screener", "").strip()
            return sector_name
        return None
    except Exception as e:
        logger.error(f"Error extracting sector name: {e}")
        return None


def extract_all_data(html: str) -> Dict:
    """
    Extract all financial data from a company page.

    Args:
        html (str): The HTML content to parse.

    Returns:
        dict: A dictionary containing all extracted data.
    """
    all_data = {}

    # Extract each type of data
    company_data = extract_company_data(html)
    if company_data:
        all_data['company_data'] = company_data
        all_data['company_name'] = company_data.get('company_name', 'Unknown')

    quarters_data = extract_quarters_data(html)
    if quarters_data:
        all_data['quarters_data'] = quarters_data

    profit_loss_data = extract_profit_loss_data(html)
    if profit_loss_data:
        all_data['profit_loss_data'] = profit_loss_data

    balance_sheet_data = extract_balance_sheet_data(html)
    if balance_sheet_data:
        all_data['balance_sheet_data'] = balance_sheet_data

    cash_flows_data = extract_cash_flows_data(html)
    if cash_flows_data:
        all_data['cash_flows_data'] = cash_flows_data

    ratios_data = extract_ratios_data(html)
    if ratios_data:
        all_data['ratios_data'] = ratios_data

    shareholding_data = extract_shareholding_data(html)
    if shareholding_data:
        all_data['shareholding_data'] = shareholding_data

    return all_data
