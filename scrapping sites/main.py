import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument(f"user-agent={get_random_user_agent()}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chromedriver_path = "C:\\chromedriver\\chromedriver.exe"  # Change to your chromedriver path
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def extract_address_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Find the div with data-local-attribute="d3adr" which holds the address
    address_div = soup.find("div", attrs={"data-local-attribute": "d3adr"})
    if address_div:
        address_span = address_div.find("span", class_="LrzXr")
        if address_span:
            return address_span.text.strip()

    return "Address not found"

def extract_address_with_regex(html):
    """
    Extract address text from the HTML using regex pattern matching
    targeting the div with data-local-attribute="d3adr" and the span with class LrzXr.
    """

    # Regex pattern to capture address inside <span class="LrzXr">...</span> within the div
    pattern = re.compile(
        r'<div[^>]*data-local-attribute="d3adr"[^>]*>.*?<span[^>]*class="LrzXr"[^>]*>(.*?)</span>',
        re.DOTALL
    )

    match = pattern.search(html)
    if match:
        address = match.group(1).strip()
        return address
    return "Address not found"
