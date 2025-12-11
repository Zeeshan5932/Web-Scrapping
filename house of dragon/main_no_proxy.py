from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import os
import random
import json
from datetime import datetime
try:
    from webdriver_manager.chrome import ChromeDriverManager
    webdriver_manager_available = True
except ImportError:
    webdriver_manager_available = False
try:
    from fake_useragent import UserAgent
    fake_ua_available = True
except ImportError:
    fake_ua_available = False


class HBOScraper:
    """
    A class for scraping House of the Dragon information from HBO's website.
    Uses user agent spoofing to avoid detection.
    """
    
    def __init__(self, max_retries=3):
        """
        Initialize the scraper with WebDriver settings
        
        Args:
            max_retries (int): Maximum number of retry attempts
        """
        self.max_retries = max_retries
        self.driver = None
        self.search_results = []
        self.hbo_data = {
            'title': 'House of the Dragon',
            'data_source': 'HBO',
            'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'episodes': [],
            'characters': [],
            'news': [],
            'metadata': {}
        }
        
        # User agents list for rotation
        if fake_ua_available:
            ua = UserAgent()
            self.user_agents = [ua.chrome, ua.firefox, ua.safari, ua.edge]
        else:
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ]
    
    def setup_driver(self):
        """Setup and configure Chrome WebDriver with user agent rotation"""
        chrome_options = webdriver.ChromeOptions()
        
        # Add random user agent
        user_agent = random.choice(self.user_agents)
        chrome_options.add_argument(f'user-agent={user_agent}')
        print(f"Using user-agent: {user_agent[:50]}...")
        
        # Add additional options to avoid detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Setup ChromeDriver service
        if webdriver_manager_available:
            s = Service(ChromeDriverManager().install())
            print("Using ChromeDriverManager for automatic driver installation")
        else:
            # Fallback to local ChromeDriver
            path = "c:\\chromedriver\\chromedriver.exe"  # Use double backslashes
            if not os.path.exists(path):
                print(f"Warning: ChromeDriver not found at {path}")
                print("Please install ChromeDriver or run: pip install webdriver-manager")
            s = Service(path)
        
        # Initialize Chrome driver
        self.driver = webdriver.Chrome(service=s, options=chrome_options)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    def search_google(self, query="House of the Dragon"):
        """
        Search Google for the given query with retry logic
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of search result elements
        """
        retries = 0
        self.search_results = []
        
        while retries < self.max_retries:
            try:
                # Navigate to Google
                self.driver.get("https://www.google.com/")
                
                # Accept cookies if shown
                try:
                    WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[.='Accept all']"))
                    ).click()
                except (TimeoutException, NoSuchElementException):
                    pass  # Button might not appear
                
                # Locate and use search box
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//textarea[@name='q']"))
                )
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.ENTER)
                
                # Wait for results and capture relevant links
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "search")))
                search_results = self.driver.find_elements(By.XPATH, 
                    "//a[contains(@href, 'house-of-the-dragon') or contains(@href, 'houseofthedragon') or contains(text(), 'House of the Dragon')]"
                )
                
                if search_results:
                    print(f"Search successful")
                    self.search_results = search_results
                    break
                else:
                    print("No search results found, trying again...")
                    retries += 1
            
            except Exception as e:
                print(f"Error during search: {e}")
                retries += 1
                
                if retries == self.max_retries:
                    print("Maximum retries reached. Continuing with current results.")
        
        return self.search_results
    
    def open_search_results(self, max_tabs=10):
        """
        Open search results in new tabs
        
        Args:
            max_tabs (int): Maximum number of tabs to open
            
        Returns:
            list: List of opened URLs
        """
        opened_urls = []
        
        # Open each result in a new tab
        for i, result in enumerate(self.search_results[:max_tabs]):
            try:
                # Get the href attribute
                link = result.get_attribute('href')
                if link and 'google' not in link.lower():  # Skip Google's internal navigation links
                    print(f"Opening: {link}")
                    # Open link in new tab using JavaScript
                    self.driver.execute_script(f"window.open('{link}', '_blank');")
                    opened_urls.append(link)
            except Exception as e:
                print(f"Error opening link: {str(e)}")
        
        # Switch back to the first tab
        if self.driver.window_handles:
            self.driver.switch_to.window(self.driver.window_handles[0])
        
        # Print summary of opened tabs
        print("\n" + "-" * 40)
        print(f"Summary: Opened {len(opened_urls)} tabs related to 'House of the Dragon'")
        print("Tab List:")
        for i, handle in enumerate(self.driver.window_handles):
            if i > 0:  # Skip the first tab (Google search results)
                self.driver.switch_to.window(handle)
                print(f"  {i}. {self.driver.title[:50]}... - {self.driver.current_url}")
        
        # Switch back to first tab
        if self.driver.window_handles:
            self.driver.switch_to.window(self.driver.window_handles[0])
        print("-" * 40)
        
        return opened_urls

    def extract_hbo_data(self):
        """
        Extract House of the Dragon data from HBO website
        Looks for tabs with HBO content and extracts episode info, characters, etc.
        """
        hbo_tabs = []
        
        # Look for HBO tabs
        for i, handle in enumerate(self.driver.window_handles):
            try:
                self.driver.switch_to.window(handle)
                
                # Check if this is an HBO website
                if 'hbo' in self.driver.current_url.lower():
                    print(f"Found HBO tab: {self.driver.title}")
                    hbo_tabs.append(handle)
                    
                    # Extract basic metadata
                    self.extract_metadata()
                    
                    # Try to detect what kind of page this is and extract accordingly
                    if '/series/' in self.driver.current_url:
                        self.extract_series_info()
                    elif '/episodes/' in self.driver.current_url or '/episode-' in self.driver.current_url:
                        self.extract_episode_info()
                    elif '/character' in self.driver.current_url:
                        self.extract_character_info()
                    else:
                        # Generic extraction for other HBO pages
                        self.extract_general_content()
            except Exception as e:
                print(f"Error extracting data from tab {i}: {str(e)}")
        
        # If no HBO tabs were found, try to extract general info from all tabs
        if not hbo_tabs:
            print("No HBO tabs found, extracting general information from all tabs")
            for i, handle in enumerate(self.driver.window_handles):
                if i > 0:  # Skip Google search results tab
                    try:
                        self.driver.switch_to.window(handle)
                        self.extract_general_content()
                    except Exception as e:
                        print(f"Error extracting general data from tab {i}: {str(e)}")
        
        # Return to the first tab
        if self.driver.window_handles:
            self.driver.switch_to.window(self.driver.window_handles[0])
        
        return self.hbo_data
    
    def extract_metadata(self):
        """Extract basic metadata from current page"""
        try:
            # Extract page title and add to metadata
            if 'metadata' not in self.hbo_data:
                self.hbo_data['metadata'] = {}
            
            # Add URL and title to metadata
            url = self.driver.current_url
            title = self.driver.title
            
            self.hbo_data['metadata'][url] = {
                'title': title,
                'url': url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # Try to extract release date if available
            try:
                release_elements = self.driver.find_elements(By.XPATH, 
                    "//*[contains(text(), 'Release Date') or contains(text(), 'Air Date') or contains(text(), 'Premiere Date')]/following-sibling::*")
                if release_elements:
                    self.hbo_data['metadata'][url]['release_date'] = release_elements[0].text.strip()
            except:
                pass
                
            # Try to extract rating if available
            try:
                rating_elements = self.driver.find_elements(By.XPATH, 
                    "//*[contains(text(), 'Rating') or contains(text(), 'Rated')]/following-sibling::*")
                if rating_elements:
                    self.hbo_data['metadata'][url]['rating'] = rating_elements[0].text.strip()
            except:
                pass
                
            print(f"Extracted metadata from: {title}")
        except Exception as e:
            print(f"Error extracting metadata: {str(e)}")
    
    def extract_series_info(self):
        """Extract series information from HBO series page"""
        try:
            # Extract series description
            description_elements = self.driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'description') or contains(@class, 'synopsis') or contains(@class, 'summary')]")
            
            if description_elements:
                self.hbo_data['description'] = description_elements[0].text.strip()
                print(f"Extracted series description: {self.hbo_data['description'][:50]}...")
            
            # Extract season information
            season_elements = self.driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'season') or contains(@data-testid, 'season')]")
            
            if not self.hbo_data.get('seasons'):
                self.hbo_data['seasons'] = []
                
            for element in season_elements:
                try:
                    season_number = element.get_attribute('data-season') or "Unknown"
                    season_name = element.text.strip()
                    
                    self.hbo_data['seasons'].append({
                        'season_number': season_number,
                        'season_name': season_name,
                        'url': self.driver.current_url
                    })
                    print(f"Extracted season info: Season {season_number}")
                except:
                    pass
        
        except Exception as e:
            print(f"Error extracting series info: {str(e)}")
    
    def extract_episode_info(self):
        """Extract episode information from episode page"""
        try:
            # Look for episode number and title
            episode_title_elements = self.driver.find_elements(By.XPATH, 
                "//h1[contains(@class, 'title') or contains(@class, 'episode-title')]")
            
            episode_data = {
                'url': self.driver.current_url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if episode_title_elements:
                episode_data['title'] = episode_title_elements[0].text.strip()
            
            # Extract episode number
            episode_number_elements = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Episode') or contains(text(), 'Ep.')]/following-sibling::*")
            
            if episode_number_elements:
                episode_data['episode_number'] = episode_number_elements[0].text.strip()
            
            # Extract episode description
            description_elements = self.driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'description') or contains(@class, 'synopsis')]")
            
            if description_elements:
                episode_data['description'] = description_elements[0].text.strip()
            
            # Extract runtime if available
            runtime_elements = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Runtime') or contains(text(), 'Duration')]/following-sibling::*")
            
            if runtime_elements:
                episode_data['runtime'] = runtime_elements[0].text.strip()
            
            # Add episode data to episodes list
            self.hbo_data['episodes'].append(episode_data)
            print(f"Extracted episode info: {episode_data.get('title', 'Unknown episode')}")
            
        except Exception as e:
            print(f"Error extracting episode info: {str(e)}")
    
    def extract_character_info(self):
        """Extract character information from character page"""
        try:
            # Look for character name and actor
            character_name_elements = self.driver.find_elements(By.XPATH, 
                "//h1[contains(@class, 'character-name') or contains(@class, 'name')]")
            
            character_data = {
                'url': self.driver.current_url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if character_name_elements:
                character_data['name'] = character_name_elements[0].text.strip()
            
            # Extract actor name
            actor_elements = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Played by') or contains(text(), 'Actor')]/following-sibling::*")
            
            if actor_elements:
                character_data['actor'] = actor_elements[0].text.strip()
            
            # Extract character description
            description_elements = self.driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'description') or contains(@class, 'bio')]")
            
            if description_elements:
                character_data['description'] = description_elements[0].text.strip()
            
            # Add character data to character list
            self.hbo_data['characters'].append(character_data)
            print(f"Extracted character info: {character_data.get('name', 'Unknown character')}")
            
        except Exception as e:
            print(f"Error extracting character info: {str(e)}")
    
    def extract_general_content(self):
        """Extract general content from any page related to House of the Dragon"""
        try:
            url = self.driver.current_url
            title = self.driver.title
            
            # Add to news collection if it looks like a news or article page
            is_article = False
            
            # Check for article indicators
            article_elements = self.driver.find_elements(By.XPATH, "//article")
            date_elements = self.driver.find_elements(By.XPATH, 
                "//*[contains(@class, 'date') or contains(@class, 'time') or contains(@class, 'published')]")
            
            if article_elements or date_elements or 'news' in url.lower() or 'blog' in url.lower():
                is_article = True
            
            if is_article:
                # This looks like a news article
                article_data = {
                    'title': title,
                    'url': url,
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Try to extract article date
                if date_elements:
                    article_data['date'] = date_elements[0].text.strip()
                
                # Try to extract article content
                content_elements = self.driver.find_elements(By.XPATH, 
                    "//article//p | //div[contains(@class, 'article-content')]//p")
                
                if content_elements:
                    content_text = "\n".join([p.text for p in content_elements[:10]]).strip()  # Get first 10 paragraphs
                    article_data['content'] = content_text
                
                self.hbo_data['news'].append(article_data)
                print(f"Extracted news article: {title}")
            else:
                # Extract any header or paragraph content related to House of the Dragon
                headers = self.driver.find_elements(By.XPATH, "//h1 | //h2 | //h3")
                paragraphs = self.driver.find_elements(By.XPATH, "//p")
                
                content = []
                if headers:
                    content.extend([h.text for h in headers[:5]])
                if paragraphs:
                    content.extend([p.text for p in paragraphs[:10]])
                
                # Add this general content to metadata
                if content and ('house' in title.lower() or 'dragon' in title.lower()):
                    if 'general_content' not in self.hbo_data:
                        self.hbo_data['general_content'] = []
                    
                    self.hbo_data['general_content'].append({
                        'title': title,
                        'url': url,
                        'content': "\n".join(content).strip(),
                        'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    print(f"Extracted general content from: {title}")
        
        except Exception as e:
            print(f"Error extracting general content: {str(e)}")
    
    def save_data_to_json(self, output_file="house_of_dragon_data.json"):
        """
        Save scraped data to JSON file
        
        Args:
            output_file (str): Path to output JSON file
        """
        try:
            # Add timestamp to data
            self.hbo_data['scrape_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save data to JSON file with nice formatting
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.hbo_data, f, indent=4, ensure_ascii=False)
            
            print(f"Data saved to {output_file}")
            return output_file
        except Exception as e:
            print(f"Error saving data to JSON: {str(e)}")
            return None
    
    def run(self, query="House of the Dragon", max_tabs=10, output_file="house_of_dragon_data.json"):
        """
        Run the complete scraping process
        
        Args:
            query (str): Search query
            max_tabs (int): Maximum tabs to open
            output_file (str): Path to output JSON file
            
        Returns:
            dict: Scraped data
        """
        try:
            # Setup driver if not already done
            if not self.driver:
                self.setup_driver()
            
            # Search Google for content
            print(f"Searching Google for: {query}")
            search_results = self.search_google(query)
            print(f"Found {len(search_results)} relevant search results")
            
            # Open results in new tabs
            opened_urls = self.open_search_results(max_tabs=max_tabs)
            print(f"Opened {len(opened_urls)} URLs in separate tabs")
            
            # Extract HBO data from tabs
            print("Extracting data from tabs...")
            self.extract_hbo_data()
            
            # Save data to JSON
            self.save_data_to_json(output_file)
            
            print("\nScraping process completed successfully!")
            return self.hbo_data
            
        except Exception as e:
            print(f"Error during scraping process: {str(e)}")
            return None
        finally:
            # Keep the browser open until user decides to close it
            print("\nAll search results have been processed.")
            print("Press Ctrl+C in this terminal window to close the browser and exit the script.")
            try:
                while True:
                    time.sleep(1)  # Keep script running
            except KeyboardInterrupt:
                print("\nExiting script and closing browser...")
                if self.driver:
                    self.driver.quit()


# Main execution
if __name__ == "__main__":
    # Create scraper instance
    scraper = HBOScraper(max_retries=3)
    
    # Run scraper
    scraper.run(query="House of the Dragon HBO Max", max_tabs=10, output_file="house_of_dragon_data.json")
