"""
Website detection utilities for Google Sheet Web Scraper
"""

import re
from typing import List, Tuple, Dict, Optional
from urllib.parse import urlparse, urljoin
import logging
from config import WEBSITE_PATTERNS

logger = logging.getLogger(__name__)


class WebsiteDetector:
    """Utility class for detecting and validating websites"""
    
    def __init__(self, custom_patterns: Dict = None):
        """Initialize with custom patterns if provided"""
        self.patterns = custom_patterns or WEBSITE_PATTERNS
    
    def is_valid_url(self, url: str) -> bool:
        """Check if a string is a valid URL"""
        if not url or not isinstance(url, str):
            return False
        
        try:
            result = urlparse(url.strip())
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def is_website(self, text: str) -> bool:
        """Check if text contains a website URL or domain"""
        if not text or not isinstance(text, str):
            return False
        
        text = text.strip().lower()
        
        # Check for URL prefixes
        for prefix in self.patterns['url_prefixes']:
            if text.startswith(prefix):
                return True
        
        # Check for domain extensions
        for extension in self.patterns['domain_extensions']:
            if extension in text:
                return True
        
        # Check for social media platforms
        for platform in self.patterns['social_media']:
            if platform in text:
                return True
        
        return False
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract all URLs from a text string"""
        if not text:
            return []
        
        urls = []
        
        # URL regex patterns
        url_patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+',  # HTTP/HTTPS URLs
            r'www\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+[^\s<>"{}|\\^`\[\]]*',  # www URLs
            r'\b[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+\b',  # Domain names
        ]
        
        for pattern in url_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                url = match.group().strip()
                if self.is_website(url):
                    urls.append(url)
        
        return list(set(urls))  # Remove duplicates
    
    def normalize_url(self, url: str) -> str:
        """Normalize a URL to a standard format"""
        if not url:
            return ''
        
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.'):
                url = 'https://' + url
            elif '.' in url and not url.startswith('//'):
                url = 'https://' + url
        
        # Parse and reconstruct
        try:
            parsed = urlparse(url)
            if parsed.netloc:
                # Ensure we have a proper URL
                scheme = parsed.scheme or 'https'
                netloc = parsed.netloc
                path = parsed.path or '/'
                
                normalized = f"{scheme}://{netloc}{path}"
                if parsed.query:
                    normalized += f"?{parsed.query}"
                if parsed.fragment:
                    normalized += f"#{parsed.fragment}"
                
                return normalized
        except Exception as e:
            logger.warning(f"Could not normalize URL '{url}': {e}")
        
        return url
    
    def extract_domain(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            parsed = urlparse(self.normalize_url(url))
            domain = parsed.netloc
            
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except Exception:
            return ''
    
    def categorize_website(self, url: str) -> str:
        """Categorize website by type"""
        domain = self.extract_domain(url).lower()
        
        # News websites
        news_keywords = ['news', 'times', 'post', 'herald', 'tribune', 'guardian', 'bbc', 'cnn', 'reuters']
        if any(keyword in domain for keyword in news_keywords):
            return 'news'
        
        # Social media
        social_media = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok', 'snapchat']
        if any(platform in domain for platform in social_media):
            return 'social_media'
        
        # E-commerce
        ecommerce_keywords = ['shop', 'store', 'buy', 'sell', 'amazon', 'ebay', 'etsy', 'marketplace']
        if any(keyword in domain for keyword in ecommerce_keywords):
            return 'ecommerce'
        
        # Blog platforms
        blog_keywords = ['blog', 'wordpress', 'blogger', 'medium', 'substack']
        if any(keyword in domain for keyword in blog_keywords):
            return 'blog'
        
        # Government
        if domain.endswith(('.gov', '.gov.uk', '.gov.au')):
            return 'government'
        
        # Education
        if domain.endswith('.edu'):
            return 'education'
        
        # Organization
        if domain.endswith('.org'):
            return 'organization'
        
        return 'general'
    
    def validate_url_accessibility(self, url: str) -> Tuple[bool, str]:
        """Check if URL is accessible (basic validation)"""
        try:
            import requests
            
            normalized_url = self.normalize_url(url)
            
            # Send HEAD request to check accessibility
            response = requests.head(normalized_url, timeout=10, allow_redirects=True)
            
            if response.status_code < 400:
                return True, f"Accessible (Status: {response.status_code})"
            else:
                return False, f"Not accessible (Status: {response.status_code})"
                
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Unknown error: {str(e)}"
    
    def get_website_info(self, url: str) -> Dict[str, str]:
        """Get comprehensive information about a website"""
        normalized_url = self.normalize_url(url)
        domain = self.extract_domain(normalized_url)
        category = self.categorize_website(normalized_url)
        is_accessible, access_status = self.validate_url_accessibility(normalized_url)
        
        return {
            'original_url': url,
            'normalized_url': normalized_url,
            'domain': domain,
            'category': category,
            'is_accessible': is_accessible,
            'access_status': access_status,
            'is_valid': self.is_valid_url(normalized_url)
        }
    
    def filter_websites(self, urls: List[str], categories: List[str] = None) -> List[str]:
        """Filter websites by categories"""
        if not categories:
            return urls
        
        filtered = []
        for url in urls:
            category = self.categorize_website(url)
            if category in categories:
                filtered.append(url)
        
        return filtered
    
    def deduplicate_urls(self, urls: List[str]) -> List[str]:
        """Remove duplicate URLs (considering normalized forms)"""
        seen_domains = set()
        unique_urls = []
        
        for url in urls:
            domain = self.extract_domain(url)
            if domain not in seen_domains:
                seen_domains.add(domain)
                unique_urls.append(self.normalize_url(url))
        
        return unique_urls
