# House of Dragon HBO Scraper

A class-based web scraper for extracting information about the "House of the Dragon" TV series from HBO websites and other sources.

## Features

- Search for "House of the Dragon" content using Google
- Open multiple search results in separate tabs
- Extract data from HBO website including:
  - Episode information
  - Character details
  - Series metadata
  - News articles
- Proxy rotation to avoid IP blocks
- User agent rotation for enhanced anonymity
- Save extracted data to JSON format

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure you have a text file with proxies (one proxy per line) in the format:
```
ip:port
```

## Usage

Basic usage:

```python
from main import HBOScraper

# Create scraper instance
scraper = HBOScraper(proxy_file="path/to/proxies.txt", use_proxy=True)

# Run the scraper
scraper.run(query="House of the Dragon HBO", max_tabs=5, output_file="house_of_dragon_data.json")
```

## Advanced Usage

You can use individual methods for more fine-grained control:

```python
scraper = HBOScraper(proxy_file="path/to/proxies.txt")
scraper.setup_driver()
scraper.search_google("House of the Dragon season 2")
scraper.open_search_results(max_tabs=3)
scraper.extract_hbo_data()
scraper.save_data_to_json("season2_data.json")
```

## Output Data Structure

The scraper outputs a JSON file with the following structure:

```json
{
    "title": "House of the Dragon",
    "data_source": "HBO",
    "scrape_date": "YYYY-MM-DD HH:MM:SS",
    "episodes": [
        {
            "title": "Episode Title",
            "episode_number": "S01E01",
            "description": "Episode description...",
            "url": "https://...",
            "runtime": "54 min"
        },
        ...
    ],
    "characters": [
        {
            "name": "Character Name",
            "actor": "Actor Name",
            "description": "Character description...",
            "url": "https://..."
        },
        ...
    ],
    "news": [
        {
            "title": "News Article Title",
            "url": "https://...",
            "date": "Publication date",
            "content": "Article content..."
        },
        ...
    ],
    "metadata": {
        "https://...": {
            "title": "Page title",
            "release_date": "2022-08-21",
            ...
        },
        ...
    }
}
```

## License

This project is for educational purposes only. Make sure to comply with HBO's terms of service when using this scraper.
