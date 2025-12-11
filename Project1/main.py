# Updated main.py

import pandas as pd
import json
import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Project1.google_sheet.google_sheet_uploader import upload_to_google_sheets
from Project1.location import extract_location_data, extract_publication_name, extract_full_notice_text
from Project1.location import process_and_store_tenant_counts, count_tenants
from Project1.information_extractor import extract_auction_sites_from_html
from Project1.information_extractor import is_valid_url, clean_url

options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Define folder paths
base_path = r"F:\\eFaida\\Project1"
data_folder = os.path.join(base_path, "data")
logs_folder = os.path.join(base_path, "logs")

# Create the necessary folders if they do not exist
os.makedirs(data_folder, exist_ok=True)
os.makedirs(logs_folder, exist_ok=True)

# Set up logging
logging.basicConfig(filename=os.path.join(logs_folder, "scrape_log.txt"), level=logging.INFO)
logging.info("Scraping started.")

# Initialize Chrome driver
service = Service("c:\\chromedriver\\chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()
wait = WebDriverWait(driver, 15)

# Open the website
url = "https://www.capublicnotice.com/search/query?page=1&size=24&view=list&showExtended=false&startRange=&keywords=&firstDate=03%2F27%2F2025&lastDate=04%2F03%2F2025&_categories=1&_county=&_city=&_source=&ordering=BY_DATE_DEC"
driver.get(url)

# Wait for the search bar to load and enter search criteria
wait.until(EC.presence_of_element_located((By.ID, "keywords")))

# Enter search criteria
search_box = driver.find_element(By.ID, "keywords")
search_box.clear()
search_box.send_keys("storage")

# Set the start and end dates
start_date = driver.find_element(By.NAME, "firstDate")
start_date.clear()
start_date.send_keys("01/01/2025")
start_date.send_keys(Keys.RETURN)

end_date = driver.find_element(By.NAME, "lastDate")
end_date.clear()
end_date.send_keys("02/28/2025")
end_date.send_keys(Keys.RETURN)

# Click the search button
try:
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "_search_search")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", search_button)
except Exception as e:
    print(f"Failed to click search button: {e}")
    driver.quit()
    exit()

# Wait for the results to load
time.sleep(7)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "panel.panel-result")))

# Function to extract data from a single panel
def extract_data(panel):
    data = {}

    # Extract Notice Date from the time element
    try:
        panel_html = panel.get_attribute("innerHTML")
        soup = BeautifulSoup(panel_html, "html.parser")

        time_tag = soup.find("time", {"datetime": True})
        if time_tag and time_tag.has_attr("datetime"):
            raw_date = time_tag["datetime"].split(" ")[0]
            data["Notice Date"] = raw_date
        else:
            data["Notice Date"] = "N/A"
    except Exception as e:
        data["Notice Date"] = "N/A"
        logging.error(f"Error extracting Notice Date: {e}")

    # Extract Publication Name from the h4 tag in panel-heading
    try:
        pub_name = panel.find_element(By.CSS_SELECTOR, "div.panel-heading h4").text.strip()
        data["Publication Name"] = pub_name if pub_name else "N/A"
    except Exception as e:
        data["Publication Name"] = "N/A"
        logging.error(f"Error extracting Publication Name: {e}")

    # Extract Full Text of the Notice
    full_text = extract_full_notice_text(panel, wait)
    data["Full Text of Notice"] = full_text

    # Extract Auction Sites
    auction_sites, tenant_count = extract_auction_sites_from_html(panel.get_attribute("innerHTML"), wait)
    data["Auction Sites"] = auction_sites
    data["Count of Tenants"] = tenant_count

    # Extract Location Information (from location.py)
    location_name, street_address, city, state, zip_code = extract_location_data(full_text)
    data["Location Name"] = location_name
    data["Street Address"] = street_address
    data["City"] = city
    data["State"] = state
    data["Zip Code"] = zip_code

    return data

notices = []
panels = driver.find_elements(By.CLASS_NAME, "panel.panel-result")
total_panels = len(panels)
print(f"Total panels found: {total_panels}")
for i in range(len(panels)):
    try:
        logging.info(f"Processing panel {i + 1}...")

        # Re-locate panel to avoid stale references
        panels = driver.find_elements(By.CLASS_NAME, "panel.panel-result")
        panel = panels[i]

        # Scroll and click panel to expand it
        driver.execute_script("arguments[0].scrollIntoView();", panel)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", panel)

        # Wait for panel-body to appear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "panel-body"))
        )

        # Optionally wait for text content inside panel-body
        WebDriverWait(driver, 10).until(
            lambda d: "..." not in d.find_elements(By.CLASS_NAME, "panel-body")[i].text and
                      len(d.find_elements(By.CLASS_NAME, "panel-body")[i].text.strip()) > 50
        )

        # Extract data after confirming it's fully loaded
        data = extract_data(panel)
        notices.append(data)

        logging.info(f"Extracted panel {i + 1} successfully.")

        time.sleep(1)  # small delay between panels

    except Exception as e:
        logging.error(f"Skipping panel {i + 1} due to error: {e}")
        continue

try:
    output_path = os.path.join(data_folder, "notices.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(notices, f, indent=4, ensure_ascii=False)
    logging.info(f"Scraped {len(notices)} notices.")
except Exception as e:
    logging.error(f"Error saving notices JSON file: {e}")

try:
    output_file = os.path.join(data_folder, "tenant_counts")
    process_and_store_tenant_counts(notices, output_file)
except Exception as e:
    logging.error(f"Error processing tenant counts: {e}")

upload_to_google_sheets(notices, sheet_name="Scrapping")

driver.quit()
logging.info("Scraping completed.")


