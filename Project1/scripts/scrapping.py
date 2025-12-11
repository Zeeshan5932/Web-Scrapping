import json
import time
import logging
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def extract_data(panel):
    """
    Extracts data from a single panel.
    """
    data = {}

    try:
        # Extract full text of notice
        full_text = panel.find_element(By.CLASS_NAME, "linkify").text.strip()
        data["Full Text of Notice"] = full_text

        # Extract publication name
        panel_html = panel.get_attribute("outerHTML")
        soup = BeautifulSoup(panel_html, "html.parser")
        publication_name = soup.find("h4").get_text(strip=True) if soup.find("h4") else "N/A"
        data["Publication Name"] = publication_name

        # Extract notice date
        time_tag = soup.find("time", {"datetime": True})
        data["Notice Date"] = time_tag["datetime"].split(" ")[0] if time_tag else "N/A"

        # Extract additional details (if available)
        details = soup.find("dl", class_="enhDetails")
        data["Additional Details"] = details.get_text(strip=True) if details else "N/A"

    except Exception as e:
        logging.error(f"Error extracting data from panel: {e}")

    return data

def scrape_data(driver, wait, data_folder):
    """
    Scrapes data from all panels on the site and saves it to a JSON file.
    """
    notices = []  # Initialize the list to store all notices

    try:
        # Wait for the results to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "panel.panel-result")))
        logging.info("Results loaded.")

        # Get all panels
        panels = driver.find_elements(By.CLASS_NAME, "panel.panel-result")
        logging.info(f"Found {len(panels)} panels.")

        for i, panel in enumerate(panels):
            try:
                logging.info(f"Processing panel {i+1}...")
                driver.execute_script("arguments[0].scrollIntoView();", panel)
                time.sleep(0.5)

                # Extract data from the panel
                data = extract_data(panel)
                notices.append(data)  # Append the extracted data to the notices list
                logging.info(f"Panel {i+1} data extracted successfully.")
            except Exception as e:
                logging.error(f"Error processing panel {i+1}: {e}")
                continue

        try:
            # Ensure the output directory exists
            os.makedirs(data_folder, exist_ok=True)

            # Save the data to the JSON file
            output_path = os.path.join(data_folder, "notices.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(notices, f, indent=4, ensure_ascii=False)
            logging.info(f"Data successfully saved to {output_path}.")
        except Exception as e:
            logging.error(f"Error saving data to JSON file: {e}")
    except Exception as e:
        logging.error(f"Error in scrape_data: {e}")
    finally:
        logging.info("Scraping process completed.")