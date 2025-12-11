# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from time import sleep
# import os
# import random
# from main import setup_driver, extract_address_from_html

# # Google Sheets API setup
# scope = [
#     "https://spreadsheets.google.com/feeds",
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive.file",
#     "https://www.googleapis.com/auth/drive"
# ]

# credentials_path = os.path.join("scrapping sites\credentials\credentials.json")

# creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
# client = gspread.authorize(creds)
# sheet = client.open("test google search").sheet1

# # Read URLs from column B starting row 2 (skip header)
# urls = sheet.col_values(2)[1:]

# def worker(row_num, url):
#     url = url.strip()
#     if not url:
#         return (row_num, "Empty URL")

#     print(f"Processing row {row_num}: {url}")

#     driver = None
#     try:
#         driver = setup_driver()
#         driver.get(url)
#         # Random delay to mimic human behavior and reduce CAPTCHA chances
#         sleep(random.uniform(3, 7))

#         html = driver.page_source
#         address = extract_address_from_html(html)

#         print(f"Row {row_num} address found: {address}")
#         return (row_num, address)

#     except Exception as e:
#         print(f"Error on row {row_num} for URL {url}: {e}")
#         return (row_num, "Error")

#     finally:
#         if driver:
#             driver.quit()

# def main():
#     url_rows = list(enumerate(urls, start=2))  # Start at row 2 due to header

#     max_workers = 3  # Control concurrency to reduce CAPTCHA chances
#     results = []

#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = {executor.submit(worker, row, url): (row, url) for row, url in url_rows}

#         for future in as_completed(futures):
#             row_num, address = future.result()
#             results.append((row_num, address))
#             # Random delay between tasks
#             sleep(random.uniform(5, 10))

#     # Update Google Sheet column C with addresses
#     for row_num, address in results:
#         try:
#             sheet.update_cell(row_num, 3, address)
#             print(f"Updated row {row_num} in sheet with address.")
#             sleep(1)  # small delay between updates to avoid rate limiting
#         except Exception as e:
#             print(f"Failed to update row {row_num}: {e}")

#     print("✅ All done!")

# if __name__ == "__main__":
#     main()


import gspread
from oauth2client.service_account import ServiceAccountCredentials
from concurrent.futures import ProcessPoolExecutor, as_completed
from time import sleep
import os
import random
from main import setup_driver, extract_address_from_html

# Google Sheets API setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Use raw string or double backslashes to avoid escape issues on Windows
credentials_path = os.path.join("scrapping sites\credentials\credentials.json")

creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)
sheet = client.open("test google search").sheet1

# Read URLs from column B starting row 2 (skip header)
urls = sheet.col_values(2)[1:]

def worker(row_num_url):
    row_num, url = row_num_url
    url = url.strip()
    if not url:
        return (row_num, "Empty URL")
        
    print(f"Processing row {row_num}: {url}")
    driver = None
    try:
        driver = setup_driver()
        driver.get(url)
        sleep(random.uniform(3, 7))  # Random delay to reduce CAPTCHA chances

        html = driver.page_source
        address = extract_address_from_html(html)
        
        # If extract_address_from_html returns list, join them
        if isinstance(address, list):
            if address:
                address = '; '.join(address)
            else:
                address = "Address not found"

        print(f"Row {row_num} address found: {address}")
        return (row_num, address)

    except Exception as e:
        print(f"Error on row {row_num} for URL {url}: {e}")
        return (row_num, "Error")

    finally:
        if driver:
            driver.quit()

def main():
    url_rows = list(enumerate(urls, start=2))  # Starting at row 2 because of header

    max_workers = 3  # Control concurrency to avoid CAPTCHA and resource exhaustion
    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker, row_num_url): row_num_url for row_num_url in url_rows}

        for future in as_completed(futures):
            row_num, address = future.result()
            results.append((row_num, address))
            sleep(random.uniform(5, 10))  # Delay between tasks

    # Update Google Sheet column C with results
    for row_num, address in results:
        try:
            sheet.update_cell(row_num, 3, address)
            print(f"Updated row {row_num} in sheet with address.")
            sleep(1)  # small delay between updates to avoid rate limits
        except Exception as e:
            print(f"Failed to update row {row_num}: {e}")

    print("✅ All done!")

if __name__ == "__main__":
    main()

