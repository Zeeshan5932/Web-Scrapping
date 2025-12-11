import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

def set_date_range_and_search(driver, wait, keyword, start_date, end_date):
    """
    Sets the date range, enters the keyword, and clicks the search button.
    """
    try:
        # Wait for the search bar to load
        logging.info("Waiting for search bar...")
        wait.until(EC.presence_of_element_located((By.ID, "keywords")))
        logging.info("Search bar loaded successfully.")

        # Enter the keyword
        search_box = driver.find_element(By.ID, "keywords")
        search_box.clear()
        search_box.send_keys(keyword)
        logging.info(f"Keyword '{keyword}' entered.")

        # Set the start date
        logging.info("Setting start date...")
        start_date_input = driver.find_element(By.NAME, "firstDate")
        start_date_input.clear()
        start_date_input.send_keys(start_date)
        start_date_input.send_keys(Keys.RETURN)
        logging.info(f"Start date '{start_date}' entered.")

        # Set the end date
        logging.info("Setting end date...")
        end_date_input = driver.find_element(By.NAME, "lastDate")
        end_date_input.clear()
        end_date_input.send_keys(end_date)
        end_date_input.send_keys(Keys.RETURN)
        logging.info(f"End date '{end_date}' entered.")

        # Click the search button
        logging.info("Waiting for search button...")
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "_search_search")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", search_button)
        logging.info("Search button clicked successfully.")

        # Wait for the results to load
        logging.info("Waiting for results to load...")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "panel.panel-result")))
        logging.info("Results loaded successfully.")
    except Exception as e:
        logging.error(f"Error in set_date_range_and_search: {e}")
        # Capture a screenshot for debugging
        screenshot_path = "error_screenshot.png"
        driver.save_screenshot(screenshot_path)
        logging.error(f"Screenshot saved to {screenshot_path}")
        driver.quit()
        exit()