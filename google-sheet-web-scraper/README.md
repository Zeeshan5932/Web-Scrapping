# Google Sheet Web Scraper & Combined Report Generator

A Python application that extracts dates from Google Sheets, finds matching website names, and scrapes data from those websites for the corresponding dates using Selenium and BeautifulSoup. Also includes a Combined Report Generator that processes multiple data sheets and creates consolidated reports.

## Features

- **Google Sheets Integration**: Connects to Google Sheets using the API
- **Date Extraction**: Automatically extracts dates from all sheets/tabs
- **Website Detection**: Identifies website URLs in the spreadsheet
- **Date-Website Matching**: Matches dates with websites for targeted scraping
- **Web Scraping**: Uses Selenium WebDriver and BeautifulSoup for robust scraping
- **Data Processing**: Saves results in JSON format with detailed reports
- **Combined Report Generation**: Processes multiple data sheets and creates consolidated reports
- **Batch Processing**: Supports both direct and batch processing modes

## Setup

### 1. Install Dependencies

For main scraper:
```bash
pip install -r requirements.txt
```

For batch report generator (gspread version):
```bash
pip install -r requirements_batch.txt
```

### 2. Google Sheets API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API
4. Create a service account and download the JSON credentials file
5. Place the credentials file in the `credentials/` folder as `service_account.json`
6. Share your Google Sheet with the service account email address

### 3. WebDriver Setup

The script uses Chrome WebDriver. Make sure you have:
- Chrome browser installed
- ChromeDriver in PATH, or use webdriver-manager (included in requirements)

## Configuration

Edit the `config` dictionary in `main.py`:

```python
config = {
    'google_sheet_url': 'YOUR_GOOGLE_SHEET_URL_HERE',
    'credentials_path': 'credentials/service_account.json',
    'headless': True,  # Set to False to see browser window
    'output_dir': 'data'
}
```

For the batch report generator, edit `batch_report_generator.py`:

```python
SHEET_NAME = "Your Google Sheet Name"
# Update the credentials path in authenticate_google_sheets() function
```

## Usage

### Combined Report Generator

#### Option 1: Using Utilities Interface
```bash
python report_utilities.py
```

This provides a menu with options to:
1. Check Status
2. Preview Data
3. Start Generation (Google Sheets API)
4. Start Batch Generation (gspread)
5. Exit

#### Option 2: Direct Execution
```bash
# Using Google Sheets API (main version)
python run_report_generator.bat

# Using gspread (batch version)
python run_batch_generator.bat
```

#### Option 3: Python Scripts
```bash
# Main combined report generator
python combined_report_generator.py

# Batch report generator (gspread version)
python batch_report_generator.py
```

### Web Scraper (Original)

#### Basic Usage

```bash
python main.py
```

#### Advanced Usage

You can also use the classes individually:

```python
from main import GoogleSheetExtractor, WebScraper, DataProcessor

# Extract data from Google Sheets
extractor = GoogleSheetExtractor('credentials/service_account.json')
sheet = extractor.open_sheet('your_sheet_url')

# Get dates and websites
dates = extractor.extract_dates_from_sheet(sheet.sheet1)
websites = extractor.extract_website_names(sheet.sheet1)

# Scrape websites
scraper = WebScraper(headless=True)
for website in websites:
    for date in dates:
        data = scraper.scrape_website_data(website, date)
        print(data)

scraper.close()
```

## Project Structure

```
google-sheet-web-scraper/
│
├── main.py                     # Main web scraper application
├── combined_report_generator.py # Combined report generator (Google Sheets API)
├── batch_report_generator.py   # Batch report generator (gspread)
├── report_utilities.py         # Utility interface for report generation
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies (main)
├── requirements_batch.txt     # Python dependencies (batch generator)
├── README.md                  # This file
│
├── run_report_generator.bat   # Batch file for main report generator
├── run_batch_generator.bat    # Batch file for batch report generator
│
├── credentials/               # Google API credentials
│   └── service_account.json
│
├── data/                      # Output data
│   ├── scraped_data_*.json
│   ├── scraping_report.txt
│   └── combined_report_*.json
│
├── logs/                      # Log files
│   └── scraper.log
│
└── utils/                 # Utility modules
    ├── __init__.py
    ├── date_parser.py
    ├── website_detector.py
    └── data_cleaner.py
```

## Report Generators

This project includes two different report generators:

### 1. Combined Report Generator (combined_report_generator.py)
- **Library**: Uses Google Sheets API directly via `googleapiclient`
- **Processing**: Processes all data in one go (direct mode)
- **Features**: 
  - Comprehensive error handling
  - Data validation
  - Structured logging
  - Integration with config.py
- **Best for**: Production environments with stable connections

### 2. Batch Report Generator (batch_report_generator.py)
- **Library**: Uses `gspread` with `oauth2client`
- **Processing**: Batch processing with pause/resume capability
- **Features**:
  - Batch size control (500 records default)
  - Pause/resume functionality
  - Direct Google Sheet manipulation
  - Simpler authentication setup
- **Best for**: Large datasets or unstable connections

### Key Differences

| Feature | Combined Report | Batch Report |
|---------|----------------|--------------|
| Library | googleapiclient | gspread |
| Authentication | Service Account JSON | Service Account JSON |
| Processing Mode | All-at-once | Batch with pause/resume |
| Configuration | config.py | Direct in script |
| Error Handling | Comprehensive | Basic |
| Resume Support | No | Yes |
| Memory Usage | Higher | Lower |

## How It Works

1. **Authentication**: Connects to Google Sheets using service account credentials
2. **Sheet Processing**: Iterates through all worksheets/tabs in the spreadsheet
3. **Date Extraction**: Scans all cells for date patterns (various formats supported)
4. **Website Detection**: Identifies URLs and website names in the spreadsheet
5. **Matching**: Creates combinations of dates and websites for scraping
6. **Web Scraping**: 
   - Uses Selenium to navigate to websites
   - Searches for content related to the target date
   - Extracts relevant data using BeautifulSoup
7. **Data Storage**: Saves results in JSON format with comprehensive metadata

## Supported Date Formats

- YYYY-MM-DD (2024-01-15)
- DD-MM-YYYY (15-01-2024)
- MM-DD-YYYY (01-15-2024)
- YYYY/MM/DD (2024/01/15)
- DD/MM/YYYY (15/01/2024)
- MM/DD/YYYY (01/15/2024)
- DD.MM.YYYY (15.01.2024)

## Website Detection

The script automatically detects:
- URLs starting with http/https
- URLs starting with www.
- Domains with common TLDs (.com, .org, .net, .io, etc.)

## Output Format

### JSON Data Structure

```json
{
  "website": "https://example.com",
  "target_date": "2024-01-15",
  "scraped_at": "2024-01-15T10:30:00",
  "title": "Page Title",
  "content": {
    "articles": [...],
    "news": [...],
    "events": [...],
    "general_content": [...]
  },
  "metadata": {
    "description": "Page description",
    "keywords": "page keywords",
    "main_heading": "Main H1 heading"
  }
}
```

### Report

A text report is generated showing:
- Total websites scraped
- Success/failure counts
- Detailed error information
- Summary of extracted content

## Error Handling

- Comprehensive logging to `logs/scraper.log`
- Graceful handling of network errors
- Timeout protection for slow websites
- Detailed error reporting in output data

## Customization

### Adding Custom Date Patterns

Edit the `_is_date()` method in the `GoogleSheetExtractor` class:

```python
def _is_date(self, value: str) -> bool:
    date_patterns = [
        '%Y-%m-%d', '%d-%m-%Y',
        # Add your custom patterns here
        '%B %d, %Y',  # January 15, 2024
    ]
```

### Custom Content Extraction

Modify the `_extract_content_by_date()` method to target specific elements:

```python
def _extract_content_by_date(self, soup: BeautifulSoup, target_date: str):
    # Add custom selectors for your target websites
    custom_selectors = [
        '.your-custom-class',
        '#specific-id',
        'div[data-date]'
    ]
```

## Troubleshooting

### Common Issues

1. **Google Sheets Authentication Error**
   - Verify credentials file path
   - Check if service account email has access to the sheet
   - Ensure APIs are enabled in Google Cloud Console

2. **WebDriver Issues**
   - Install/update Chrome browser
   - Check ChromeDriver compatibility
   - Try running with `headless=False` for debugging

3. **Scraping Failures**
   - Check website accessibility
   - Verify date formats in the content
   - Adjust timeout settings for slow websites

### Debug Mode

Run with debug logging:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes. Always respect website terms of service and robots.txt files. Use appropriate delays between requests to avoid overwhelming servers.
