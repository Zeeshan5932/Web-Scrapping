from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def create_driver():
    options = Options()
    # options.add_argument('--headless')  # Uncomment to run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    service = Service("c:\\chromedriver\\chromedriver.exe")  # Path to chromedriver
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    return driver
