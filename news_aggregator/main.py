#!/usr/bin/env python3
# filepath: f:\eFaida\news_aggregator\main.py
"""
BBC News Aggregator - Main Script
This script scrapes news articles from BBC News and saves them to a JSON file.
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import time
import random
import re

def get_user_agent():
    """Return a random user agent to avoid being blocked"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    ]
    return random.choice(user_agents)

def extract_image_url(card_element):
    """Extract image URL from a news card element"""
    try:
        # Try to find the image element using various selectors
        img_tag = card_element.select_one("img[srcset]")
        if img_tag and img_tag.has_attr("srcset"):
            # Extract the highest resolution image URL from srcset attribute
            srcset = img_tag["srcset"]
            # Split srcset by comma and get the last entry (highest resolution)
            urls = [url.strip().split()[0] for url in srcset.split(",")]
            if urls:
                return urls[-1]  # Return the highest resolution URL
                
        # Try to get src attribute as fallback
        if img_tag and img_tag.has_attr("src"):
            return img_tag["src"]
    except Exception as e:
        print(f"Error extracting image URL: {e}")
    
    return None

def extract_metadata(card_element):
    """Extract metadata like date and category from a news card element"""
    metadata = {"date": "", "category": ""}
    
    try:
        # Try to extract date
        date_span = card_element.select_one('[data-testid="card-metadata-lastupdated"]')
        if date_span:
            metadata["date"] = date_span.get_text(strip=True)
            
        # Try to extract category
        category_span = card_element.select_one('[data-testid="card-metadata-tag"]')
        if category_span:
            metadata["category"] = category_span.get_text(strip=True)
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        
    return metadata

def extract_articles(soup):
    """Extract all article elements from the soup"""
    articles = []
    
    # Look for all card elements with different layouts
    card_types = [
        '[data-testid="london-card"]',
        '[data-testid="dundee-card"]', 
        '[data-testid="manchester-card"]'
    ]
    
    for selector in card_types:
        card_elements = soup.select(selector)
        
        for card in card_elements:
            try:
                # Extract headline
                headline_element = card.select_one('[data-testid="card-headline"]')
                headline = headline_element.get_text(strip=True) if headline_element else ""
                
                # Extract summary/description
                description = card.select_one('[data-testid="card-description"]')
                summary = description.get_text(strip=True) if description else ""
                
                # Extract link
                link_element = card.select_one('a[href]')
                link = link_element["href"] if link_element and link_element.has_attr("href") else ""
                
                # Make sure link is absolute
                if link and link.startswith("/"):
                    link = "https://www.bbc.com" + link
                
                # Extract image
                image_url = extract_image_url(card)
                
                # Extract metadata
                metadata = extract_metadata(card)
                
                # Only add articles with headlines
                if headline:
                    articles.append({
                        "headline": headline,
                        "summary": summary,
                        "link": link,
                        "image_url": image_url,
                        "date": metadata["date"],
                        "category": metadata["category"],
                        "full_text": ""  # Will be populated later if fetch_full_articles=True
                    })
            except Exception as e:
                print(f"Error processing card: {e}")
    
    return articles

def fetch_article_content(url):
    """Fetch and extract the content of a specific article"""
    try:
        headers = {"User-Agent": get_user_agent()}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"content": "", "error": f"Failed to fetch article: Status code {response.status_code}"}
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Try to find the article container
        article_container = soup.find("article")
        if not article_container:
            # Try alternative selector
            article_container = soup.find(attrs={"role": "main"})
            if not article_container:
                article_container = soup  # Fallback to entire page
        
        # Get all paragraphs in the article
        paragraphs = article_container.find_all("p")
        article_text = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # Extract publication date
        time_element = soup.find("time")
        pub_date = ""
        if time_element and time_element.has_attr("datetime"):
            pub_date = time_element["datetime"]
        
        return {
            "content": article_text,
            "pub_date": pub_date,
            "error": None
        }
    except Exception as e:
        return {"content": "", "error": str(e)}

def fetch_and_save_bbc_news(output_file="all_details.json", fetch_full_articles=False, delay=1):
    """Fetch BBC news, extract articles, and save to JSON file"""
    url = "https://www.bbc.com/news"
    
    try:
        # Set up headers with random user agent
        headers = {"User-Agent": get_user_agent()}
        
        # Fetch the main page
        print(f"Fetching news from {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to fetch news: Status code {response.status_code}")
            return False
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract all articles
        articles = extract_articles(soup)
        
        if not articles:
            print("No articles found.")
            return False
            
        print(f"Found {len(articles)} articles.")
        
        # Optionally fetch full article content
        if fetch_full_articles:
            print("Fetching full article content...")
            for i, article in enumerate(articles):
                if article["link"]:
                    print(f"[{i+1}/{len(articles)}] Fetching: {article['headline']}")
                    result = fetch_article_content(article["link"])
                    
                    if result["error"]:
                        print(f"  Error: {result['error']}")
                    else:
                        article["full_text"] = result["content"]
                        if not article["date"] and result["pub_date"]:
                            article["date"] = result["pub_date"]
                    
                    # Add a delay to be respectful to the server
                    time.sleep(delay)
        
        # Save the data to a JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "source": "BBC News",
                "fetch_date": datetime.now().isoformat(),
                "article_count": len(articles),
                "articles": articles
            }, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully saved {len(articles)} articles to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error fetching BBC news: {e}")
        return False

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Fetch news and save to JSON file
    output_file = "data/all_details.json"
    success = fetch_and_save_bbc_news(
        output_file=output_file,
        fetch_full_articles=True,  # Set to False to speed up execution
        delay=2  # Delay between article requests to be respectful to the server
    )
    
    if success:
        print(f"News data saved to {output_file}")
    else:
        print("Failed to fetch news data.")