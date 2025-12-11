# import time
# import logging
# import json
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium import webdriver
# from bs4 import BeautifulSoup
# import os
# import re

# # Setup logging
# logs_folder = os.path.join(os.path.dirname(__file__), "..", "logs")
# os.makedirs(logs_folder, exist_ok=True)

# logging.basicConfig(filename=os.path.join(logs_folder, "scrape_log.txt"), level=logging.INFO)
# logging.info("Scraping started.")

# # Setup WebDriver options
# options = Options()
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')

# # Initialize WebDriver
# service = Service("c:\\chromedriver\\chromedriver.exe")
# driver = webdriver.Chrome(service=service, options=options)
# wait = WebDriverWait(driver, 15)

# # Define data folder path
# data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
# os.makedirs(data_folder, exist_ok=True)

# def extract_full_notice_text(panel, wait):
#     try:
#         # Wait for the <p> tag with class 'linkify' and itemprop='description' to be present
#         wait.until(EC.presence_of_element_located((By.XPATH, "//p[contains(@class, 'linkify') and @itemprop='description']")))

#         # Extract the full text content of the <p> tag using XPath
#         full_text = panel.find_element(By.XPATH, "//p[contains(@class, 'linkify') and @itemprop='description']").text.strip()
#         print(f"Full Text of Notice: {full_text}")

#         # Clean up the text: remove newlines and replace periods with a single space
#         cleaned_text = re.sub(r'[\n]+', ' ', full_text)  # Replace newline characters with space
#         cleaned_text = re.sub(r'\s+\.', ' ', cleaned_text)  # Remove periods with a whitespace if preceded by spaces
#         cleaned_text = re.sub(r'[\.]+', ' ', cleaned_text)  # Replace multiple periods with a space
#         cleaned_text = cleaned_text.strip()  # Remove any leading/trailing spaces after cleaning

#         return cleaned_text if cleaned_text else "N/A"

#     except Exception as e:
#         logging.error(f"Error extracting full text from the panel: {e}")
#         return "N/A"

# # Open website and scrape
# def scrape_notices(url, search_keywords, start_date_str, end_date_str):
#     driver.get(url)

#     # Wait for the search bar to load
#     wait.until(EC.presence_of_element_located((By.ID, "keywords")))
#     driver.find_element(By.ID, "keywords").send_keys(search_keywords)

#     # Set start and end dates
#     driver.find_element(By.NAME, "firstDate").clear()
#     driver.find_element(By.NAME, "firstDate").send_keys(start_date_str)
#     driver.find_element(By.NAME, "lastDate").clear()
#     driver.find_element(By.NAME, "lastDate").send_keys(end_date_str)

#     # Click Search button
#     search_btn = wait.until(EC.element_to_be_clickable((By.ID, "_search_search")))
#     driver.execute_script("arguments[0].click();", search_btn)

#     # Wait for results
#     time.sleep(6)
#     panels = driver.find_elements(By.CLASS_NAME, "panel.panel-result")
#     print(f"Found {len(panels)} panels")

#     notices = []
#     for i, panel in enumerate(panels):
#         try:
#             logging.info(f"Processing panel {i + 1}...")

#             # Re-locate panel to avoid stale references
#             panels = driver.find_elements(By.CLASS_NAME, "panel.panel-result")
#             panel = panels[i]

#             # Scroll and click to expand
#             driver.execute_script("arguments[0].scrollIntoView();", panel)
#             time.sleep(0.5)
#             driver.execute_script("arguments[0].click();", panel)

#             # Wait for panel-body to load and be visible
#             wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "panel-body")))

#             # Extract full notice text using the new function
#             notice_text = extract_full_notice_text(panel, wait)
#             notices.append({"Full Text of Notice": notice_text})

#             # Optional: close panel by clicking again
#             driver.execute_script("arguments[0].click();", panel)
#             time.sleep(0.5)

#         except Exception as e:
#             logging.error(f"Skipping panel {i + 1} due to error: {e}")
#             continue

#     # Save notices to JSON
#     output_file = os.path.join(data_folder, "notices_minimal.json")
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(notices, f, indent=4, ensure_ascii=False)

#     logging.info("Scraping completed.")
#     driver.quit()


import time
import logging
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import re

# Setup logging
logs_folder = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(logs_folder, exist_ok=True)

logging.basicConfig(filename=os.path.join(logs_folder, "scrape_log.txt"), level=logging.INFO)
logging.info("Scraping started.")

# Setup WebDriver options
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Initialize WebDriver
service = Service("c:\\chromedriver\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

# Define data folder path
data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(data_folder, exist_ok=True)

# Function to clean extracted text
def clean_text(full_text):
    # Remove newlines, replace periods and commas with space
    cleaned_text = re.sub(r'[\n]+', ' ', full_text)  # Replace newline characters with space
    cleaned_text = re.sub(r'[.,;]+', ' ', cleaned_text)  # Replace periods, commas, semicolons with space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with a single space
    return cleaned_text.strip()  # Remove any leading/trailing spaces after cleaning

# Function to extract full notice text
def extract_full_notice_text(panel, wait):
    try:
        # Wait for the <p> tag with class 'linkify' and itemprop='description' to be present
        wait.until(EC.presence_of_element_located((By.XPATH, "//p[contains(@class, 'linkify') and @itemprop='description']")))

        # Extract the full text content of the <p> tag using XPath
        full_text = panel.find_element(By.XPATH, "//p[contains(@class, 'linkify') and @itemprop='description']").text.strip()
        logging.info(f"Full Text of Notice: {full_text}")

        # Clean up the text using the clean_text function
        cleaned_text = clean_text(full_text)
        
        return cleaned_text if cleaned_text else "N/A"
    except Exception as e:
        logging.error(f"Error extracting full text from the panel: {e}")
        return "N/A"

# Open website and scrape
def scrape_notices(url, search_keywords, start_date_str, end_date_str):
    driver.get(url)

    # Wait for the search bar to load
    wait.until(EC.presence_of_element_located((By.ID, "keywords")))
    driver.find_element(By.ID, "keywords").send_keys(search_keywords)

    # Set start and end dates
    driver.find_element(By.NAME, "firstDate").clear()
    driver.find_element(By.NAME, "firstDate").send_keys(start_date_str)
    driver.find_element(By.NAME, "lastDate").clear()
    driver.find_element(By.NAME, "lastDate").send_keys(end_date_str)

    # Click Search button
    search_btn = wait.until(EC.element_to_be_clickable((By.ID, "_search_search")))
    driver.execute_script("arguments[0].click();", search_btn)

    # Wait for results
    time.sleep(6)

     # Get all panels once
    panels = driver.find_elements(By.CLASS_NAME, "panel.panel-result")
    total = len(panels)
    logging.info(f"Found {total} panels")

    notices = []

    if total >= 293:
        # Select first, middle, and last 5 panels
        first_panels = [(panels[i], "first") for i in range(5)]
        mid_start = total // 2 - 2  # Center-ish 5
        middle_panels = [(panels[i], "middle") for i in range(mid_start, mid_start + 5)]
        last_panels = [(panels[i], "last") for i in range(total - 5, total)]

        selected_panels = first_panels + middle_panels + last_panels
    else:
        # Fallback: use all available panels
        selected_panels = [(panel, "all") for panel in panels]

    # Now scrape selected panels
    for i, (panel, source) in enumerate(selected_panels):
        try:
            logging.info(f"Processing panel {i + 1} from {source}...")

            driver.execute_script("arguments[0].scrollIntoView();", panel)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", panel)

            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "panel-body")))

            notice_text = extract_full_notice_text(panel, wait)
            notices.append({
                "Full Text of Notice": notice_text,
                "Source": source
            })

            driver.execute_script("arguments[0].click();", panel)
            time.sleep(0.5)

        except Exception as e:
            logging.error(f"Skipping panel {i + 1} from {source} due to error: {e}")
            continue
    # Save notices to JSON
    output_file = os.path.join(data_folder, "notices_minimal.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(notices, f, indent=4, ensure_ascii=False)

    logging.info("Scraping completed.")
    driver.quit()



# import time
# import logging
# import json
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium import webdriver
# from bs4 import BeautifulSoup
# import os
# import re

# # Setup logging
# logs_folder = os.path.join(os.path.dirname(__file__), "..", "logs")
# os.makedirs(logs_folder, exist_ok=True)
# logging.basicConfig(filename=os.path.join(logs_folder, "scrape_log.txt"), level=logging.INFO)
# logging.info("Scraping started.")

# # Setup WebDriver
# options = Options()
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# service = Service("c:\\chromedriver\\chromedriver.exe")  # Ensure that chromedriver path is correct
# driver = webdriver.Chrome(service=service, options=options)
# wait = WebDriverWait(driver, 15)

# # Setup data path
# data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
# os.makedirs(data_folder, exist_ok=True)

# # Clean extracted text
# def clean_text(text):
#     text = re.sub(r'[\n]+', ' ', text)
#     text = re.sub(r'[.,;]+', ' ', text)
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()

# # Extract full text directly from panel (without clicking)
# def extract_full_notice_text_from_panel(panel):
#     try:
#         soup = BeautifulSoup(panel.get_attribute("outerHTML"), "html.parser")
#         full_text = soup.select_one("p[itemprop='description']")
#         return clean_text(full_text.get_text(strip=True)) if full_text else "N/A"
#     except Exception as e:
#         logging.error(f"Error parsing full notice text: {e}")
#         return "N/A"

# # Main scraping function
# def scrape_notices(url, search_keywords, start_date_str, end_date_str):
#     driver.get(url)

#     # Wait and fill search inputs
#     wait.until(EC.presence_of_element_located((By.ID, "keywords"))).clear()
#     driver.find_element(By.ID, "keywords").send_keys(search_keywords)
#     driver.find_element(By.NAME, "firstDate").clear()
#     driver.find_element(By.NAME, "firstDate").send_keys(start_date_str)
#     driver.find_element(By.NAME, "lastDate").clear()
#     driver.find_element(By.NAME, "lastDate").send_keys(end_date_str)

#     # Trigger search
#     search_btn = wait.until(EC.element_to_be_clickable((By.ID, "_search_search")))
#     driver.execute_script("arguments[0].click();", search_btn)

#     # Wait for results to load
#     wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "panel.panel-result")))

#     panels = driver.find_elements(By.CLASS_NAME, "panel.panel-result")
#     total = len(panels)
#     logging.info(f"Found {total} panels")

#     notices = []

#     # Determine panel selection strategy
#     if total >= 15:
#         first_panels = [(panels[i], "first") for i in range(5)]
#         mid_start = total // 2 - 2
#         middle_panels = [(panels[i], "middle") for i in range(mid_start, mid_start + 5)]
#         last_panels = [(panels[i], "last") for i in range(total - 5, total)]
#         selected_panels = first_panels + middle_panels + last_panels
#     else:
#         selected_panels = [(panel, "all") for panel in panels]

#     for i, (panel, source) in enumerate(selected_panels):
#         try:
#             driver.execute_script("arguments[0].scrollIntoView();", panel)
#             time.sleep(0.3)

#             notice_text = extract_full_notice_text_from_panel(panel)
#             notices.append({
#                 "Full Text of Notice": notice_text,
#                 "Source": source
#             })

#             logging.info(f"Scraped panel {i + 1} from {source}.")

#         except Exception as e:
#             logging.error(f"Error processing panel {i + 1} ({source}): {e}")
#             continue

#     # Save to JSON
#     output_file = os.path.join(data_folder, "notices_minimal.json")
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(notices, f, indent=4, ensure_ascii=False)

#     logging.info("Scraping complete.")
#     driver.quit()

# # Run the scraper
# scrape_notices(
#     url="https://www.capublicnotice.com/search/query?page=0&size=24&view=list&showExtended=false&startRange=&keywords=http%3A%2F%2Fwww.storagetreasures.com&firstDate=01%2F01%2F2025&lastDate=02%2F28%2F2025&_categories=1&_county=&_city=&_source=&ordering=BY_DATE_DEC",
#     search_keywords="http://www.storagetreasures.com",
#     start_date_str="01/01/2025",
#     end_date_str="02/28/2025"
# )


