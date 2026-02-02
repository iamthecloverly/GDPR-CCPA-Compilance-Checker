"""Input validation and sanitization module."""

import re
from typing import Tuple
from urllib.parse import urlparse
import logging

from exceptions import InvalidURLError, ValidationError

logger = logging.getLogger(__name__)


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate and normalize a URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        Tuple of (is_valid, normalized_url or error_message)
        
    Raises:
        InvalidURLError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise InvalidURLError("URL cannot be empty")
    
    # Strip whitespace
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        
        # Validate components
        if not parsed.netloc:
            raise InvalidURLError("Invalid URL: missing domain")
        
        if not parsed.scheme in ('http', 'https'):
            raise InvalidURLError(f"Invalid URL: unsupported scheme '{parsed.scheme}'")
        
        # Check for valid domain format
        domain = parsed.netloc.lower()
        if not re.match(r'^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$', domain):
            raise InvalidURLError(f"Invalid URL: malformed domain '{domain}'")
        
        logger.info(f"Validated URL: {url}")
        return True, url
        
    except InvalidURLError:
        raise
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        raise InvalidURLError(f"Invalid URL: {str(e)}") from e


def validate_batch_urls(urls: list) -> Tuple[list, list]:
    """
    Validate a batch of URLs.
    
    Args:
        urls: List of URL strings
        
    Returns:
        Tuple of (valid_urls, invalid_urls)
    """
    valid_urls = []
    invalid_urls = []
    
    if not urls or not isinstance(urls, list):
        raise ValidationError("URLs must be a non-empty list")
    
    for url in urls:
        try:
            _, normalized = validate_url(url)
            valid_urls.append(normalized)
        except InvalidURLError as e:
            invalid_urls.append({"url": url, "error": str(e)})
            logger.warning(f"Invalid URL in batch: {url} - {e}")
    
    if not valid_urls:
        raise ValidationError(f"No valid URLs in batch. Errors: {invalid_urls}")
    
    logger.info(f"Validated batch: {len(valid_urls)} valid, {len(invalid_urls)} invalid")
    return valid_urls, invalid_urls


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """
    Sanitize text input.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        ValidationError: If text exceeds maximum length
    """
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Check length
    if len(text) > max_length:
        raise ValidationError(f"Text exceeds maximum length of {max_length} characters")
    
    # Remove null bytes and other control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text


def validate_score(score: float) -> bool:
    """
    Validate a compliance score.
    
    Args:
        score: Score value
        
    Returns:
        True if valid (0-100)
        
    Raises:
        ValidationError: If score is out of range
    """
    if not isinstance(score, (int, float)):
        raise ValidationError(f"Score must be numeric, got {type(score)}")
    
    if not 0 <= score <= 100:
        raise ValidationError(f"Score must be between 0 and 100, got {score}")
    
    return True


def validate_grade(grade: str) -> bool:
    """
    Validate a compliance grade.
    
    Args:
        grade: Grade letter (A-F)
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If grade is invalid
    """
    valid_grades = {'A', 'B', 'C', 'D', 'F'}
    
    if not isinstance(grade, str) or grade.upper() not in valid_grades:
        raise ValidationError(f"Grade must be A-F, got {grade}")
    
    return True


def validate_api_key(api_key: str, min_length: int = 20) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key string
        min_length: Minimum key length
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If key is invalid
    """
    if not api_key or not isinstance(api_key, str):
        raise ValidationError("API key cannot be empty")
    
    if len(api_key) < min_length:
        raise ValidationError(f"API key too short (minimum {min_length} characters)")
    
    # Check for common invalid patterns
    if api_key.lower() == 'none' or api_key.lower() == 'null':
        raise ValidationError("API key cannot be 'none' or 'null'")
    
    if not re.match(r'^[a-zA-Z0-9_\-]+$', api_key):
        raise ValidationError("API key contains invalid characters")
    
    return True
