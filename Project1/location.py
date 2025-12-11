import re
import logging
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import pandas as pd

# Function to extract the publication name (from <h4> tag)
def extract_publication_name(panel_html):
    try:
        soup = BeautifulSoup(panel_html, 'html.parser')
        publication_name = soup.find("h4").get_text(strip=True) if soup.find("h4") else "N/A"
        return publication_name
    except Exception as e:
        logging.error(f"Error extracting publication name: {e}")
        return "N/A"

# Function to extract location name (e.g., "Auction", "Storage", etc.)
def extract_location_name(full_text):
    try:
        # Normalize text to reduce noise from punctuation
        normalized_text = re.sub(r'[\n,.-]', ' ', full_text)
        location_name_pattern = re.compile(r"(Storage|Auction|Center|Facility|Warehouse)[\w\s]*", re.IGNORECASE)
        location_match = location_name_pattern.search(normalized_text)
        return location_match.group(0).strip() if location_match else "N/A"
    except Exception as e:
        logging.error(f"Error extracting location name: {e}")
        return "N/A"

# Function to extract address (city, state, zip code)
def extract_address(full_text):
    try:
        normalized_text = re.sub(r'[\n,.-]', ' ', full_text)  # Normalize input for consistency
        address_match = re.search(
            r'(?P<city>[A-Z][a-zA-Z\s]+)\s+(?P<state>[A-Z]{2})\s+(?P<zip>\d{5}(?:-\d{4})?)',
            normalized_text
        )
        city = address_match.group("city") if address_match else None
        state = address_match.group("state") if address_match else None
        zip_code = address_match.group("zip") if address_match else None
        return city, state, zip_code
    except Exception as e:
        logging.error(f"Error extracting address: {e}")
        return None, None, None

# Function to extract full street address
def extract_street_address(full_text):
    try:
        normalized_text = re.sub(r'[\n,.-]', ' ', full_text)
        full_address_match = re.search(
            r'([0-9]{1,6}\s[\w\s\.,\-]+?(Ave|Avenue|St|Street|Blvd|Boulevard|Rd|Road|Dr|Drive|Ln|Lane|Way|Ct|Court))',
            normalized_text,
            re.IGNORECASE
        )
        return full_address_match.group(0).strip() if full_address_match else None
    except Exception as e:
        logging.error(f"Error extracting street address: {e}")
        return None

# Function to extract full notice text from the panel
def extract_full_notice_text(panel, wait):
    try:
        # Wait for the full notice text to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//p[contains(@class, 'linkify') and @itemprop='description']")))

        # Use XPath to locate the full notice text
        full_text = panel.find_element(By.XPATH, "//p[contains(@class, 'linkify') and @itemprop='description']").text.strip()
        return full_text if full_text else "N/A"
    except Exception as e:
        logging.error(f"Error extracting Full Text of Notice: {e}")
        return "N/A"

# Function to extract the notice date (e.g., "03/27/2025")
def extract_notice_date(panel, wait):
    try:
        # Wait until the notice date is available
        WebDriverWait(panel, 10).until(EC.presence_of_element_located((By.XPATH, "//time[@datetime]")))

        # Extract the notice date
        panel_html = panel.get_attribute("outerHTML")
        soup = BeautifulSoup(panel_html, "html.parser")
        time_tag = soup.find("time", {"datetime": True})
        if time_tag and "datetime" in time_tag.attrs:
            return time_tag["datetime"].split(" ")[0]
        else:
            logging.warning("Notice date <time> tag or datetime attribute not found.")
            return "N/A"
    except Exception as e:
        logging.error(f"Error extracting notice date: {e}")
        return "N/A"

# Function to extract all location-related information
def extract_location_data(full_text):
    try:
        location_name = extract_location_name(full_text)
        street_address = extract_street_address(full_text)
        city, state, zip_code = extract_address(full_text)
        logging.info(f"Extracted Location Data: Location Name: {location_name}, Street Address: {street_address}, City: {city}, State: {state}, Zip Code: {zip_code}")
        return location_name, street_address, city, state, zip_code
    except Exception as e:
        logging.error(f"Error extracting location data: {e}")
        return "N/A", None, None, None, None

def count_tenants(full_text):
    return len(re.findall(r'\btenants?\b', full_text, re.IGNORECASE))

def process_and_store_tenant_counts(notices, output_file):
    try:
        tenant_data = []

        for notice in notices:
            full_text = notice.get("full_text", "")
            tenant_count = count_tenants(full_text)
            tenant_data.append({
                "notice_id": notice.get("id", "N/A"),
                "tenant_count": tenant_count
            })

        logging.info(f"Tenant data saved to {output_file}.json and {output_file}.xlsx")
    except Exception as e:
        logging.error(f"Error processing and storing tenant counts: {e}")