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
from Project1.location import extract_location_data  # Importing the extract_location_data function from location.py


options = Options()
options.add_argument('--headless')
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
search_box.send_keys("http://jmichaelsauctions.com")

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

# Function to extract auction sites from HTML
def extract_auction_sites_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    auction_sites = []
    links = soup.find_all('a', href=True)
    for link in links:
        url = link['href']
        if re.match(r'^https?://(www\.)?.*\.com$', url):  # Match URLs with .com
            auction_sites.append(url)
    return auction_sites

# Function to extract full notice text from the panel
def extract_full_notice_text(panel):
    try:
        # Use XPath for more flexible selection of full notice text
        full_text = panel.find_element(By.XPATH, "//p[contains(@class, 'linkify') and @itemprop='description']").text.strip()
        return full_text if full_text else "N/A"
    except Exception as e:
        logging.error(f"Error extracting Full Text of Notice: {e}")
        return "N/A"

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
    full_text = extract_full_notice_text(panel)
    data["Full Text of Notice"] = full_text

    # Scrape auction sites and tenant count for each panel
    auction_sites = extract_auction_sites_from_html(panel.get_attribute("innerHTML"))
    tenant_count = len(auction_sites)  # Count the number of auction sites (assuming each represents a tenant)
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

# Scrape all panels using the enhanced method
notices = []
panels = driver.find_elements(By.CLASS_NAME, "panel.panel-result")
for i, panel in enumerate(panels):
    try:
        logging.info(f"Processing panel {i+1}...")
        driver.execute_script("arguments[0].scrollIntoView();", panel)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", panel)
        time.sleep(2)

        data = extract_data(panel)
        notices.append(data)

        # Escape modal (if opened)
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ESCAPE)
        time.sleep(3)

        # Refresh panels in case of DOM changes
        panels = driver.find_elements(By.CLASS_NAME, "panel.panel-result")
    except Exception as e:
        logging.error(f"Skipping panel {i+1} due to error: {e}")
        continue

# Save the data to the same JSON file
try:
    with open(os.path.join(data_folder, "notices.json"), "w", encoding="utf-8") as f:
        json.dump(notices, f, indent=4, ensure_ascii=False)
    logging.info(f"Scraped {len(notices)} notices.")
except Exception as e:
    logging.error(f"Error saving notices JSON file: {e}")

# Close the browser
driver.quit()
logging.info("Scraping completed.")
