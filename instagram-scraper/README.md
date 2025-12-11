# Enhanced Instagram Scraper

A flexible and powerful tool for scraping Instagram data including posts, profiles, hashtags, and more.

## Features

- Extract detailed post information:
  - Captions, hashtags, and mentions
  - Like counts, comment counts, and share counts
  - Post dates and locations
  - Media URLs (images, videos, carousels)
  - Tagged users
  - User profile data

- Organized data storage:
  - Creates folder structure based on search queries
  - Separate folder for each search query
  - Individual JSON files for each post
  - Summary JSON file for each search session

- Advanced capabilities:
  - Anti-detection measures
  - Human-like browsing behavior
  - Robust error handling and recovery
  - Batch processing of multiple queries
  - Comprehensive report generation

## Installation

1. Clone the repository or download the source code
2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your Instagram credentials:

```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

## Usage

### Basic Usage

Run the script with Python:

```
python run.py
```

This will prompt you to enter a search query.

### Command Line Arguments

You can also use command line arguments for more control:

```
python run.py -q "travel" -n 30 -d 15
```

Arguments:
- `-q`, `--query`: Search query (hashtag, username, or topic)
- `-n`, `--num-posts`: Maximum number of post URLs to collect (default: 15)
- `-d`, `--details`: Maximum number of posts to extract details from (default: 10)
- `--headless`: Run Chrome in headless mode (no UI)
- `-r`, `--retries`: Number of retries for failed operations (default: 3)
- `--batch`: Path to batch file with multiple queries (one per line)

### Batch Processing

Create a text file with one query per line:

```
travel
#food
natgeo
vacation spots
```

Then run:

```
python run.py --batch queries.txt
```

## Output Structure

The scraped data will be organized in the following structure:

```
data/
  ├── travel/                           # Search query folder
  │   ├── 20250611_134523/             # Timestamp folder
  │   │   ├── summary.json              # Summary of this scrape session
  │   │   ├── all_posts.json            # All posts in a single file
  │   │   ├── post_CWxyz123.json        # Individual post file
  │   │   ├── post_CWabc456.json        # Individual post file
  │   │   └── ...
  │   ├── report_1718134523.html        # HTML report
  │   └── report_1718134523.json        # JSON report data
  │
  ├── food/                            # Another search query
  │   ├── ...
```

## Reports

The scraper automatically generates reports for each search query:

1. **JSON Report**: Contains comprehensive statistics including:
   - Top users, hashtags, and mentions
   - Post type distribution
   - Average engagement metrics
   - Session summaries

2. **HTML Report**: A visual representation of the JSON data with tables and charts.

## Notes

- Instagram frequently updates their website structure, which may break the scraper. Check for updates regularly.
- Using this tool excessively might result in your account being temporarily blocked or rate limited by Instagram.
- Use responsibly and respect Instagram's terms of service and rate limits.
