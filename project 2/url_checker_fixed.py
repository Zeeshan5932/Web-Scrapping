# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# import time
# import re

# def check_url(url):
#     """Checks if a URL is working via HTTP and fallback browser automation."""
#     if not re.match(r'^https?://', url):
#         url = 'https://' + url

#     print(f"Checking URL: {url}")

#     # Step 1: Fast HEAD/GET request
#     try:
#         try:
#             response = requests.head(url, timeout=10, allow_redirects=True)
#             if response.status_code < 400:
#                 print(f"  ✓ HEAD successful: {response.status_code}")
#                 return "Working"
#         except:
#             response = requests.get(url, timeout=10, allow_redirects=True)
#             if response.status_code < 400:
#                 print(f"  ✓ GET successful: {response.status_code}")
#                 return "Working"
#     except Exception as e:
#         print(f"  ! HTTP requests failed: {e}")

#     # Step 2: Try browser automation if HTTP fails
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")  # Optional: headless mode
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--disable-extensions")

#     chromedriver_path = "C:\\chromedriver\\chromedriver.exe"
#     service = Service(chromedriver_path)
#     driver = None

#     try:
#         print("  → Trying browser automation...")
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.set_page_load_timeout(20)
#         driver.get(url)
#         time.sleep(5)

#         page_title = driver.title.lower()
#         page_source = driver.page_source.lower()

#         # Look for strong error indicators
#         errors = [
#             ("404" in page_title and "not found" in page_title),
#             "this site can't be reached" in page_source,
#             "server ip address could not be found" in page_source
#         ]

#         if any(errors):
#             print("  ✗ Definite error found in page content.")
#             return "Not Working"

#         print("  ✓ Browser loaded the page successfully.")
#         return "Working"

#     except Exception as e:
#         print(f"  ! Browser error: {e}")
#         try:
#             response = requests.get(url, timeout=15, allow_redirects=True)
#             if response.status_code < 400:
#                 print("  ✓ Final fallback GET successful.")
#                 return "Working"
#         except:
#             pass
#         return "Not Working"
#     finally:
#         if driver:
#             try:
#                 driver.quit()
#             except:
#                 pass




import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def extract_address(page_source):
    address_pattern = re.compile(
        r'\d{1,5}\s\w+\s\w+.*?(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Square|Sq|Trail|Trl|Parkway|Pkwy|Circle|Cir)\.?,?\s?.*',
        re.IGNORECASE | re.DOTALL
    )
    match = address_pattern.search(page_source)
    if match:
        return match.group(0).strip()
    else:
        return "Address not found"

def is_captcha_page(page_source):
    """Check if the page contains a CAPTCHA challenge"""
    captcha_indicators = [
        "captcha",
        "robot",
        "automated requests",
        "unusual traffic",
        "verify you're a human",
        "our systems have detected unusual traffic",
        "solve the above captcha",
        "ip address:",
        "violation of the terms of service"
    ]
    
    page_source_lower = page_source.lower()
    for indicator in captcha_indicators:
        if indicator in page_source_lower:
            return True
    return False

def check_url(url, cookies=None):
    if not url:
        return "No URL"

    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    
    # Add more human-like browser settings
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Use a common user agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")

    chromedriver_path = "C:\\chromedriver\\chromedriver.exe"  # Update this path
    service = Service(chromedriver_path)
    driver = None

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)  # Increased timeout
        
        # First visit Google to set cookies
        driver.get("https://www.google.com")
        
        # Add any cookies from previous CAPTCHA solving
        if cookies:
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Error adding cookie: {e}")
        
        # Random sleep to seem more human-like
        time.sleep(random.uniform(1, 3))
        
        # Now navigate to the actual URL
        driver.get(url)
        
        # Random sleep to simulate human behavior
        time.sleep(random.uniform(3, 6))
        
        # Simulate human-like behavior by scrolling
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        time.sleep(random.uniform(1, 2))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.5);")
        time.sleep(random.uniform(1, 2))
        
        page_source = driver.page_source
        
        # Check for CAPTCHA
        if is_captcha_page(page_source):
            print(f"⚠️ CAPTCHA detected for URL: {url}")
            return "CAPTCHA detected - please try manually or change IP address"
        
        # Extract address
        address = extract_address(page_source)
        return address
        
    except Exception as e:
        print(f"Error loading URL {url}: {e}")
        return "Error loading page"
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

