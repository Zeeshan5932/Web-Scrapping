# """
# Twitter Login Module

# Handles authentication to Twitter using Selenium.
# """

# import time
# import sys
# import os

# # Add the project root directory to the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from utils.helpers import wait_for_element
# from config.settings import LOGIN_URL, USERNAME, PASSWORD

# def login_to_twitter(driver, username=None, password=None):
#     """
#     Log into Twitter with the provided credentials
    
#     Args:
#         driver: Selenium WebDriver instance
#         username: Twitter username or email (optional, uses settings.py if not provided)
#         password: Twitter password (optional, uses settings.py if not provided)
        
#     Returns:
#         bool: True if login successful, False otherwise
#     """
#     # Use credentials from settings if not provided
#     if username is None:
#         username = USERNAME
#     if password is None:
#         password = PASSWORD
        
#     # Navigate to the login page
#     driver.get(LOGIN_URL)
    
#     try:
#         print("Attempting to log in to Twitter...")
        
#         # Wait for the username field to appear
#         username_field = wait_for_element(driver, "input[autocomplete='username']")
#         if not username_field:
#             print("Username field not found on login page")
#             return False
            
#         # Enter username and press Next
#         username_field.send_keys(username)
#         username_field.send_keys(Keys.RETURN)
        
#         # Wait for password field
#         password_field = wait_for_element(driver, "input[type='password']")
#         if not password_field:
#             print("Password field not found")
#             return False
            
#         # Enter password and submit
#         password_field.send_keys(password)
#         password_field.send_keys(Keys.RETURN)
        
#         # Verify login success by checking for home timeline
#         time.sleep(3)  # Allow time for login to complete
        
#         # Check if we're on the home timeline or if there's a login error
#         if "home" in driver.current_url.lower():
#             print("Login successful!")
#             return True
#         else:
#             # Check for error messages
#             try:
#                 error_message = driver.find_element(By.CSS_SELECTOR, "[data-testid='error-detail']")
#                 print(f"Login failed: {error_message.text}")
#             except NoSuchElementException:
#                 print("Login status unclear. Please check manually.")
#             return False
            
#     except Exception as e:
#         print(f"Login error: {str(e)}")
#         return False


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def login(driver, username, password):
    driver.get("https://twitter.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text"))).send_keys(username)
    driver.find_element(By.XPATH, '//span[text()="Next"]').click()
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)
    driver.find_element(By.XPATH, '//span[text()="Log in"]').click()
    time.sleep(5)
