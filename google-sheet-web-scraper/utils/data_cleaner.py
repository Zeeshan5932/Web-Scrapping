"""
Data cleaning utilities for Google Sheet Web Scraper
"""

import re
import html
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Utility class for cleaning and processing scraped data"""
    
    def __init__(self):
        """Initialize data cleaner"""
        pass
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text or not isinstance(text, str):
            return ''
        
        # Decode HTML entities
        cleaned = html.unescape(text)
        
        # Remove HTML tags
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove extra punctuation
        cleaned = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', cleaned)
        
        # Trim and return
        return cleaned.strip()
    
    def remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from text"""
        if not text:
            return ''
        
        # Remove script and style elements
        text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        return text
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        if not text:
            return ''
        
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_sentences(self, text: str, min_length: int = 10) -> List[str]:
        """Extract sentences from text"""
        if not text:
            return []
        
        # Split by sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            cleaned = self.clean_text(sentence)
            if len(cleaned) >= min_length:
                cleaned_sentences.append(cleaned)
        
        return cleaned_sentences
    
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []
        
        # Convert to lowercase and split
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter by length and common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'can', 'may', 'might', 'must', 'shall', 'from', 'up', 'down', 'out', 'off',
            'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'just', 'now'
        }
        
        keywords = []
        for word in words:
            if len(word) >= min_length and word not in stop_words:
                keywords.append(word)
        
        # Return unique keywords
        return list(set(keywords))
    
    def clean_scraped_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean scraped data structure"""
        if not isinstance(data, dict):
            return data
        
        cleaned_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                cleaned_data[key] = self.clean_text(value)
            elif isinstance(value, list):
                cleaned_data[key] = self.clean_list_data(value)
            elif isinstance(value, dict):
                cleaned_data[key] = self.clean_scraped_data(value)
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    def clean_list_data(self, data_list: List[Any]) -> List[Any]:
        """Clean list of data items"""
        if not isinstance(data_list, list):
            return data_list
        
        cleaned_list = []
        
        for item in data_list:
            if isinstance(item, str):
                cleaned_item = self.clean_text(item)
                if cleaned_item:  # Only add non-empty strings
                    cleaned_list.append(cleaned_item)
            elif isinstance(item, dict):
                cleaned_item = self.clean_scraped_data(item)
                if cleaned_item:  # Only add non-empty dicts
                    cleaned_list.append(cleaned_item)
            elif item is not None:
                cleaned_list.append(item)
        
        return cleaned_list
    
    def remove_duplicates(self, data_list: List[Dict[str, Any]], key: str = 'url') -> List[Dict[str, Any]]:
        """Remove duplicate items from list based on a key"""
        if not isinstance(data_list, list):
            return data_list
        
        seen = set()
        unique_data = []
        
        for item in data_list:
            if isinstance(item, dict) and key in item:
                identifier = item[key]
                if identifier not in seen:
                    seen.add(identifier)
                    unique_data.append(item)
            else:
                unique_data.append(item)
        
        return unique_data
    
    def filter_content_by_length(self, content: List[str], min_length: int = 20, max_length: int = 5000) -> List[str]:
        """Filter content by length"""
        if not isinstance(content, list):
            return content
        
        filtered = []
        for item in content:
            if isinstance(item, str) and min_length <= len(item) <= max_length:
                filtered.append(item)
        
        return filtered
    
    def extract_urls_from_content(self, content: str) -> List[str]:
        """Extract URLs from content"""
        if not content:
            return []
        
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        
        return list(set(urls))  # Remove duplicates
    
    def clean_filename(self, filename: str) -> str:
        """Clean filename for safe file system usage"""
        if not filename:
            return 'untitled'
        
        # Remove or replace invalid characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove extra spaces and dots
        cleaned = re.sub(r'\s+', '_', cleaned)
        cleaned = re.sub(r'\.+', '.', cleaned)
        
        # Limit length
        if len(cleaned) > 100:
            cleaned = cleaned[:100]
        
        return cleaned.strip('._')
    
    def validate_data_structure(self, data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """Validate that data contains required fields"""
        if not isinstance(data, dict):
            return False, ['Data is not a dictionary']
        
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        is_valid = len(missing_fields) == 0
        return is_valid, missing_fields
    
    def merge_similar_content(self, content_list: List[str], similarity_threshold: float = 0.8) -> List[str]:
        """Merge similar content items to reduce duplicates"""
        if not content_list or len(content_list) <= 1:
            return content_list
        
        # Simple similarity check based on shared words
        def calculate_similarity(text1: str, text2: str) -> float:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
        
        merged_content = []
        used_indices = set()
        
        for i, content1 in enumerate(content_list):
            if i in used_indices:
                continue
            
            similar_items = [content1]
            used_indices.add(i)
            
            for j, content2 in enumerate(content_list[i+1:], i+1):
                if j in used_indices:
                    continue
                
                similarity = calculate_similarity(content1, content2)
                if similarity >= similarity_threshold:
                    similar_items.append(content2)
                    used_indices.add(j)
            
            # Merge similar items (take the longest one)
            merged_item = max(similar_items, key=len)
            merged_content.append(merged_item)
        
        return merged_content
    
    def sanitize_json_data(self, data: Any) -> Any:
        """Sanitize data for JSON serialization"""
        if isinstance(data, dict):
            return {key: self.sanitize_json_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_json_data(item) for item in data]
        elif isinstance(data, str):
            # Ensure valid Unicode
            try:
                return data.encode('utf-8').decode('utf-8')
            except UnicodeError:
                return data.encode('utf-8', errors='ignore').decode('utf-8')
        elif data is None or isinstance(data, (int, float, bool)):
            return data
        else:
            # Convert other types to string
            return str(data)
