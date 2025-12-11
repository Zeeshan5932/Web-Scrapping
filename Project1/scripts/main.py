import os
import logging
from driver_setup import setup_driver
from date_range import set_date_range_and_search
from scrapping import scrape_data

# Define folder paths
base_path = r"F:\\eFaida\\Project1"
data_folder = os.path.join(base_path, "data")
logs_folder = os.path.join(base_path, "logs")

# Create necessary folders
os.makedirs(data_folder, exist_ok=True)
os.makedirs(logs_folder, exist_ok=True)

# Set up logging
log_file_path = os.path.join(logs_folder, "scrape_log.txt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)
logging.info("Scraping process started.")

# Main function
def main():
    # Set up the WebDriver
    driver, wait = setup_driver()

    try:
        # Set date range and search
        keyword = "storage"
        start_date = "01/01/2025"
        end_date = "02/28/2025"
        logging.info(f"Setting date range and searching for keyword: {keyword}")
        set_date_range_and_search(driver, wait, keyword=keyword, start_date=start_date, end_date=end_date)

        # Scrape data
        output_path = os.path.join(data_folder, "notices.json")
        logging.info(f"Scraping data and saving to: {output_path}")
        scrape_data(driver, wait, output_path)
    except Exception as e:
        logging.error(f"An error occurred during the scraping process: {e}")
    finally:
        # Quit the WebDriver
        driver.quit()
        logging.info("Scraping process completed.")

# Entry point
if __name__ == "__main__":
    main()