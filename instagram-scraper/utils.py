from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_random_user_agent():
    """Return a random user agent to avoid detection"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(user_agents)

def login_instagram(driver, retry_count=2):
    """
    Login to Instagram with error handling and retry logic
    
    Args:
        driver: Selenium WebDriver instance
        retry_count: Number of login retries if it fails
    """
    # Get username and password from environment variables
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    if not username or not password:
        raise ValueError("Instagram username or password not set in .env file!")
    
    # Add a random delay to appear more human-like
    time.sleep(random.uniform(1.5, 3))
    
    for attempt in range(retry_count + 1):
        try:
            # Navigate to Instagram login page
            driver.get("https://www.instagram.com/accounts/login/")
            
            # Wait for the login page to load properly
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            # Add a small delay before typing to mimic human behavior
            time.sleep(random.uniform(0.5, 1.5))

            # Input username with random typing speed
            username_field = driver.find_element(By.NAME, "username")
            username_field.clear()
            for char in username:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))  # Random delay between keystrokes
            
            # Add a brief pause between username and password entry
            time.sleep(random.uniform(0.5, 1))
            
            # Input password with random typing speed
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            for char in password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))  # Random delay between keystrokes
            
            # Click the login button instead of pressing Enter
            try:
                login_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                )
                login_button.click()
            except:
                # Fall back to pressing Enter if button not found
                password_field.send_keys(Keys.RETURN)
            
            # Wait for login to complete by looking for specific elements on the home page
            WebDriverWait(driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/inbox/')]")),
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/explore/')]")),
                    EC.presence_of_element_located((By.XPATH, "//span[text()='Search']"))
                )
            )
            
            print("Successfully logged in to Instagram")
            break  # Break out of retry loop if successful
            
        except Exception as e:
            if attempt < retry_count:
                print(f"Login attempt {attempt+1} failed: {str(e)}. Retrying...")
                time.sleep(random.uniform(3, 5))  # Wait before retrying
            else:
                print(f"Failed to login after {retry_count+1} attempts: {str(e)}")
                raise
    
    # Handle potential popups with better error handling
    handle_post_login_popups(driver)
    
    return driver

def handle_post_login_popups(driver):
    """Handle various popups that might appear after Instagram login"""
    
    # List of possible popup patterns to handle
    popups = [
        {"text": "Not Now", "by": By.XPATH, "value": "//button[contains(text(), 'Not Now')]"},
        {"text": "Save Info", "by": By.XPATH, "value": "//button[text()='Save Info']"},
        {"text": "Not Now", "by": By.XPATH, "value": "//div[@role='button'][text()='Not Now']"}, 
        {"text": "Cancel", "by": By.XPATH, "value": "//button[text()='Cancel']"}
    ]
    
    # Try to handle each possible popup
    for popup in popups:
        try:
            button = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((popup["by"], popup["value"]))
            )
            print(f"Clicked '{popup['text']}' popup")
            button.click()
            time.sleep(1)  # Short wait after clicking
        except (TimeoutException, NoSuchElementException):
            # This popup was not found, which is fine
            pass
