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

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import io
from pypdf import PdfReader
from typing import Dict, List, Optional
import logging

from config import Config
from constants import (
    COOKIE_KEYWORDS, PRIVACY_KEYWORDS, CCPA_KEYWORDS, TRACKING_DOMAINS,
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
        self.headers = {"User-Agent": USER_AGENT}
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic and connection pooling.
        
        Returns:
            Configured requests.Session with HTTPAdapter and Retry strategy.
        """
        session = requests.Session()
        retries = Retry(
            total=Config.MAX_RETRIES,
            backoff_factor=Config.BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))
        return session

    def _get_content(self, url: str) -> (bytes, str):
        """
        Fetch content from a URL (HTML or PDF).
        
        Args:
            url: The URL to fetch
            
        Returns:
            Tuple of (raw content as bytes, content type)
            
        Raises:
            NetworkError: If the request fails
        """
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                headers=self.headers,
                allow_redirects=True
            )
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            return response.content, content_type
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise NetworkError(f"Failed to fetch URL: {str(e)}") from e
    
    def analyze_compliance(self, url: str) -> Dict[str, any]:
        """
        Analyze a website or PDF for compliance indicators.
        
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
            # Fetch content
            content, content_type = self._get_content(url)

            if "application/pdf" in content_type:
                return self._analyze_pdf(content, url)

            if "text/html" not in content_type:
                 raise NetworkError(f"URL returned unsupported content type: {content_type}")

            soup = BeautifulSoup(content, "html.parser")
            
            results = {
                "cookie_consent": self._check_cookie_consent(soup),
                "privacy_policy": self._check_privacy_policy(soup, url),
                "ccpa_compliance": self._check_ccpa_compliance(soup),
                "contact_info": self._check_contact_info(soup),
                "trackers": self._detect_trackers(soup)
            }
            
            # Smart Crawl: If key elements are missing, crawl internal links
            missing_elements = []
            if not results["privacy_policy"].startswith("Found"):
                missing_elements.append("privacy_policy")
            if not results["ccpa_compliance"].startswith("Found"):
                missing_elements.append("ccpa_compliance")

            if missing_elements:
                logger.info(f"Missing elements {missing_elements}, initiating smart crawl")
                self._smart_crawl(url, soup, results, missing_elements)

            logger.info(f"Successfully analyzed {url}")
            return results
            
        except NetworkError:
            raise
        except Exception as e:
            logger.error(f"Analysis error for {url}: {e}")
            raise ScanError(f"Analysis error: {str(e)}") from e

    def _analyze_pdf(self, content: bytes, url: str) -> Dict[str, any]:
        """
        Analyze a PDF document for compliance indicators.

        Args:
            content: Raw PDF content
            url: The source URL

        Returns:
            Dictionary containing compliance findings
        """
        try:
            reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            text_lower = text.lower()

            # Analyze text content directly
            results = {
                "cookie_consent": "N/A (PDF Document)",
                "privacy_policy": "Found - Direct PDF Link",
                "ccpa_compliance": "Found - CCPA Terms Detected" if any(k in text_lower for k in CCPA_KEYWORDS) else "Not Found in PDF",
                "contact_info": self._check_contact_info_text(text),
                "trackers": [] # Cannot detect JS trackers in PDF
            }

            return results
        except Exception as e:
            logger.error(f"PDF analysis failed: {e}")
            return {
                "cookie_consent": "Error analyzing PDF",
                "privacy_policy": "Found - Direct PDF Link",
                "ccpa_compliance": "Error analyzing PDF",
                "contact_info": "Error analyzing PDF",
                "trackers": []
            }
    
    def _check_cookie_consent(self, soup: BeautifulSoup) -> str:
        """
        Check for cookie consent banner.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Status string indicating whether cookie consent was found
        """
        # Check for common cookie banner elements
        for keyword in COOKIE_KEYWORDS:
            # Check in text content
            if soup.find(string=re.compile(keyword, re.IGNORECASE)):
                return "Found - Cookie consent detected"
            
            # Check in div IDs and classes
            if soup.find(["div", "section"], {"id": re.compile(keyword, re.IGNORECASE)}):
                return "Found - Cookie consent banner detected"
            
            if soup.find(["div", "section"], {"class": re.compile(keyword, re.IGNORECASE)}):
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
        # Look for links containing privacy keywords
        all_links = soup.find_all("a", href=True)
        
        for link in all_links:
            link_text = link.get_text().lower()
            href = link.get("href", "").lower()
            
            for keyword in PRIVACY_KEYWORDS:
                if keyword in link_text or keyword in href:
                    return "Found - Privacy policy link detected"
        
        return "Not Found - No privacy policy link detected"
    
    def _check_ccpa_compliance(self, soup: BeautifulSoup) -> str:
        """
        Check for CCPA compliance indicators (Do Not Sell link).

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            Status string indicating whether CCPA elements were found
        """
        # Look for links containing CCPA keywords
        all_links = soup.find_all("a", href=True)

        for link in all_links:
            link_text = link.get_text().lower()
            href = link.get("href", "").lower()

            for keyword in CCPA_KEYWORDS:
                if keyword in link_text or keyword in href:
                    return "Found - CCPA 'Do Not Sell' link detected"

        return "Not Found - No CCPA 'Do Not Sell' link detected"

    def _check_contact_info(self, soup: BeautifulSoup) -> str:
        """
        Check for contact information in HTML.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Status string with details of found contact information
        """
        return self._check_contact_info_text(soup.get_text())
        
    def _check_contact_info_text(self, text: str) -> str:
        """
        Check for contact information in raw text.
        
        Args:
            text: Text to analyze

        Returns:
            Status string with details of found contact information
        """
        has_email = bool(EMAIL_PATTERN.search(text))
        has_phone = bool(PHONE_PATTERN.search(text))
        
        if has_email or has_phone:
            details = []
            if has_email:
                details.append("email")
            if has_phone:
                details.append("phone")
            
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

    def _smart_crawl(self, base_url: str, soup: BeautifulSoup, results: Dict[str, any], missing: List[str]):
        """
        Crawl internal links to find missing compliance elements.

        Args:
            base_url: The starting URL
            soup: BeautifulSoup object of the starting page
            results: Results dictionary to update
            missing: List of missing element keys
        """
        internal_links = set()
        domain = urlparse(base_url).netloc

        # Find relevant internal links (e.g., footer links, legal pages)
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)

            # Only follow internal links
            if parsed.netloc == domain or not parsed.netloc:
                # Prioritize promising paths
                lower_href = href.lower()
                if any(x in lower_href for x in ["legal", "terms", "about", "privacy", "compliance", "footer"]):
                    internal_links.add(full_url)

        # Limit the number of pages to crawl to avoid long scan times
        crawl_limit = 3
        crawled_count = 0

        for url in internal_links:
            if crawled_count >= crawl_limit:
                break

            try:
                html = self._get_html(url)
                sub_soup = BeautifulSoup(html, "html.parser")

                if "privacy_policy" in missing and not results["privacy_policy"].startswith("Found"):
                    status = self._check_privacy_policy(sub_soup, url)
                    if status.startswith("Found"):
                        results["privacy_policy"] = status
                        missing.remove("privacy_policy")

                if "ccpa_compliance" in missing and not results["ccpa_compliance"].startswith("Found"):
                    status = self._check_ccpa_compliance(sub_soup)
                    if status.startswith("Found"):
                        results["ccpa_compliance"] = status
                        missing.remove("ccpa_compliance")

                crawled_count += 1

                if not missing:
                    break

            except Exception as e:
                logger.warning(f"Failed to crawl internal link {url}: {e}")

    def _get_html(self, url: str) -> bytes:
        """
        Fetch HTML content from a URL (compatibility wrapper).
        """
        content, content_type = self._get_content(url)
        if "text/html" not in content_type:
             raise NetworkError(f"URL did not return HTML content (got {content_type})")
        return content
