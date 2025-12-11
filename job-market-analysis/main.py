from login import handle_login
from scraper import extract_job_urls
from recommendation import recommend_jobs

def main():
    # Step 1: Handle login (if required)
    username = input("Enter your Glassdoor username: ")
    password = input("Enter your Glassdoor password: ")
    driver = handle_login(username, password)
    
    # Step 2: Get user input (job title and location)
    job_title = input("Enter the job title you're looking for: ")
    location = input("Enter your location: ")
    
    # Step 3: Extract job URLs based on the job title and location
    job_urls = extract_job_urls(job_title, location)
    
    # Step 4: Recommend jobs based on extracted URLs
    recommend_jobs(job_urls)

if __name__ == "__main__":
    main()
