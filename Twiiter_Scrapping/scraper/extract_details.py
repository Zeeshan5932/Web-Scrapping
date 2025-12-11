import json
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from threading import Lock

lock = Lock()
results = []

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"\+?\d[\d\s\-()]{7,}"
LINK_REGEX = r"(https?://[^\s]+)"

def init_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_regex(text):
    return {
        "emails": re.findall(EMAIL_REGEX, text),
        "phones": re.findall(PHONE_REGEX, text),
        "links": re.findall(LINK_REGEX, text)
    }

def scrape_profile(url):
    driver = init_browser()
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        name = soup.find("div", attrs={"data-testid": "UserName"})
        bio = soup.find("div", {"data-testid": "UserDescription"})
        location = soup.find("span", {"data-testid": "UserLocation"})

        name_text = name.get_text(strip=True) if name else ""
        bio_text = bio.get_text(strip=True) if bio else ""
        location_text = location.get_text(strip=True) if location else ""

        # Combine all visible text for regex
        visible_text = soup.get_text(" ", strip=True)
        regex_data = extract_regex(visible_text)

        data = {
            "url": url,
            "name": name_text,
            "bio": bio_text,
            "location": location_text,
            "emails": list(set(regex_data["emails"])),
            "phones": list(set(regex_data["phones"])),
            "links": list(set(regex_data["links"]))
        }

        with lock:
            results.append(data)

    except Exception as e:
        print(f"[✘] Error scraping {url}: {e}")
    finally:
        driver.quit()

def process_profiles(queue: deque, output_path: str, max_to_process=10, max_threads=3):
    selected_urls = list(queue)[:max_to_process]

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(scrape_profile, selected_urls)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"[✔] Extracted and saved {len(results)} profile(s)")
