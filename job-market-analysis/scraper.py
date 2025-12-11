from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def extract_job_urls(job_title, location):
    driver = webdriver.Chrome(executable_path="path_to_chromedriver")
    driver.get("https://www.glassdoor.com/Job/index.htm")

    # Step 1: Input job title and location in the search form
    search_input = driver.find_element(By.NAME, "sc.keyword")
    location_input = driver.find_element(By.NAME, "sc.location")

    search_input.send_keys(job_title)   # Job title entered by user
    location_input.send_keys(location)  # Location entered by user

    # Step 2: Press "Enter" to search
    location_input.send_keys(Keys.RETURN)

    time.sleep(5)  # Wait for results to load
    
    job_urls = []
    
    # Step 3: Extract job listings from the current page
    job_listings = driver.find_elements(By.CLASS_NAME, "jobLink")
    
    for job in job_listings:
        job_urls.append(job.get_attribute("href"))
    
    # Step 4: Handle pagination (optional) - if there are more pages to scrape
    while True:
        try:
            # Check for the next page button
            next_button = driver.find_element(By.CLASS_NAME, "nextButton")
            next_button.click()
            time.sleep(5)  # Wait for the next page to load
            
            # Extract new job listings
            job_listings = driver.find_elements(By.CLASS_NAME, "jobLink")
            for job in job_listings:
                job_urls.append(job.get_attribute("href"))
        
        except:
            break  # No more pages, exit the loop

    driver.quit()  # Close the browser
    
    return job_urls
