import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import logging

def setup_driver():
    """
    Sets up the Selenium WebDriver with Chrome options.
    Returns the driver and WebDriverWait instance.
    """
    try:
        # Set Chrome options
        options = Options()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')  # Prevent shared memory issues
        options.add_argument('--start-maximized')  # Start maximized for better visibility

        # # Add a custom user-agent
        # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.84 Safari/537.36"
        # options.add_argument(f"user-agent={user_agent}")

        service = Service("c:\\chromedriver\\chromedriver.exe")
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        wait = WebDriverWait(driver, 15)

        logging.info("WebDriver setup completed successfully.")
        return driver, wait
    except Exception as e:
        logging.error(f"Error setting up WebDriver: {e}")
        raise