Creating a interactive Dashboard for financial data of Listed indian companies


Main Task: Web Scraping Data Extraction and DashBoard
=
Task 1: Retreving HTML ✔️
-
Sub Task 1.1: Send HTTP Request ✔️

Sub Task 1.2: Get HTML Response ✔️

Task 2: Data Extraction ✔️
-
Sub Task 2.1: Parse HTML ✔️

Sub Task 2.2: Extract Financial Data ✔️

Task 3: Queue and Hash Map Implementation ❔
-
Sub Task 3.1: Implement Queue ✔️

Sub Task 3.2: Implement Hash Map

Task 4: Data Storage ❔
-
Storing data in Json intermedia for now

TO-DO - SQL/PostGres server ❔ 

Sub Task 4.1: Connect to Database

Sub Task 4.2: Create Table

Sub Task 4.3: Insert Data

Task 5: Create Dash Board 
-
Feature maybe ?

  - Search function
  - Compare
  - visualise

----
/// NOTES

**1. Processing Limit:**
- Set a limit on the number of pages to scrape per session

**2. Rate Limit:**
- Set a delay between HTTP requests (e.g., 1-5 seconds) to avoid overwhelming the website.

**3. Crawl Limit:**
- Set a limit on the number of crawls throughout the website per session

**4. Hash Map for Listed Companies:**
- Implement a hash map (dictionary) to store the listed companies
- Check the hash map before scraping a company's data to avoid duplication
