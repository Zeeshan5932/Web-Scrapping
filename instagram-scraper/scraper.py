from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import random
import os

def scrape_instagram(driver, max_posts=15):
    """
    Scrape Instagram posts from search results (hashtag, profile, or general search)
    
    Args:
        driver: Selenium WebDriver instance
        max_posts: Maximum number of posts to scrape (limit for faster results)
        
    Returns:
        list: List of Instagram post URLs
    """
    # Wait for posts to load
    print("Waiting for posts to load...")
    time.sleep(random.uniform(2, 4))

    # Check if we're on a profile page, hashtag page, or search results
    current_url = driver.current_url
    print(f"Currently on: {current_url}")
    
    # Special handling for profile pages - check if user exists
    if "/tags/" not in current_url and "/explore/" not in current_url and "instagram.com/" in current_url:
        try:
            # Check if profile exists or we got redirected to login/error page
            not_found_indicators = [
                "//h2[contains(text(), 'Sorry, this page')]",
                "//div[contains(text(), 'Sorry, this page')]",
                "//h2[contains(text(), 'Page Not Found')]"
            ]
            
            for indicator in not_found_indicators:
                elements = driver.find_elements(By.XPATH, indicator)
                if elements:
                    print(f"⚠️ Profile not found or private: {current_url}")
                    return []  # Return empty list as no posts are available
            
            # Try to find elements indicating a private profile
            private_indicators = [
                "//h2[contains(text(), 'Private')]",
                "//h1[contains(text(), 'Private')]",
                "//div[contains(text(), 'This Account is Private')]"
            ]
            
            for indicator in private_indicators:
                elements = driver.find_elements(By.XPATH, indicator)
                if elements:
                    print(f"⚠️ This account is private: {current_url}")
                    return []  # Return empty list as no posts are available
            
            # If we're here, profile likely exists and is public
            # Extra check - look for username in profile header
            try:
                profile_header = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//header//h2"))
                )
                username = profile_header.text.strip()
                print(f"Found profile: {username}")
            except:
                print("Could not find username in profile header")
            
        except Exception as e:
            print(f"Error checking profile status: {e}")
    
    # Scroll down to load more posts (lazy loading)
    print(f"Scrolling to load up to {max_posts} posts...")
    posts_count = 0
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    # Try to load at least max_posts
    scroll_attempts = 0
    max_scroll_attempts = 5  # Increased for better results with profiles
    
    while posts_count < max_posts and scroll_attempts < max_scroll_attempts:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new posts to load
        time.sleep(random.uniform(1.5, 3.5))
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Get current post count using multiple selectors to ensure we find posts
        posts = []
        post_selectors = [
            '//a[contains(@href, "/p/")]',
            '//article//a[contains(@href, "/p/")]',
            '//div[contains(@role, "presentation")]//a[contains(@href, "/p/")]',
            '//article//div//a[contains(@href, "/p/")]'
        ]
        
        for selector in post_selectors:
            try:
                found_posts = driver.find_elements(By.XPATH, selector)
                if found_posts:
                    posts = found_posts
                    break
            except:
                continue
                
        posts_count = len(posts)
        
        print(f"Found {posts_count} posts so far...")
        
        # Break if no more posts are loading
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
            
        last_height = new_height
      # Try different selectors to find posts based on page type
    urls = []
    
    # Use a more reliable XPath to find post links (works for profiles, hashtags, and search)
    selectors = [
        '//a[contains(@href, "/p/")]',  # Standard post links
        '//article//a[contains(@href, "/p/")]',  # Post links inside article elements
        '//div[@role="presentation"]//a[contains(@href, "/p/")]'  # Another common pattern
    ]
    
    # Try each selector until we find posts
    for selector in selectors:
        try:
            posts = driver.find_elements(By.XPATH, selector)
            if posts:
                print(f"Found {len(posts)} posts using selector: {selector}")
                break
        except Exception as e:
            print(f"Error with selector {selector}: {e}")
    
    # Extract URLs from posts
    for i, post in enumerate(posts[:max_posts]):
        try:
            href = post.get_attribute("href")
            if href and "/p/" in href and href not in urls:
                urls.append(href)
                print(f"Found post URL #{len(urls)}: {href}")
                
                # If we have enough posts, stop
                if len(urls) >= max_posts:
                    break
        except Exception as e:
            print(f"Error extracting URL: {e}")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save URLs to a JSON file with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    url_file_path = f"data/urls_{timestamp}.json"
    with open(url_file_path, "w") as url_file:
        json_data = {
            "search_timestamp": timestamp,
            "search_url": driver.current_url,
            "post_count": len(urls),
            "post_urls": urls
        }
        json.dump(json_data, url_file, indent=4)
    
    print(f"Extracted {len(urls)} unique post URLs and saved to '{url_file_path}'")
    return urls

def scrape_post_details(driver, url):
    """
    Scrape details from an individual Instagram post
    
    Args:
        driver: Selenium WebDriver instance
        url: URL of the Instagram post to scrape
        
    Returns:
        dict: Post details including caption, username, likes, comments, etc.
    """
    # Prepare data structure for post details
    post_data = {
        "url": url,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "username": "Not found",
        "full_name": "Not found",
        "caption": "No caption available",
        "likes_count": "Not available",
        "comments_count": "Not available",
        "shares_count": "Not available",
        "post_date": "Unknown",
        "hashtags": [],
        "mentions": [],
        "tagged_users": [],
        "location": "Not specified",
        "post_type": "Unknown",
        "media_urls": [],
        "comments": [],
        "profile_data": {
            "username": "Not found",
            "full_name": "Not found",
            "profile_pic_url": "Not available",
            "bio": "Not available",
            "followers_count": "Not available",
            "following_count": "Not available",
            "posts_count": "Not available",
            "website_url": "Not available",
            "is_verified": False
        }
    }

    # Open the individual post page
    print(f"Navigating to post: {url}")
    try:
        driver.get(url)
        
        # Wait for post to load
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//time")))
        except:
            print("Warning: Timeout waiting for post elements - proceeding anyway")
            
        # Add a random delay to mimic human browsing behavior
        time.sleep(random.uniform(1.5, 3))
    except Exception as e:
        print(f"Error loading post URL: {e}")
        return post_data  # Return basic data structure with URL if page fails to load    # Extract username and profile data - Updated selector patterns for 2023-2024 Instagram
    try:
        # Try multiple selector patterns
        username_selectors = [
            "//a[@role='link' and contains(@href, '/')]", 
            "//header//a[@role='link']",
            "//div[@role='presentation']//a[@role='link']",
            "//article//header//a"
        ]
        
        for selector in username_selectors:
            try:
                username_element = driver.find_element(By.XPATH, selector)
                username = username_element.text.strip()
                if username and not username.startswith("Like") and len(username) > 0:
                    post_data["username"] = username
                    post_data["profile_data"]["username"] = username
                    print(f"Found username: {username}")
                    
                    # Try to get profile link too
                    profile_url = username_element.get_attribute("href")
                    if profile_url:
                        post_data["profile_url"] = profile_url
                        
                        # Try to get more profile data by visiting profile page
                        try:
                            # Save current URL to return afterward
                            current_url = driver.current_url
                            
                            # Visit profile page
                            print(f"Visiting profile page: {profile_url}")
                            driver.get(profile_url)
                            time.sleep(random.uniform(2, 3))
                            
                            # Extract profile picture
                            try:
                                profile_pic_elements = driver.find_elements(By.XPATH, 
                                    "//header//img[@alt and contains(@alt, 'profile picture')]")
                                if profile_pic_elements:
                                    profile_pic_url = profile_pic_elements[0].get_attribute("src")
                                    post_data["profile_data"]["profile_pic_url"] = profile_pic_url
                            except:
                                pass
                            
                            # Extract bio
                            try:
                                bio_elements = driver.find_elements(By.XPATH, 
                                    "//div[contains(@class, 'biography')]//span | //div[@class='_aa_c']//span")
                                if bio_elements:
                                    post_data["profile_data"]["bio"] = bio_elements[0].text.strip()
                            except:
                                pass
                                  # Extract follower/following counts
                            try:
                                stat_elements = driver.find_elements(By.XPATH, 
                                    "//header//ul//li//span")
                                if len(stat_elements) >= 3:
                                    # Parse posts count
                                    post_data["profile_data"]["posts_count"] = stat_elements[0].text.strip()
                                    
                                    # Parse followers count with proper numeric handling
                                    followers_text = stat_elements[1].text.strip()
                                    post_data["profile_data"]["followers_count"] = followers_text
                                    
                                    # Add numeric version for analytics
                                    try:
                                        # Parse values like "1.2M" or "4.5K" to proper numbers
                                        followers_numeric = followers_text.replace(',', '')
                                        if 'K' in followers_numeric or 'k' in followers_numeric:
                                            followers_numeric = float(followers_numeric.replace('K', '').replace('k', '')) * 1000
                                        elif 'M' in followers_numeric or 'm' in followers_numeric:
                                            followers_numeric = float(followers_numeric.replace('M', '').replace('m', '')) * 1000000
                                        elif 'B' in followers_numeric or 'b' in followers_numeric:
                                            followers_numeric = float(followers_numeric.replace('B', '').replace('b', '')) * 1000000000
                                        else:
                                            followers_numeric = float(''.join(c for c in followers_numeric if c.isdigit() or c == '.'))
                                        
                                        post_data["profile_data"]["followers_numeric"] = int(followers_numeric)
                                    except:
                                        post_data["profile_data"]["followers_numeric"] = 0
                                    
                                    # Parse following count
                                    post_data["profile_data"]["following_count"] = stat_elements[2].text.strip()
                            except:
                                pass
                                
                            # Extract website
                            try:
                                website_elements = driver.find_elements(By.XPATH, 
                                    "//a[contains(@href, 'http') and not(contains(@href, 'instagram.com'))]")
                                if website_elements:
                                    website_url = website_elements[0].get_attribute("href")
                                    post_data["profile_data"]["website_url"] = website_url
                            except:
                                pass
                                
                            # Check if verified
                            try:
                                verified_elements = driver.find_elements(By.XPATH, 
                                    "//span[contains(@aria-label, 'Verified') or contains(@class, 'verified')]")
                                post_data["profile_data"]["is_verified"] = len(verified_elements) > 0
                            except:
                                pass
                                
                            # Return to post page
                            driver.get(current_url)
                            time.sleep(random.uniform(1, 2))
                            
                        except Exception as profile_error:
                            print(f"Error fetching profile data: {profile_error}")
                            # Return to post page
                            driver.get(current_url)
                            
                    break
            except NoSuchElementException:
                continue
    except Exception as e:
        print(f"Error getting username: {e}")# Extract caption
    try:
        # Try multiple caption selector patterns
        caption_selectors = [
            "//div[contains(@class, 'caption')]/span", 
            "//div[@role='button']/span",
            "//div[contains(@class, '_a9zs')]", 
            "//h1[@role='link']/following-sibling::span",
            "//article//span[contains(text(), ' ')]"  # Any span with text in article
        ]
        
        for selector in caption_selectors:
            try:
                caption_element = driver.find_element(By.XPATH, selector)
                caption = caption_element.text.strip()
                if caption and len(caption) > 5:  # Ensure it's not just a short text
                    post_data["caption"] = caption
                    print(f"Found caption: {caption[:50]}...")
                                  # Extract hashtags and mentions from caption
                    hashtags = []
                    mentions = []
                    words = caption.split()
                    for word in words:
                        if word.startswith('#'):
                            hashtag = word.strip('.,!?;:()')
                            if hashtag not in hashtags:
                                hashtags.append(hashtag)
                        elif word.startswith('@'):
                            mention = word.strip('.,!?;:()')
                            if mention not in mentions:
                                mentions.append(mention)
                    
                    if hashtags:
                        post_data["hashtags"] = hashtags
                        print(f"Found {len(hashtags)} hashtags")
                        
                    if mentions:
                        post_data["mentions"] = mentions
                        print(f"Found {len(mentions)} mentions")
                    
                    # Try to find post shares count
                    shares_selectors = [
                        "//span[contains(text(), 'shares')]/parent::div", 
                        "//span[contains(text(), 'shares')]",
                        "//a[contains(text(), 'shares')]/span",
                        "//div[@role='button' and contains(@aria-label, 'shares')]"
                    ]
                    
                    for selector in shares_selectors:
                        try:
                            shares_element = driver.find_element(By.XPATH, selector)
                            shares_text = shares_element.text.strip()
                            if shares_text and any(c.isdigit() for c in shares_text):
                                post_data["shares_count"] = shares_text
                                print(f"Found shares count: {shares_text}")
                                break
                        except NoSuchElementException:
                            continue
                    break
            except NoSuchElementException:
                continue
    except Exception as e:
        print(f"Error getting caption: {e}")
      # Try to extract post date
    try:
        date_selectors = [
            "//time",
            "//time[@datetime]"
        ]
        
        for selector in date_selectors:
            try:
                time_element = driver.find_element(By.XPATH, selector)
                datetime_attr = time_element.get_attribute("datetime")
                if datetime_attr:
                    post_data["post_date"] = datetime_attr
                    print(f"Found post date: {datetime_attr}")
                    break
                else:
                    # If no datetime attribute, try the displayed text
                    time_text = time_element.text
                    if time_text:
                        post_data["post_date"] = time_text
                        print(f"Found post date text: {time_text}")
                        break
            except NoSuchElementException:
                continue
    except Exception as e:
        print(f"Error extracting post date: {e}")
        
    # Try to extract tagged users
    try:
        # First, check if there's a "tagged people" button/link and click it
        tagged_people_selectors = [
            "//span[contains(text(), 'tagged')]/parent::div", 
            "//span[contains(text(), 'tagged')]",
            "//button[contains(text(), 'tagged')]",
            "//a[contains(@href, 'tagged')]"
        ]
        
        tagged_found = False
        for selector in tagged_people_selectors:
            try:
                tagged_button = driver.find_element(By.XPATH, selector)
                if tagged_button:
                    tagged_button.click()
                    time.sleep(1)  # Wait for tagged dialog
                    tagged_found = True
                    print("Clicked on tagged users button")
                    break
            except NoSuchElementException:
                continue
                
        # Now try extracting tagged users (with or without clicking the button)
        tagged_user_selectors = [
            "//div[@role='dialog']//a[@role='link' and contains(@href, '/')]",
            "//div[contains(@aria-label, 'tagged')]//a[@role='link']",
            "//button[contains(text(), 'tagged')]/following::a"
        ]
        
        for selector in tagged_user_selectors:
            try:
                tagged_elements = driver.find_elements(By.XPATH, selector)
                tagged_users = []
                
                for element in tagged_elements:
                    username = element.text.strip()
                    href = element.get_attribute("href")
                    
                    # Make sure it's an actual username (non-empty, not button text, etc.)
                    if username and len(username) > 0 and not username.startswith("Back") and not username.startswith("Close"):
                        if "@" + username not in post_data["mentions"]:  # Avoid duplicating users already in mentions
                            tagged_users.append(username)
                
                if tagged_users:
                    post_data["tagged_users"] = tagged_users
                    print(f"Found {len(tagged_users)} tagged users")
                    break
            except NoSuchElementException:
                continue
                
        # If we opened a dialog with the tagged button, close it
        if tagged_found:
            try:
                close_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Close')]")
                if close_buttons:
                    close_buttons[0].click()
                    time.sleep(0.5)
            except:
                pass
    except Exception as e:
        print(f"Error extracting tagged users: {e}")
        
    # Try to extract location
    try:
        location_selectors = [
            "//a[contains(@href, '/explore/locations/')]",
            "//div[contains(@class, 'location')]//a",
            "//header//div[@role='button']"
        ]
        
        for selector in location_selectors:
            try:
                location_element = driver.find_element(By.XPATH, selector)
                location_text = location_element.text.strip()
                if location_text and len(location_text) > 0 and location_text != post_data["username"]:
                    post_data["location"] = location_text
                    print(f"Found location: {location_text}")
                    
                    # Get the location URL if available
                    location_url = location_element.get_attribute("href")
                    if location_url and "locations" in location_url:
                        post_data["location_url"] = location_url
                    break
            except NoSuchElementException:
                continue
    except Exception as e:
        print(f"Error extracting location: {e}")
        # Try to extract media URLs and determine post type
    try:
        # Check for video elements
        video_selectors = [
            "//video",
            "//video[@src]",
            "//div[@role='button']//video"
        ]
        
        # Check for carousel indicators
        carousel_selectors = [
            "//div[@role='tablist']", 
            "//div[contains(@class, 'carousel')]",
            "//button[contains(@aria-label, 'Next')]"
        ]
        
        # Check for images
        img_selectors = [
            "//article//img[@sizes]",
            "//div[@role='button']//img",
            "//div[@role='dialog']//img"
        ]
        
        # First check if it's a video
        is_video = False
        for selector in video_selectors:
            try:
                video_elements = driver.find_elements(By.XPATH, selector)
                if video_elements:
                    for video in video_elements:
                        src = video.get_attribute("src")
                        poster = video.get_attribute("poster")
                        
                        if src and ("scontent" in src or "instagram" in src or "cdninstagram" in src):
                            post_data["media_urls"].append({"type": "video", "url": src})
                            post_data["post_type"] = "Video"
                            is_video = True
                            print(f"Found video URL")
                        
                        if poster and ("scontent" in poster or "instagram" in poster):
                            post_data["media_urls"].append({"type": "poster", "url": poster})
            except:
                continue
        
        # Then check if it's a carousel
        is_carousel = False
        for selector in carousel_selectors:
            try:
                carousel_elements = driver.find_elements(By.XPATH, selector)
                if carousel_elements:
                    post_data["post_type"] = "Carousel"
                    is_carousel = True
                    print(f"Detected carousel post")
                    break
            except:
                continue
        
        # Finally check for images if not already identified as video
        if not is_video:
            for selector in img_selectors:
                try:
                    image_elements = driver.find_elements(By.XPATH, selector)
                    for img in image_elements:
                        src = img.get_attribute("src")
                        if src and ("scontent" in src or "instagram" in src):
                            if src not in [media["url"] for media in post_data["media_urls"]]:
                                post_data["media_urls"].append({"type": "image", "url": src})
                                if not is_carousel and post_data["post_type"] == "Unknown":
                                    post_data["post_type"] = "Photo"
                                print(f"Found image URL")
                except:
                    continue
        
        # For backward compatibility
        if post_data["media_urls"] and "image_url" not in post_data:
            post_data["image_url"] = post_data["media_urls"][0]["url"]
            
    except Exception as e:
        print(f"Error extracting media URLs: {e}")
              # Try to get engagement metrics and comments
    try:
        # Latest Instagram selectors for like counts
        like_selectors = [
            "//section//span[@class]/span",
            "//section//div[@role='button']/span",
            "//*[contains(text(), 'likes')]/span",
            "//span[contains(text(), 'likes')]",
            "//div[@role='button' and contains(@aria-label, 'like')]",
            "//article//section//div[@role='button']"
        ]
        
        for selector in like_selectors:
            try:
                likes_element = driver.find_element(By.XPATH, selector)
                likes_text = likes_element.text.strip()
                if likes_text and any(c.isdigit() for c in likes_text):
                    post_data["likes_count"] = likes_text
                    print(f"Found likes count: {likes_text}")
                    break
                # Try checking aria-label attribute for likes
                likes_aria = likes_element.get_attribute("aria-label")
                if likes_aria and 'like' in likes_aria.lower() and any(c.isdigit() for c in likes_aria):
                    post_data["likes_count"] = likes_aria
                    print(f"Found likes from aria-label: {likes_aria}")
                    break
            except NoSuchElementException:
                continue
                
        # Try to get comments count
        comment_selectors = [
            "//span[contains(text(), 'comment')]/parent::div",
            "//span[contains(text(), 'comment')]",
            "//a[contains(text(), 'comment')]/span",
            "//div[@role='button' and contains(@aria-label, 'comment')]",
            "//a[@role='link' and contains(@href, '/comments/')]"
        ]
        
        for selector in comment_selectors:
            try:
                comments_element = driver.find_element(By.XPATH, selector)
                comments_text = comments_element.text.strip()
                if comments_text and any(c.isdigit() for c in comments_text):
                    post_data["comments_count"] = comments_text
                    print(f"Found comments count: {comments_text}")
                    break
                # Try checking aria-label attribute for comments
                comments_aria = comments_element.get_attribute("aria-label")
                if comments_aria and 'comment' in comments_aria.lower() and any(c.isdigit() for c in comments_aria):
                    post_data["comments_count"] = comments_aria
                    print(f"Found comments from aria-label: {comments_aria}")
                    break
            except NoSuchElementException:
                continue
                
        # Try to extract actual comments
        try:
            # Click "View all comments" if available
            view_comments_selectors = [
                "//a[contains(text(), 'View all')]",
                "//a[contains(text(), 'comments')]",
                "//span[contains(text(), 'View all')]"
            ]
            
            for selector in view_comments_selectors:
                try:
                    view_comments = driver.find_elements(By.XPATH, selector)
                    if view_comments:
                        view_comments[0].click()
                        print("Clicked 'View all comments'")
                        time.sleep(2)
                        break
                except:
                    continue
            
            # Extract comments
            comment_container_selectors = [
                "//ul[@class]/ul/li",
                "//div[@role='dialog']//ul/li",
                "//div[contains(@aria-label, 'comments')]//ul/li"
            ]
            
            for container_selector in comment_container_selectors:
                comment_elements = driver.find_elements(By.XPATH, container_selector)
                if comment_elements:
                    # Extract up to 10 most recent comments
                    max_comments = min(10, len(comment_elements))
                    comments_data = []
                    
                    for i, comment_el in enumerate(comment_elements[:max_comments]):
                        try:
                            comment_text = comment_el.text.strip()
                            if comment_text and len(comment_text) > 0:
                                # Split username and comment text
                                parts = comment_text.split("\n")
                                if len(parts) >= 2:
                                    username = parts[0]
                                    comment = parts[1]
                                    
                                    # Check for verification badge
                                    is_verified = False
                                    try:
                                        verified_spans = comment_el.find_elements(By.XPATH, ".//span[contains(@aria-label, 'Verified')]")
                                        is_verified = len(verified_spans) > 0
                                    except:
                                        pass
                                    
                                    # Check for like count on comment
                                    like_count = "0"
                                    try:
                                        like_spans = comment_el.find_elements(By.XPATH, ".//div[@role='button']/span")
                                        if like_spans:
                                            like_text = like_spans[0].text.strip()
                                            if like_text and like_text.isdigit():
                                                like_count = like_text
                                    except:
                                        pass
                                    
                                    comment_data = {
                                        "username": username,
                                        "text": comment,
                                        "is_verified": is_verified,
                                        "likes": like_count
                                    }
                                    
                                    comments_data.append(comment_data)
                        except Exception as ce:
                            print(f"Error extracting comment: {ce}")
                    
                    # Add comments to post data
                    if comments_data:
                        post_data["comments"] = comments_data
                        print(f"Extracted {len(comments_data)} comments")
                    break
        except Exception as comment_err:
            print(f"Error extracting comments: {comment_err}")
    except Exception as e:
        print(f"Error getting engagement metrics: {e}")

    # Print summary of what we found
    print(f"Extracted data for post {url}:")
    print(f"- Username: {post_data['username']}")
    print(f"- Caption: {post_data['caption'][:50]}..." if len(post_data['caption']) > 50 else f"- Caption: {post_data['caption']}")
    print(f"- Hashtags: {len(post_data['hashtags'])} found")
    
    return post_data
