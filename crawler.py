import pandas as pd
import json
import os
from tabulate import tabulate

json_folder = ''

# Load company data
company_data = pd.json_normalize(pd.read_json(os.path.join(json_folder, 'json\company_data.json')))

# Load quarters data
quarters_data = pd.json_normalize(pd.read_json(os.path.join(json_folder, 'json\quarters_data.json')))

# Print company data in a table
print("Company Data:")
print(tabulate(company_data, headers='keys', tablefmt='psql'))

# Print quarters data in a table
print("\nQuarters Data:")
print(tabulate(quarters_data, headers='keys', tablefmt='psql'))