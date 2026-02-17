"""
Compliance Model Module

This module provides web scraping and analysis capabilities for detecting GDPR/CCPA
compliance indicators on websites. It uses BeautifulSoup4 for HTML parsing and 
requests with retry logic for robust HTTP requests.

Classes:
    ComplianceModel: Main class for analyzing website compliance

Key Features:
    - HTTP retry logic with exponential backoff
    - Connection pooling for performance
    - Detection of cookie consent banners
    - Privacy policy link detection
    - Contact information detection (email, phone)
    - Third-party tracker identification
    
Example:
    >>> model = ComplianceModel()
    >>> results = model.analyze_compliance('https://example.com')
    >>> print(f"Cookie consent: {results['cookie_consent']}")
"""

import os
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
import logging

from config import Config
from utils import create_session
from constants import (
    COOKIE_PATTERNS, PRIVACY_PATTERNS, TRACKING_DOMAINS,
    EMAIL_PATTERN, PHONE_PATTERN, USER_AGENT
)
from exceptions import NetworkError, ScanError

logger = logging.getLogger(__name__)

class ComplianceModel:
    """
    Model for analyzing website compliance indicators.
    
    Performs web scraping to detect GDPR/CCPA compliance elements including
    cookie consent banners, privacy policies, contact information, and trackers.
    
    Attributes:
        timeout: Request timeout in seconds
        headers: HTTP headers for requests
        session: Persistent HTTP session with retry logic
    """
    
    def __init__(self):
        """Initialize the compliance model with configured session."""
        self.timeout = Config.REQUEST_TIMEOUT
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Connection": "keep-alive"
        }
        self.session = create_session()

    def _get_html(self, url: str) -> bytes:
        """
        Fetch HTML content from a URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            Raw HTML content as bytes
            
        Raises:
            NetworkError: If the request fails or doesn't return HTML
        """
        try:
            verify_ssl = os.getenv("VERIFY_SSL", "true").lower() == "true"
            response = self.session.get(
                url,
                timeout=self.timeout,
                headers=self.headers,
                allow_redirects=True,
                verify=verify_ssl
            )
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                raise NetworkError(f"URL did not return HTML content (got {content_type})")
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise NetworkError(f"Failed to fetch URL: {str(e)}") from e
    
    def analyze_compliance(self, url: str) -> Dict[str, any]:
        """
        Analyze a website for compliance indicators.
        
        Args:
            url: The website URL to analyze
            
        Returns:
            Dictionary containing compliance findings:
                - cookie_consent: Cookie banner detection result
                - privacy_policy: Privacy policy detection result
                - contact_info: Contact information detection result
                - trackers: List of detected tracking domains
                
        Raises:
            ScanError: If analysis fails
        """
        try:
            # Fetch webpage
            html = self._get_html(url)
            soup = BeautifulSoup(html, "html.parser")
            
            results = {
                "cookie_consent": self._check_cookie_consent(soup),
                "privacy_policy": self._check_privacy_policy(soup, url),
                "contact_info": self._check_contact_info(soup),
                "trackers": self._detect_trackers(soup)
            }
            
            logger.info(f"Successfully analyzed {url}")
            return results
            
        except NetworkError:
            raise
        except Exception as e:
            logger.error(f"Analysis error for {url}: {e}")
            raise ScanError(f"Analysis error: {str(e)}") from e
    
    def _check_cookie_consent(self, soup: BeautifulSoup) -> str:
        """
        Check for cookie consent banner.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Status string indicating whether cookie consent was found
        """
        if not COOKIE_KEYWORDS:
            return "Not Found - No cookie consent banner detected"

        # Pre-compile combined regex for better performance
        cookie_pattern = re.compile(
            "|".join(re.escape(k) for k in COOKIE_KEYWORDS), re.IGNORECASE
        )

        # Check in text content (single traversal)
        if soup.find(string=cookie_pattern):
            return "Found - Cookie consent detected"

        # Check in div/section IDs (single traversal)
        if soup.find(["div", "section"], id=cookie_pattern):
            return "Found - Cookie consent banner detected"

        # Check in div/section classes (single traversal)
        if soup.find(["div", "section"], class_=cookie_pattern):
            return "Found - Cookie consent banner detected"

        return "Not Found - No cookie consent banner detected"
    
    def _check_privacy_policy(self, soup: BeautifulSoup, base_url: str) -> str:
        """
        Check for privacy policy link.
        
        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL of the website
            
        Returns:
            Status string indicating whether privacy policy was found
        """
        # Look for links containing privacy keywords using pre-compiled patterns
        all_links = soup.find_all("a", href=True)
        
        for link in all_links:
            link_text = link.get_text()
            href = link.get("href", "")
            
            for pattern in PRIVACY_PATTERNS:
                if pattern.search(link_text) or pattern.search(href):
                    return "Found - Privacy policy link detected"
        
        return "Not Found - No privacy policy link detected"
    
    def _check_contact_info(self, soup: BeautifulSoup) -> str:
        """
        Check for contact information.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Status string with details of found contact information
        """
        page_text = soup.get_text()
        
        has_email = bool(EMAIL_PATTERN.search(page_text))
        has_phone = bool(PHONE_PATTERN.search(page_text))
        
        # Check for contact page link
        contact_link = soup.find("a", href=True, string=re.compile("contact", re.IGNORECASE))
        
        if has_email or has_phone or contact_link:
            details = []
            if has_email:
                details.append("email")
            if has_phone:
                details.append("phone")
            if contact_link:
                details.append("contact page")
            
            return f"Found - Contact info detected ({', '.join(details)})"
        
        return "Not Found - No contact information detected"
    
    def _detect_trackers(self, soup: BeautifulSoup) -> List[str]:
        """
        Detect third-party tracking scripts.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of detected tracking domains
        """
        trackers = []
        
        # Check script tags
        scripts = soup.find_all("script", src=True)
        
        for script in scripts:
            src = script.get("src", "")
            for domain in TRACKING_DOMAINS:
                if domain in src:
                    if domain not in trackers:
                        trackers.append(domain)
        
        # Check inline scripts for tracking code
        inline_scripts = soup.find_all("script", src=False)
        for script in inline_scripts:
            script_content = script.string or ""
            for domain in TRACKING_DOMAINS:
                if domain in script_content:
                    if domain not in trackers:
                        trackers.append(domain)
        
        return trackers
