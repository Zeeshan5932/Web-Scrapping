import json
import time
import os
import random
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from scraper import scrape_instagram, scrape_post_details
from utils import login_instagram, get_random_user_agent
from collections import Counter

# Helper functions for insights generation
def get_top_items(items, limit=10):
    """Get the most common items from a list"""
    counter = Counter(items)
    return [{"item": item, "count": count} for item, count in counter.most_common(limit)]

def get_post_type_distribution(posts):
    """Get distribution of post types"""
    types = [post.get("post_type", "Unknown") for post in posts]
    counter = Counter(types)
    return {post_type: count for post_type, count in counter.items()}

def get_engagement_stats(posts):
    """Calculate engagement statistics from posts"""
    likes = []
    comments = []
    
    for post in posts:
        try:
            # Extract numeric values from likes_count
            likes_str = post.get("likes_count", "0")
            if isinstance(likes_str, str):
                # Remove non-numeric characters
                likes_val = int(''.join(c for c in likes_str if c.isdigit()) or 0)
            else:
                likes_val = int(likes_str)
            likes.append(likes_val)
        except:
            pass
            
        try:
            # Extract numeric values from comments_count
            comments_str = post.get("comments_count", "0")
            if isinstance(comments_str, str):
                # Remove non-numeric characters
                comments_val = int(''.join(c for c in comments_str if c.isdigit()) or 0)
            else:
                comments_val = int(comments_str)
            comments.append(comments_val)
        except:
            pass
    
    return {
        "avg_likes": sum(likes) / len(likes) if likes else 0,
        "avg_comments": sum(comments) / len(comments) if comments else 0,
        "max_likes": max(likes) if likes else 0,
        "max_comments": max(comments) if comments else 0,
        "total_likes": sum(likes),
        "total_comments": sum(comments)
    }

# CSV export function
def export_to_csv(data, file_path):
    """
    Export the scraped data to a CSV file
    
    Args:
        data (list): The scraped data to export
        file_path (str): The file path for the output CSV file
    """
    if not data or len(data) == 0:
        print("No data available to export.")
        return
    
    # Extract keys from the first dictionary as CSV header
    header = data[0].keys()
    
    try:
        with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=header)
            
            writer.writeheader()  # Write the header row
            for row in data:
                writer.writerow(row)  # Write each data row
                
        print(f"Data successfully exported to '{file_path}'")
    except Exception as e:
        print(f"Error exporting data to CSV: {e}")

def save_posts_to_csv(posts, output_path):
    """
    Save posts data to a CSV file for better readability and analysis
    
    Args:
        posts (list): List of post dictionaries with simplified data
        output_path (str): Path to save the CSV file
        
    Returns:
        str: Path to the created CSV file
    """
    try:
        # Define CSV headers based on the structure of our simplified posts
        headers = [
            "Username", 
            "Post URL", 
            "Post Date",
            "Post Type",
            "Likes",
            "Comments", 
            "Location",
            "Caption",
            "Hashtags",
            "Mentions",
            "Followers Count",
            "Posts Count",
            "Verified"
        ]
        
        # Open and write to CSV file
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header row
            writer.writerow(headers)
            
            # Write data for each post
            for post in posts:
                # Get profile data (if available)
                profile = post.get("profile", {})
                followers_count = profile.get("followers_count", "N/A")  
                posts_count = profile.get("posts_count", "N/A")
                verified = "Yes" if profile.get("is_verified", False) else "No"
                
                # Format lists (hashtags and mentions) as comma-separated strings
                hashtags_str = ", ".join(post.get("hashtags", []))
                mentions_str = ", ".join(post.get("mentions", []))
                  # Clean caption - remove line breaks for CSV
                caption = post.get("caption", "").replace("\n", " ").replace("\r", " ")
                if len(caption) > 100:
                    caption = caption[:97] + "..."
                # Escape any CSV special characters
                caption = caption.replace('"', '""')# Write the row
                writer.writerow([
                    post.get("username", ""),
                    post.get("url", ""),
                    post.get("post_date", ""),
                    post.get("post_type", ""),
                    post.get("likes_count", ""),
                    post.get("comments_count", ""),
                    post.get("location", ""),
                    caption,
                    hashtags_str,
                    mentions_str,
                    followers_count,
                    posts_count,
                    verified
                ])
                
        print(f"CSV data successfully saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error saving CSV data: {e}")
        return None

# Setup Selenium Chrome Driver
def setup_driver(headless=False):
    """
    Configure and setup the Chrome WebDriver with anti-detection measures
    
    Args:
        headless: Whether to run Chrome in headless mode (without UI)
    
    Returns:
        WebDriver instance configured for Instagram
    """
    options = Options()
    
    # Get random user agent
    user_agent = get_random_user_agent()
    
    # Add arguments to avoid detection
    if headless:
        options.add_argument("--headless")  # Run in headless mode if requested
    
    # Add anti-detection measures
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Try using webdriver-manager for automatic ChromeDriver management
    try:
        s = Service(ChromeDriverManager().install())
        print("Using ChromeDriverManager for automatic driver installation")
    except Exception as e:
        print(f"Error with ChromeDriverManager: {e}")
        # Fallback to local ChromeDriver
        path = "c:/chromedriver/chromedriver.exe"  # Adjust this path to your chromedriver location
        if not os.path.exists(path):
            print(f"Warning: ChromeDriver not found at {path}")
            print("Please install ChromeDriver or run: pip install webdriver-manager")
        s = Service(path)
    
    # Initialize the driver
    driver = webdriver.Chrome(service=s, options=options)
    
    # Additional anti-detection measures
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Set window size to appear like a standard screen
    driver.set_window_size(1366, 768)
    
    return driver

def main():
    # Step 1: Setup the driver
    # Set headless=False to see the browser while scraping (useful for debugging)
    driver = setup_driver(headless=False)
    
    try:
        # Step 2: Login to Instagram (automatically using credentials from .env)
        login_instagram(driver)
        
        # Add a random delay to look more like human behavior
        time.sleep(random.uniform(1, 3))        # Step 3: Get the search query from the user
        search_query = input("Enter what you want to search (username, hashtag, or topic): ").strip()
        
        # Ask if this is a profile search (to handle usernames better)
        search_type = input("Is this a profile username? (y/n): ").lower()
        is_profile = search_type.startswith('y')
        if not search_query:
            search_query = "travel"  # Default search term if none provided
            print(f"Using default search term: {search_query}")
            is_profile = False
        
        # Process the search query based on type
        if is_profile:
            # Clean up username - remove @, spaces and special characters
            username = search_query.replace('@', '').strip().replace(' ', '')
            print(f"Searching for profile: {username}")
            driver.get(f"https://www.instagram.com/{username}/")
            
            # Check if profile exists or we got redirected
            time.sleep(random.uniform(2, 3))
            not_found_detected = False
            
            # Check for "Page Not Found" indicators
            not_found_indicators = [
                "//h2[contains(text(), 'Sorry, this page')]", 
                "//div[contains(text(), 'Sorry, this page')]",
                "//h2[contains(text(), 'Page Not Found')]"
            ]
            
            for indicator in not_found_indicators:
                try:
                    elements = driver.find_elements(By.XPATH, indicator)
                    if elements:
                        print(f"Profile not found: {username}")
                        not_found_detected = True
                        break
                except:
                    pass
        elif search_query.startswith("#"):
            # Remove the # symbol if the user included it
            hashtag = search_query[1:]
            print(f"Searching for hashtag: #{hashtag}")
            driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
        elif " " not in search_query:
            # If no spaces, likely a username
            print(f"Searching for profile: {search_query}")
            driver.get(f"https://www.instagram.com/{search_query}/")
        else:
            # General search
            print(f"Performing general search for: {search_query}")
            # First navigate to search page
            driver.get("https://www.instagram.com/explore/")
            time.sleep(2)
            
            # Find the search box
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']"))
                )
                search_box.click()
                time.sleep(1)
                search_box.send_keys(search_query)
                time.sleep(2)  # Wait for search results to appear
            except Exception as e:
                print(f"Error using search box: {e}")
                # Fallback to hashtag search
                print("Falling back to hashtag search")
                # Replace spaces with underscores for hashtag format
                hashtag = search_query.replace(" ", "")
                driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
        
        # Wait for the page to load completely
        time.sleep(random.uniform(3, 5))

    # Step 4: Extract URLs of the posts and save them to a JSON file
        urls = scrape_instagram(driver)
          # Step 5: Scrape the details for each URL (with a limit for faster results)
        max_details = min(len(urls), 10)  # Limit to 10 posts for faster results
        print(f"Extracting detailed data from {max_details} out of {len(urls)} posts...")
        
        post_details = []
        for i, url in enumerate(urls[:max_details]):
            print(f"\nScraping details for post {i+1}/{max_details}: {url}")
            post_data = scrape_post_details(driver, url)
            post_details.append(post_data)
            
            # Add a short delay between posts to avoid rate limiting
            if i < max_details - 1:  # No need to wait after the last post
                delay = random.uniform(1.5, 3)
                print(f"Waiting {delay:.1f} seconds before next post...")
                time.sleep(delay)        # Step 6: Save the post details with only important information
        timestamp = time.strftime("%Y%m%d_%H%M%S")
          # Clean up the search query to use as a folder name (remove special characters)
        folder_name = ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in search_query)
        
        # Create unique timestamp-based folder for each scrape session
        base_folder = f"data/{folder_name}/{timestamp}"
        os.makedirs(base_folder, exist_ok=True)  # Create folder structure
        
        # Clean up and simplify post data to keep only important information
        simplified_posts = []
        for post in post_details:
            # Extract only the essential fields
            essential_data = {
                "url": post.get("url", ""),
                "username": post.get("username", "Not found"),
                "timestamp": post.get("timestamp", ""),
                "post_date": post.get("post_date", "Unknown"),
                "caption": post.get("caption", "No caption available"),
                "likes_count": post.get("likes_count", "Not available"),
                "comments_count": post.get("comments_count", "Not available"),
                "post_type": post.get("post_type", "Unknown"),
                "hashtags": post.get("hashtags", []),
                "mentions": post.get("mentions", []),
                "location": post.get("location", "Not specified")
            }
            
            # Add media URLs (only keeping the URLs, not the type info)
            media_urls = []
            for media in post.get("media_urls", []):
                if isinstance(media, dict) and "url" in media:
                    media_urls.append(media["url"])
                elif isinstance(media, str):
                    media_urls.append(media)
            
            essential_data["media_urls"] = media_urls
            
            # Add profile data (only the most important fields)
            if "profile_data" in post and isinstance(post["profile_data"], dict):
                essential_data["profile"] = {
                    "username": post["profile_data"].get("username", "Not found"),
                    "full_name": post["profile_data"].get("full_name", "Not found"),
                    "followers_count": post["profile_data"].get("followers_count", "Not available"),
                    "posts_count": post["profile_data"].get("posts_count", "Not available"),
                    "is_verified": post["profile_data"].get("is_verified", False)
                }
            
            simplified_posts.append(essential_data)
        
        # Create a single comprehensive data file with all important information
        data_file_path = f"{base_folder}/{folder_name}_data_{timestamp}.json"
        with open(data_file_path, "w", encoding="utf-8") as data_file:
            json_output = {
                "scrape_timestamp": timestamp,
                "search_query": search_query,
                "total_posts_found": len(urls),
                "posts_extracted": len(simplified_posts),
                "posts": simplified_posts
            }
            json.dump(json_output, data_file, indent=4, ensure_ascii=False)

        # Export the same data to CSV format
        # csv_file_path = f"{base_folder}/{folder_name}_data_{timestamp}.csv"
        # export_to_csv(simplified_posts, csv_file_path)

        # # Save detailed posts to CSV
        # detailed_csv_path = f"{base_folder}/{folder_name}_detailed_data_{timestamp}.csv"
        # save_posts_to_csv(post_details, detailed_csv_path)

        print(f"\nScraping completed! Important data saved to '{data_file_path}'.")
    except Exception as e:
        print(f"An error occurred during scraping: {str(e)}")
    finally:
        # Keep the browser open for inspection or close based on user input
        input("Press Enter to close the browser and exit...")
        driver.quit()

def run_scraper(search_query=None, max_posts=15, max_details=10, headless=False, retries=3):
    """
    Run the Instagram scraper with customizable parameters
    
    Args:
        search_query (str): What to search for (username, hashtag, or topic)
        max_posts (int): Maximum number of post URLs to collect
        max_details (int): Maximum number of posts to extract details from
        headless (bool): Whether to run Chrome in headless mode
        retries (int): Number of retries for failed operations
        
    Returns:
        str: Path to the saved folder containing scraped data
    """
    driver = None
    try:
        # Setup driver
        driver = setup_driver(headless=headless)
        
        try:
            # Login to Instagram with retry logic
            login_success = False
            login_attempts = 0
            
            while not login_success and login_attempts < retries:
                try:
                    login_instagram(driver)
                    login_success = True
                except Exception as e:
                    login_attempts += 1
                    print(f"Login attempt {login_attempts} failed: {str(e)}")
                    if login_attempts >= retries:
                        raise Exception(f"Failed to login after {retries} attempts")
                    time.sleep(random.uniform(5, 10))  # Wait before retrying
            
            # Use provided search query or ask for input
            if not search_query:
                search_query = input("Enter what you want to search (hashtag, username, or topic): ").strip()
                
            if not search_query:
                search_query = "travel"  # Default
                print(f"Using default search term: {search_query}")
            
            # Ensure starting with a clean slate
            try:
                driver.get("https://www.instagram.com/")
                time.sleep(random.uniform(2, 3))
            except Exception as e:
                print(f"Error navigating to home page: {e}")
                print("Continuing with search...")
            
            # Determine search type and navigate with retry logic
            search_attempts = 0
            search_success = False
            
            while not search_success and search_attempts < retries:
                try:
                    if search_query.startswith("#"):
                        hashtag = search_query[1:]
                        print(f"Searching for hashtag: #{hashtag}")
                        driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
                    elif " " not in search_query:
                        print(f"Searching for profile: {search_query}")
                        driver.get(f"https://www.instagram.com/{search_query}/")
                    else:
                        print(f"Performing general search for: {search_query}")
                        driver.get("https://www.instagram.com/explore/")
                        time.sleep(random.uniform(2, 3))
                        
                        # Find search box
                        try:
                            search_box = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']"))
                            )
                            search_box.click()
                            time.sleep(random.uniform(0.5, 1.5))
                            search_box.send_keys(search_query)
                            time.sleep(random.uniform(2, 3))
                            
                            # Try to click on a search result
                            try:
                                result_selectors = [
                                    "//a[@role='link']",
                                    "//div[@role='none']//a",
                                    "//div[contains(@aria-label, 'Search results')]//a"
                                ]
                                
                                for selector in result_selectors:
                                    try:
                                        results = WebDriverWait(driver, 5).until(
                                            EC.presence_of_all_elements_located((By.XPATH, selector))
                                        )
                                        if results:
                                            results[0].click()
                                            time.sleep(random.uniform(2, 3))
                                            break
                                    except:
                                        continue
                            except Exception as click_err:
                                print(f"Could not click search result: {click_err}")
                                # Continue anyway - we've entered the search term
                                pass
                        except Exception as search_box_err:
                            print(f"Error with search box: {search_box_err}")
                            # Fallback to hashtag search
                            hashtag = search_query.replace(" ", "")
                            driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
                    
                    # Check if the page loaded correctly
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.any_of(
                                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/p/')]")),  # Post links
                                EC.presence_of_element_located((By.XPATH, "//img[@alt='Profile picture']")),  # Profile page
                                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Posts')]"))  # Hashtag page
                            )
                        )
                        search_success = True
                    except:
                        print("Page did not load correctly, retrying...")
                        search_attempts += 1
                        if search_attempts >= retries:
                            raise Exception("Failed to load search results after multiple attempts")
                        time.sleep(random.uniform(5, 10))
                        
                except Exception as e:
                    search_attempts += 1
                    print(f"Search attempt {search_attempts} failed: {e}")
                    if search_attempts >= retries:
                        raise Exception(f"Failed to search after {retries} attempts")
                    time.sleep(random.uniform(5, 10))
            
            # Wait for page to fully load
            time.sleep(random.uniform(3, 5))
            
            # Extract URLs with retry logic
            url_attempts = 0
            urls = []
            
            while len(urls) == 0 and url_attempts < retries:
                try:
                    urls = scrape_instagram(driver, max_posts=max_posts)
                    if len(urls) == 0:
                        url_attempts += 1
                        print(f"No posts found, attempt {url_attempts}/{retries}")
                        if url_attempts >= retries:
                            raise Exception("No posts found after multiple attempts")
                        time.sleep(random.uniform(3, 5))
                except Exception as e:
                    url_attempts += 1
                    print(f"URL scraping attempt {url_attempts} failed: {e}")
                    if url_attempts >= retries:
                        raise Exception(f"Failed to scrape post URLs after {retries} attempts")
                    time.sleep(random.uniform(5, 10))
            
            max_details = min(len(urls), max_details)
            post_details = []
            
            # Extract detailed post information with individual post retry logic
            for i, url in enumerate(urls[:max_details]):
                post_attempts = 0
                success = False
                
                while not success and post_attempts < retries:
                    try:
                        print(f"Scraping post {i+1}/{max_details}: {url} (attempt {post_attempts+1})")
                        post_data = scrape_post_details(driver, url)
                        post_details.append(post_data)
                        success = True
                    except Exception as e:
                        post_attempts += 1
                        print(f"Error scraping post {url}: {e}")
                        if post_attempts >= retries:
                            print(f"Skipping post {url} after {retries} failed attempts")
                            # Add a minimal placeholder with just the URL to maintain consistency
                            post_details.append({"url": url, "error": str(e)})
                        time.sleep(random.uniform(3, 5))
                
                # Add a random delay between posts to avoid rate limiting
                if i < max_details - 1:
                    delay = random.uniform(1.5, 3)
                    print(f"Waiting {delay:.1f} seconds before next post...")
                    time.sleep(delay)              # Save results with simplified data structure
            timestamp = time.strftime("%Y%m%d_%H%M%S")
              # Clean up the search query to use as a folder name (remove special characters)
            folder_name = ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in search_query)
            
            # Create unique timestamp-based folder for each scrape session
            base_folder = f"data/{folder_name}/{timestamp}"
            os.makedirs(base_folder, exist_ok=True)  # Create folder structure
            
            # Clean up and simplify post data to keep only important information
            simplified_posts = []
            for post in post_details:
                # Extract only the essential fields
                essential_data = {
                    "url": post.get("url", ""),
                    "username": post.get("username", "Not found"),
                    "timestamp": post.get("timestamp", ""),
                    "post_date": post.get("post_date", "Unknown"),
                    "caption": post.get("caption", "No caption available"),
                    "likes_count": post.get("likes_count", "Not available"),
                    "comments_count": post.get("comments_count", "Not available"),
                    "post_type": post.get("post_type", "Unknown"),
                    "hashtags": post.get("hashtags", []),
                    "mentions": post.get("mentions", []),
                    "location": post.get("location", "Not specified")
                }
                
                # Add media URLs (only keeping the URLs, not the type info)
                media_urls = []
                for media in post.get("media_urls", []):
                    if isinstance(media, dict) and "url" in media:
                        media_urls.append(media["url"])
                    elif isinstance(media, str):
                        media_urls.append(media)
                
                essential_data["media_urls"] = media_urls
                
                # Add profile data (only the most important fields)
                if "profile_data" in post and isinstance(post["profile_data"], dict):
                    essential_data["profile"] = {
                        "username": post["profile_data"].get("username", "Not found"),
                        "full_name": post["profile_data"].get("full_name", "Not found"),
                        "followers_count": post["profile_data"].get("followers_count", "Not available"),
                        "posts_count": post["profile_data"].get("posts_count", "Not available"),
                        "is_verified": post["profile_data"].get("is_verified", False)
                    }
                
                simplified_posts.append(essential_data)
            
            # Create a single comprehensive data file with all important information
            data_file_path = f"{base_folder}/{folder_name}_data_{timestamp}.json"
            with open(data_file_path, "w", encoding="utf-8") as data_file:
                json_output = {
                    "scrape_timestamp": timestamp,
                    "search_query": search_query,
                    "total_posts_found": len(urls),
                    "posts_extracted": len(simplified_posts),
                    "posts": simplified_posts
                }                
                json.dump(json_output, data_file, indent=4, ensure_ascii=False)
                print(f"Scraping completed! Important data saved to '{data_file_path}'")
                
                # Export data to CSV format for better readability
                csv_path = f"{base_folder}/{folder_name}_data_{timestamp}.csv"
                csv_result = save_posts_to_csv(simplified_posts, csv_path)
                if csv_result:
                    print(f"Data exported to CSV for better analysis: '{csv_path}'")
                
                # Generate a simple insights summary
            try:
                print("\nGenerating insights summary...")
                
                # Create a simple insights summary directly from the data
                insights = {
                    "search_query": search_query,
                    "timestamp": timestamp,
                    "total_posts": len(urls),
                    "analyzed_posts": len(simplified_posts),
                    "top_hashtags": get_top_items([tag for post in simplified_posts for tag in post.get("hashtags", [])], 10),
                    "top_mentions": get_top_items([mention for post in simplified_posts for mention in post.get("mentions", [])], 5),
                    "post_types": get_post_type_distribution(simplified_posts),
                    "engagement_stats": get_engagement_stats(simplified_posts)
                }
                
                # Save the insights
                insights_path = f"{base_folder}/{folder_name}_insights_{timestamp}.json"
                with open(insights_path, "w", encoding="utf-8") as insights_file:
                    json.dump(insights, insights_file, indent=4, ensure_ascii=False)
                    
                print(f"Insights summary saved to '{insights_path}'")
            except Exception as insights_error:
                print(f"Error generating insights: {insights_error}")
                
            return data_file_path
            
        finally:
            # Allow user to see the results before closing
            input("Press Enter to close the browser...")
            driver.quit()
            
    except Exception as e:
        print(f"Error running scraper: {str(e)}")
        return None

if __name__ == "__main__":
    main()
