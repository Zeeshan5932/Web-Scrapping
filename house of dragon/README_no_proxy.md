# House of Dragon HBO Scraper (No Proxy Version)

This version of the House of Dragon HBO scraper removes the proxy functionality while maintaining all the core data extraction features. This makes the scraper easier to use without needing proxy configurations.

## Changes from the Original Version

1. Removed all proxy-related functionality:
   - Removed proxy loading and rotation
   - Simplified the initialization parameters
   - Streamlined connection retry logic

2. Maintained all core features:
   - Google search for House of Dragon content
   - Multi-tab opening
   - Full data extraction from HBO pages
   - Data saving to JSON format
   - User agent rotation for some anonymity

## Usage

Basic usage:

```python
from main_no_proxy import HBOScraper

# Create scraper instance
scraper = HBOScraper(max_retries=3)

# Run the scraper
scraper.run(query="House of the Dragon HBO", max_tabs=5, output_file="house_of_dragon_data.json")
```

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements_no_proxy.txt
```

## Output Structure

The scraper outputs a JSON file with the same structure as the original version:

```json
{
    "title": "House of the Dragon",
    "data_source": "HBO",
    "scrape_date": "YYYY-MM-DD HH:MM:SS",
    "episodes": [...],
    "characters": [...],
    "news": [...],
    "metadata": {...}
}
```

## When to Use This Version

Use this no-proxy version when:
1. You don't need to hide your IP address
2. You encounter issues with proxy connections
3. You want a simpler, more reliable version without proxy configuration
4. You're scraping a reasonable amount of data that won't trigger rate limits

For extensive scraping that needs IP rotation, consider using the original version with proxy support.
