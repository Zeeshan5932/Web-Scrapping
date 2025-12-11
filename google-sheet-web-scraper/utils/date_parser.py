"""
Date parsing utilities for Google Sheet Web Scraper
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import logging
from config import DATE_PATTERNS

logger = logging.getLogger(__name__)


class DateParser:
    """Utility class for parsing and handling dates"""
    
    def __init__(self, date_patterns: List[str] = None):
        """Initialize with custom date patterns if provided"""
        self.date_patterns = date_patterns or DATE_PATTERNS
    
    def parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse a date string into a datetime object"""
        if not date_string or not isinstance(date_string, str):
            return None
        
        # Clean the string
        cleaned_date = self._clean_date_string(date_string)
        
        # Try each pattern
        for pattern in self.date_patterns:
            try:
                parsed_date = datetime.strptime(cleaned_date, pattern)
                logger.debug(f"Successfully parsed '{date_string}' using pattern '{pattern}'")
                return parsed_date
            except ValueError:
                continue
        
        # Try fuzzy parsing for common formats
        fuzzy_date = self._fuzzy_date_parse(cleaned_date)
        if fuzzy_date:
            return fuzzy_date
        
        logger.warning(f"Could not parse date: '{date_string}'")
        return None
    
    def is_valid_date(self, date_string: str) -> bool:
        """Check if a string contains a valid date"""
        return self.parse_date(date_string) is not None
    
    def extract_dates_from_text(self, text: str) -> List[Tuple[str, datetime]]:
        """Extract all dates from a text string"""
        dates = []
        
        # Common date regex patterns
        date_regexes = [
            r'\b\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}\b',  # YYYY-MM-DD variants
            r'\b\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4}\b',   # DD-MM-YYYY variants
            r'\b\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2}\b',   # DD-MM-YY variants
            r'\b\w+ \d{1,2},? \d{4}\b',               # Month DD, YYYY
            r'\b\d{1,2} \w+ \d{4}\b',                 # DD Month YYYY
        ]
        
        for regex in date_regexes:
            matches = re.finditer(regex, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group()
                parsed_date = self.parse_date(date_str)
                if parsed_date:
                    dates.append((date_str, parsed_date))
        
        return dates
    
    def _clean_date_string(self, date_string: str) -> str:
        """Clean and normalize date string"""
        # Remove extra whitespace
        cleaned = date_string.strip()
        
        # Remove common prefixes/suffixes
        prefixes = ['date:', 'published:', 'created:', 'updated:']
        for prefix in prefixes:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove time components if present (keep only date part)
        time_patterns = [
            r'\s+\d{1,2}:\d{2}(:\d{2})?(\s*(AM|PM))?.*$',  # Time at end
            r'T\d{2}:\d{2}:\d{2}.*$',                       # ISO time
        ]
        
        for pattern in time_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def _fuzzy_date_parse(self, date_string: str) -> Optional[datetime]:
        """Attempt fuzzy date parsing for edge cases"""
        try:
            # Try with dateutil parser if available
            from dateutil.parser import parse
            return parse(date_string, fuzzy=True)
        except (ImportError, ValueError, TypeError):
            pass
        
        # Manual fuzzy parsing for common cases
        date_string = date_string.lower()
        
        # Handle "today", "yesterday", etc.
        if 'today' in date_string:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'yesterday' in date_string:
            return (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'tomorrow' in date_string:
            return (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Handle relative dates like "2 days ago"
        relative_match = re.search(r'(\d+)\s+(day|week|month)s?\s+ago', date_string)
        if relative_match:
            number = int(relative_match.group(1))
            unit = relative_match.group(2)
            
            if unit == 'day':
                return (datetime.now() - timedelta(days=number)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif unit == 'week':
                return (datetime.now() - timedelta(weeks=number)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif unit == 'month':
                # Approximate month as 30 days
                return (datetime.now() - timedelta(days=number*30)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        return None
    
    def format_date(self, date_obj: datetime, format_str: str = '%Y-%m-%d') -> str:
        """Format a datetime object as string"""
        if not isinstance(date_obj, datetime):
            return ''
        return date_obj.strftime(format_str)
    
    def date_range(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """Generate a list of dates between start and end date"""
        dates = []
        current_date = start_date
        
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        return dates
    
    def is_date_in_range(self, target_date: datetime, start_date: datetime, end_date: datetime) -> bool:
        """Check if a date falls within a range"""
        return start_date <= target_date <= end_date
    
    def get_date_variations(self, date_obj: datetime) -> List[str]:
        """Get different string representations of a date"""
        if not isinstance(date_obj, datetime):
            return []
        
        variations = []
        for pattern in self.date_patterns:
            try:
                formatted = date_obj.strftime(pattern)
                variations.append(formatted)
            except ValueError:
                continue
        
        return list(set(variations))  # Remove duplicates
