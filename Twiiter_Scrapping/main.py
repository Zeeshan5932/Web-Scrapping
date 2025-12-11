from config.settings import *
from scraper.login import login
from scraper.search_profiles import search_profiles
from scraper.extract_details import process_profiles
from collections import deque
import os, json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def run():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        login(driver, TWITTER_USERNAME, TWITTER_PASSWORD)
        keyword = input("Enter designation to search (e.g. Web Developer): ").strip()
        safe_keyword = keyword.lower().replace(" ", "_")
        data_dir = f"data/{safe_keyword}"
        os.makedirs(data_dir, exist_ok=True)

        search_profiles(driver, keyword, scrolls=SCROLL_COUNT)

        input("\n[✔] URLs saved. Press Enter to start extracting profile details...")

        with open(f"{data_dir}/profile_urls.json", "r", encoding="utf-8") as f:
            profile_urls = json.load(f)

        to_extract = int(input(f"Found {len(profile_urls)} profiles. How many profiles do you want to extract? "))

        from collections import deque
        queue = deque(profile_urls)
        output_path = f"{data_dir}/profile_details.json"

        process_profiles(queue, output_path, max_to_process=to_extract)

    finally:
        driver.quit()

if __name__ == "__main__":
    run()

