import re
from bs4 import BeautifulSoup
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to extract the notice date (e.g., "03/27/2025")
def extract_notice_date(panel, wait):
    try:
        if not hasattr(panel, "get_attribute"):
            raise ValueError("Input to extract_notice_date must be a Selenium WebElement.")

        # Wait for the panel to load fully (if necessary)
        WebDriverWait(panel, 10).until(EC.presence_of_element_located((By.XPATH, "//time[@datetime]")))

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


def extract_auction_sites_from_html(panel_html, wait):
    try:
        # Parse the panel HTML
        soup = BeautifulSoup(panel_html, 'html.parser')
        auction_sites = set()

        # Extract the full text of the notice
        full_text = soup.get_text()

        # Define a regex pattern to match auction site URLs
        # This pattern matches URLs starting with "http", "www", or "http" and ending with ".com"
        # It will capture URLs like http://example.com, www.example.com, and others that end with .com
        text_urls = re.findall(r'(https?://\S+\.com|\S+\.com)', full_text)
        print(f"Extracted URLs: {text_urls}")

        # Add each valid auction site URL to the set
        for url in text_urls:
            if is_valid_url(url):
                auction_sites.add(clean_url(url))

        # Count auction sites
        auction_sites_count = len(auction_sites)  # Count number of unique auction sites

        # Log the extracted auction sites and their count
        logging.info(f"Extracted Auction Sites: {list(auction_sites)}")
        logging.info(f"Total Auction Sites Count: {auction_sites_count}")

        # Return both the list of auction sites and the count
        return list(auction_sites), auction_sites_count

    except Exception as e:
        logging.error(f"Error extracting auction sites: {e}")
        return [], 0


# Helper function to validate TLDs (Top-Level Domains)
def is_valid_url(url):
    # Only allow valid URLs that end in .com, .org, .net, etc.
    return bool(re.search(r'\.(com|org|net|gov|edu|info|biz|co\.\w+|io|me|app|site|store)\b', url, re.IGNORECASE))


# Clean trailing punctuation from URLs
def clean_url(url):
    # Strip leading/trailing whitespace and remove common punctuation characters at the end
    return url.strip().rstrip('.,);:]')

