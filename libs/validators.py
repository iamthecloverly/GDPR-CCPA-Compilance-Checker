"""Input validation utilities for the compliance checker."""

import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def validate_domain(domain: str) -> Tuple[bool, str]:
    """
    Validate domain format.
    
    Args:
        domain: Domain to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not domain or not isinstance(domain, str):
        return False, "Domain cannot be empty"
    
    domain = domain.strip().lower()
    
    # Remove protocol if present
    if "://" in domain:
        domain = domain.split("://", 1)[1]
    
    # Remove path if present
    if "/" in domain:
        domain = domain.split("/")[0]
    
    # Validate domain pattern
    domain_pattern = r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$'
    if not re.match(domain_pattern, domain):
        return False, "Invalid domain format"
    
    # Check minimum length
    if len(domain) < 4:
        return False, "Domain too short"
    
    # Check maximum length
    if len(domain) > 253:
        return False, "Domain too long"
    
    return True, ""


def validate_csv_content(csv_text: str, max_urls: int = 1000) -> Tuple[bool, str, List[str]]:
    """
    Validate CSV content with URLs.
    
    Args:
        csv_text: CSV content as string
        max_urls: Maximum number of URLs allowed
        
    Returns:
        Tuple of (is_valid, error_message, parsed_urls)
    """
    if not csv_text or not isinstance(csv_text, str):
        return False, "CSV content cannot be empty", []
    
    lines = csv_text.strip().split('\n')
    urls = []
    errors = []
    
    # Skip header if present
    start_idx = 0
    first_line = lines[0].strip().lower()
    if 'url' in first_line or 'website' in first_line or 'domain' in first_line:
        start_idx = 1
    
    for idx, line in enumerate(lines[start_idx:], start=start_idx):
        line = line.strip()
        if not line:
            continue
        
        # Try to extract URL (handle CSV with multiple columns)
        parts = line.split(',')
        url = parts[0].strip()
        
        if not url:
            continue
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://', 'www.', 'ftp://')):
            url = 'https://' + url
        
        urls.append(url)
        
        if len(urls) > max_urls:
            return False, f"Too many URLs (max {max_urls})", []
    
    if not urls:
        return False, "No valid URLs found in CSV", []
    
    return True, "", urls


def sanitize_domain(domain: str) -> str:
    """
    Sanitize domain input.
    
    Args:
        domain: Domain to sanitize
        
    Returns:
        Sanitized domain
    """
    if not domain:
        return ""
    
    domain = domain.strip().lower()
    
    # Remove protocol if present
    if "://" in domain:
        domain = domain.split("://", 1)[1]
    
    # Remove path and query parameters
    domain = domain.split("/")[0].split("?")[0]
    
    # Remove trailing/leading whitespace and special chars
    domain = re.sub(r'[^\w.\-]', '', domain)
    
    return domain


def validate_batch_size(count: int, max_batch: int = 100) -> Tuple[bool, str]:
    """
    Validate batch size.
    
    Args:
        count: Number of items in batch
        max_batch: Maximum allowed batch size
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if count <= 0:
        return False, "Batch size must be greater than 0"
    
    if count > max_batch:
        return False, f"Batch size exceeds limit ({max_batch})"
    
    return True, ""


def sanitize_text_input(text: str, max_length: int = 10000) -> Tuple[bool, str, str]:
    """
    Sanitize and validate text input.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed text length
        
    Returns:
        Tuple of (is_valid, error_message, sanitized_text)
    """
    if not text:
        return False, "Input cannot be empty", ""
    
    if not isinstance(text, str):
        return False, "Input must be text", ""
    
    # Check length
    if len(text) > max_length:
        return False, f"Input exceeds maximum length ({max_length} characters)", ""
    
    # Remove potentially harmful characters but keep alphanumeric and common symbols
    sanitized = re.sub(r'[<>{}[\]\\]', '', text)
    sanitized = sanitized.strip()
    
    if not sanitized:
        return False, "Input contains only invalid characters", ""
    
    return True, "", sanitized
