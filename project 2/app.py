# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from url_checker_fixed import check_url  # Import the fixed check_url function
# from time import sleep
# import os

# # Define the scope for Google Sheets API
# scope = [
#     "https://spreadsheets.google.com/feeds",
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive.file",
#     "https://www.googleapis.com/auth/drive"
# ]

# # Path to credentials
# credentials_path = os.path.join("project 2", "credentials", "credentials.json")

# # Authenticate using the credentials JSON file
# creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
# client = gspread.authorize(creds)

# # Open the sheet (replace with your spreadsheet name)
# sheet = client.open("test google search").sheet1

# # Get all URLs from column B (index 2), skip the header
# urls = sheet.col_values(2)[1:]

# # Loop through each URL and update the status in column C (index 3)
# print(f"Found {len(urls)} URLs to check...\n")

# for index, url in enumerate(urls, start=2):  # Starting from row 2
#     if not url or url.strip() == "":
#         print(f"Skipping empty URL at row {index}")
#         continue

#     print(f"Checking URL {index - 1}/{len(urls)}: {url}")
#     try:
#         status = check_url(url.strip())
#         sheet.update_cell(index, 3, status)
#         print(f"  ➤ Status: {status}\n")
#         sleep(1.5)  # Delay to avoid rate limits
#     except Exception as e:
#         print(f"Error checking URL {url}: {str(e)}")
#         try:
#             sheet.update_cell(index, 3, "Error")
#         except:
#             print(f"Could not update sheet for URL at row {index}")

# print("\n✅ URL check and status update complete.")




import gspread
from oauth2client.service_account import ServiceAccountCredentials
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
import os
import random
from url_checker_fixed import check_url, is_captcha_page  # Import the function from your module
from captcha_handler import solve_captcha_manually, handle_captcha_with_proxy_rotation

# Google Sheets API setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

credentials_path = os.path.join("project 2", "credentials", "credentials.json")

creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)

sheet = client.open("test google search").sheet1

# Read URLs from column B (index 2), skipping header
urls = sheet.col_values(2)[1:]

# Storage for cookies after CAPTCHA solving
captcha_cookies = None

def worker(url_row):
    global captcha_cookies
    index, url = url_row
    url = url.strip()
    if not url:
        return (index, "Empty URL")
        
    print(f"Processing row {index} : {url}")
    
    # Add a random delay between 3-7 seconds before each request
    random_delay = random.uniform(3, 7)
    sleep(random_delay)
    
    max_retries = 3
    current_try = 0
    
    while current_try < max_retries:
        try:
            # Pass cookies if we have them from a previous CAPTCHA solve
            address = check_url(url, cookies=captcha_cookies)
            
            # Check if result indicates CAPTCHA
            if "captcha" in str(address).lower():
                print(f"⚠️ CAPTCHA detected at row {index}. Attempting to solve...")
                
                # Option 1: Try solving the CAPTCHA manually
                captcha_solved, new_cookies = solve_captcha_manually(url)
                
                if captcha_solved and new_cookies:
                    captcha_cookies = new_cookies
                    print("Retrying with new cookies...")
                    sleep(2)
                    continue
                    
                # Option 2: Try rotating proxies (if manual solving fails)
                # proxy = handle_captcha_with_proxy_rotation()
                # if proxy:
                #     print("Retrying with new proxy...")
                #     sleep(10)
                #     continue
                
                # If all CAPTCHA handling methods fail
                current_try += 1
                print(f"CAPTCHA handling attempt {current_try} failed. Waiting before retry...")
                sleep(random.uniform(60, 120))  # Wait 1-2 minutes before retry
                continue
                
            print(f"Row {index} done: {address}")
            return (index, address)
            
        except Exception as e:
            print(f"Error at row {index}: {e}")
            current_try += 1
            if current_try < max_retries:
                print(f"Retrying... Attempt {current_try+1}/{max_retries}")
                sleep(random.uniform(10, 20))  # Wait 10-20 seconds before retry
            else:
                return (index, "Error after multiple attempts")
    
    return (index, "Failed - possible CAPTCHA block")

def main():
    url_rows = list(enumerate(urls, start=2))  # row numbers start at 2
    
    # Check if we're continuing a previously interrupted run
    existing_results = sheet.col_values(3)[1:]  # Get existing results
    
    # Filter out URLs that have already been processed
    remaining_url_rows = []
    for i, (index, _) in enumerate(url_rows):
        if i < len(existing_results) and existing_results[i] and existing_results[i] != "Error" and "Failed" not in existing_results[i] and "CAPTCHA" not in existing_results[i]:
            print(f"Skipping row {index} (already processed)")
            continue
        remaining_url_rows.append(url_rows[i])
    
    print(f"Found {len(remaining_url_rows)} URLs to process out of {len(url_rows)} total")
    
    if not remaining_url_rows:
        print("✅ All URLs already processed.")
        return
    
    results = []

    # Reduced concurrency to avoid triggering CAPTCHA
    max_workers = 1  # Sequential processing to avoid CAPTCHA
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker, url_row): url_row for url_row in remaining_url_rows}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            # Longer delay between completing requests
            sleep(random.uniform(5, 10))  # Random delay between 5-10 seconds

    # Write addresses back to column C (index 3)
    for row_num, address in results:
        try:
            sheet.update_cell(row_num, 3, address)
            print(f"Updated row {row_num} with: {address}")
            # Add small delay between sheet updates
            sleep(1)
        except Exception as e:
            print(f"Failed to update row {row_num}: {e}")

    print("✅ All URLs processed and addresses updated in Google Sheet.")

if __name__ == "__main__":
    main()

