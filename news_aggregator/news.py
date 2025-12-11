import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# URL for BBC News homepage
news_url = "https://www.bbc.com/news"

# Fetch and parse the page
response = requests.get(news_url)
news_soup = BeautifulSoup(response.content, "html.parser")

# Try multiple selectors for headlines
headlines = news_soup.find_all("h3", class_="gs-c-promo-heading__title")

# If not found, try anchor tags with class 'gs-c-promo-heading'
if not headlines:
    promo_anchors = news_soup.select("a.gs-c-promo-heading")
    headlines = [a for a in promo_anchors if a.text.strip()]

# If still not found, fallback to all anchor tags with '/news/' in href and non-empty text
if not headlines:
    headlines = [
        a for a in news_soup.find_all("a", href=True)
        if "/news/" in a["href"] and a.text.strip()
    ]

if not headlines:
    print("No headlines found using known selectors.")
else:
    articles_data = []  # List to store all articles data

    for idx, headline in enumerate(headlines, start=1):
        # Get the headline text and link
        headline_text = headline.text.strip()
        link = None
        if headline.name == "a" and headline.has_attr("href"):
            link = headline["href"]
        else:
            parent_a = headline.find_parent("a", href=True)
            if parent_a:
                link = parent_a["href"]
        
        # Make sure the link is absolute
        if link and link.startswith("/"):
            link = "https://www.bbc.com" + link
        
        article_data = {
            "headline": headline_text,
            "link": link,
            "summary": "",  # Placeholder for the summary
            "date": "",  # Placeholder for the date
            "article": "",  # Placeholder for the article content
        }

        if link:
            print(f"{idx}. {headline_text}")
            print(f"   Link: {link}")

            try:
                # Fetch the article page
                article_resp = requests.get(link)
                article_soup = BeautifulSoup(article_resp.content, "html.parser")

                # Try to extract all paragraphs in the article body
                article_tag = article_soup.find("article")
                if not article_tag:
                    article_tag = article_soup.find(attrs={"role": "main"})
                if article_tag:
                    paragraphs = article_tag.find_all("p")
                else:
                    paragraphs = article_soup.find_all("p")
                
                article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                snippet = article_text[:400] + ("..." if len(article_text) > 400 else "")

                article_data["summary"] = snippet

                # Try to extract date and time
                date_str = ""
                time_tag = article_soup.find("time")
                if not time_tag:
                    meta_time = article_soup.find("meta", attrs={"property": "article:published_time"})
                    if meta_time and meta_time.has_attr("content"):
                        date_str = meta_time["content"]
                if not date_str and time_tag and time_tag.has_attr("datetime"):
                    date_str = time_tag["datetime"]
                elif not date_str and time_tag:
                    date_str = time_tag.get_text(strip=True)

                if date_str:
                    try:
                        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        date_str = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
                    except Exception:
                        pass
                
                article_data["date"] = date_str if date_str else "(No date found)"
                article_data["article"] = article_text
            except Exception as e:
                print(f"   Error fetching article: {e}")
                article_data["summary"] = "(Error fetching summary)"
                article_data["date"] = "(No date found)"
                article_data["article"] = "(Error fetching article)"

        # Add this article's data to the list
        articles_data.append(article_data)

    # Save articles data to JSON file
    with open("bbc_articles_data.json", "w", encoding="utf-8") as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=4)

    print(f"All data saved to 'bbc_articles_data.json'.")
