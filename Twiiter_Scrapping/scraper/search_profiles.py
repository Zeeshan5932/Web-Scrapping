import json, os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def search_profiles(driver, keyword, scrolls=5):
    safe_keyword = keyword.lower().replace(" ", "_")
    os.makedirs(f"data/{safe_keyword}", exist_ok=True)
    search_url = f"https://twitter.com/search?q={keyword}&f=user"
    driver.get(search_url)
    time.sleep(3)

    for _ in range(scrolls):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)

    profiles = driver.find_elements(By.XPATH, '//a[contains(@href, "/") and not(contains(@href, "/status/"))]')
    urls = list(set([p.get_attribute('href') for p in profiles if p.get_attribute('href') and "/status/" not in p.get_attribute('href')]))

    with open(f"data/{safe_keyword}/profile_urls.json", "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=4)

    print(f"[✔] Saved {len(urls)} profile URLs to data/{safe_keyword}/profile_urls.json")
