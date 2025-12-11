# BBC News Aggregator Documentation

## Project Overview

The BBC News Aggregator is a Python-based web scraping tool designed to automatically collect news articles from the BBC News website. The tool extracts headlines, summaries, content, images, and metadata from news articles and stores them in a structured JSON format for easy access and analysis.

## Key Features

### 1. News Collection Capabilities
- **Multi-Page Scraping**: Extracts articles from BBC News homepage, business section, and other sections
- **Full Content Extraction**: Downloads and processes complete article text
- **Image Collection**: Captures high-resolution images associated with articles
- **Metadata Extraction**: Collects publication dates and category information

### 2. Data Extraction Elements
- Article headlines and titles
- Article summaries and descriptions
- Publication dates and timestamps
- News categories and tags
- Full article content
- Direct links to original articles
- High-resolution images

### 3. Anti-Detection Mechanisms
- Random user agent rotation
- Configurable delays between requests
- Timeout handling and error recovery
- Respectful scraping practices

## How It Works

### Simple Workflow

The News Aggregator follows a straightforward workflow:

1. **Connect to BBC News**: Establishes a connection to the BBC News homepage or specific section (business, sports, etc.)
2. **Extract Article Cards**: Identifies and processes news article elements
3. **Collect Basic Information**: Gathers headlines, summaries, and links
4. **Download Full Content**: Optionally retrieves the complete article text
5. **Process and Clean Data**: Organizes the information into a structured format
6. **Save to JSON**: Stores all collected data in a standardized JSON file

## Data Management

### Data Organization

The BBC News Aggregator saves collected data in a simple, organized way:

- All articles are stored in the `/data` directory
- Data is saved in a single comprehensive JSON file
- Each scraping session creates a new file with the latest articles

### What Information is Stored

Each scrape session captures the following key data fields:

**JSON Data Structure:**
- **headline**: The title of the news article
- **summary**: Brief description or introduction to the article
- **link**: Direct URL to the original BBC article
- **image_url**: URL to the highest resolution image for the article
- **date**: Publication date of the article
- **category**: News category (e.g., Politics, Business, Technology)
- **full_text**: Complete text content of the article (when full articles are fetched)

The data file also includes metadata about the scraping session:
- Source identifier (BBC News)
- Fetch timestamp
- Number of articles collected

## Using the Tool

### Getting Started

The BBC News Aggregator is designed for easy use:

1. Install the required dependencies (primarily requests and BeautifulSoup4)
2. Run the main script using Python
3. Wait for the scraping process to complete
4. Access the collected data in the output JSON file

### Available News Sources

The tool can extract news from different BBC sections:

1. **Main News Page**: Use `main.py` to scrape the BBC News homepage for general news
2. **Business News**: Use `business.py` to scrape the BBC Business section for financial and economic news
3. **Alternative News Scraper**: Use `news.py` for an alternative approach to extract headlines

To add support for additional sections (like Sports, Technology, or Entertainment):
- Create a new script similar to `business.py`
- Update the URL to point to the desired section (e.g., "https://www.bbc.com/sport")
- Test and adjust selectors if necessary for section-specific article layouts

### Usage Options

The tool includes several configuration options:

- **fetch_full_articles**: Toggle whether to download complete article text
- **delay**: Set the waiting time between requests to be respectful to BBC's servers
- **output_file**: Specify where to save the collected data

#### Customizing News Sources

To create a new scraper for additional BBC sections (e.g., Sports):

```python
# Example template for adding a sports news scraper
def fetch_sports_news(output_file="data/sports_details.json", fetch_full_articles=True, delay=1):
    """Fetch BBC sports news, extract articles, and save to JSON file"""
    url = "https://www.bbc.com/sport"
    
    # The rest of the function follows the same pattern as fetch_business_news()
    # ...

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    
    # Call the sports news fetcher
    success = fetch_sports_news(
        output_file="data/sports_details.json",
        fetch_full_articles=True,
        delay=2
    )
```

## Performance and Considerations

### Runtime Expectations
- Quick mode (headlines only): ~10 seconds
- Full content mode: 2-5 minutes depending on article count and server response times

### Limitations
- Only works with the current BBC News website structure
- Subject to changes in BBC's HTML layout
- Currently supports general news and business sections (expandable to other sections)
- Designed for research and personal use, not commercial applications
- Limited to publicly available content

## Best Practices

1. **Be Respectful**: Use reasonable delays between requests
2. **Run Sparingly**: Don't overload BBC's servers with frequent scraping
3. **Personal Use**: Use the collected data for personal research only
4. **Update Regularly**: Check for changes in BBC's website structure

---

*This tool is designed for educational and research purposes. Users are responsible for using the collected data in compliance with BBC's terms of service and applicable copyright laws.*
