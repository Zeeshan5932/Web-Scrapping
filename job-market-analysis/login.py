from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def handle_login(username, password):
    driver = webdriver.Chrome(executable_path="path_to_chromedriver")
    driver.get("https://www.glassdoor.com/profile/login_input.htm")
    
    time.sleep(2)  # Wait for the page to load
    
    # Enter username and password
    driver.find_element(By.ID, "userEmail").send_keys(username)
    driver.find_element(By.ID, "userPassword").send_keys(password)
    
    # Submit the login form
    driver.find_element(By.CLASS_NAME, "gd-btn").click()
    
    time.sleep(5)  # Wait for the login to complete
    
    # Check if login is successful (you can customize the check based on the page structure)
    if driver.current_url == "https://www.glassdoor.com/":
        print("Login successful!")
    else:
        print("Login failed!")
    
    return driver  # Return the driver for further actions
