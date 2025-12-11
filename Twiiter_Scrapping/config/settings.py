import os
from dotenv import load_dotenv
import json

load_dotenv()

TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
SCROLL_COUNT = 5
SCROLL_PAUSE_TIME = 2  # Time to wait after each scroll
BASE_URL = "https://twitter.com/"
LOGIN_URL = "https://twitter.com/login"
WAIT_TIMEOUT = 10  # Default wait timeout for elements

SEARCH_URL = "https://twitter.com/search?q={}&src=typed_query&f=user"
MAX_SCROLLS = 10  # Maximum number of scrolls to perform
MAX_PROFILES = 100  # Maximum number of profiles to collect
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
DATA_FILE = os.path.join(DATA_DIR, "profile_urls.json")
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)
DATA_USER_DETAILS = os.path.join(DATA_DIR, "user_details.json")
if not os.path.exists(DATA_USER_DETAILS):
    with open(DATA_USER_DETAILS, 'w') as f:
        json.dump({"users": []}, f)

DATA_TWEETS = os.path.join(DATA_DIR, "tweets.json")
if not os.path.exists(DATA_TWEETS):
    with open(DATA_TWEETS, 'w') as f:
        json.dump({"tweets": []}, f)
#         username_elem = user_cell.find_element(By.CSS_SELECTOR, "[data-testid='UserCell'] a")
#                     if username in [profile["username"] for profile in collected_profiles]:
#                         print(f"Skipping already collected profile: {username}")
#                         continue
#
#                     collected_profiles.append({
#                         "username": username,
#                         "name": name,
#                         "url": href
#                     })
#                     print(f"Collected profile: {username} - {name}")

#     except Exception as e:
#         print(f"Error collecting profiles: {str(e)}")

