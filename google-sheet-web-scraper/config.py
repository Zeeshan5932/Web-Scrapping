# Configuration settings for Google Sheet Web Scraper

import os

# Google Sheets Configuration
GOOGLE_SHEET_CONFIG = {
    'sheet_url': 'https://docs.google.com/spreadsheets/d/1V6M9eBiGa-oxBkZ8u3vm6N11QhKokkH1o4rlJCx3vm0/edit?gid=2057846545#gid=2057846545',
    'credentials_path': 'credentials/credentials.json',
    'scope': [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
}

# Web Scraping Configuration
SCRAPING_CONFIG = {
    'headless': True,
    'window_size': (1920, 1080),
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'timeout': 30,
    'delay_between_requests': 2,
    'max_retries': 3
}

# Chrome Options
CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-blink-features=AutomationControlled',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-images',  # For faster loading
    '--disable-javascript',  # Optional: disable JS if not needed
]

# Output Configuration
OUTPUT_CONFIG = {
    'data_dir': 'data',
    'logs_dir': 'logs',
    'report_filename': 'scraping_report.txt',
    'json_filename_template': 'scraped_data_{timestamp}.json'
}

# Date Patterns for Recognition
DATE_PATTERNS = [
    '%Y-%m-%d',      # 2024-01-15
    '%d-%m-%Y',      # 15-01-2024
    '%m-%d-%Y',      # 01-15-2024
    '%Y/%m/%d',      # 2024/01/15
    '%d/%m/%Y',      # 15/01/2024
    '%m/%d/%Y',      # 01/15/2024
    '%d.%m.%Y',      # 15.01.2024
    '%Y.%m.%d',      # 2024.01.15
    '%B %d, %Y',     # January 15, 2024
    '%d %B %Y',      # 15 January 2024
    '%b %d, %Y',     # Jan 15, 2024
    '%d %b %Y',      # 15 Jan 2024
]

# Website Detection Patterns
WEBSITE_PATTERNS = {
    'url_prefixes': ['http://', 'https://', 'www.'],
    'domain_extensions': ['.com', '.org', '.net', '.edu', '.gov', '.io', '.co', '.uk', '.de', '.fr'],
    'social_media': ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com']
}

# Content Extraction Selectors
CONTENT_SELECTORS = {
    'articles': [
        'article', '.article', '#article',
        '.post', '.blog-post',
        '.news-item', '.news-article',
        '.story', '.content-item'
    ],
    'main_content': [
        'main', '.main', '#main',
        '.content', '#content',
        '.page-content', '.main-content'
    ],
    'headings': ['h1', 'h2', 'h3', '.title', '.headline'],
    'dates': [
        '.date', '.published', '.timestamp',
        '[datetime]', '.post-date', '.article-date'
    ],
    'text_content': [
        'p', '.text', '.description',
        '.summary', '.excerpt'
    ]
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': os.path.join(OUTPUT_CONFIG['logs_dir'], 'scraper.log'),
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# Error Handling
ERROR_CONFIG = {
    'max_retries': 3,
    'retry_delay': 5,
    'timeout_duration': 30,
    'continue_on_error': True
}
