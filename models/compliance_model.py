import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

class ComplianceModel:
    """Model for analyzing website compliance indicators"""
    
    def __init__(self):
        self.timeout = 10
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def analyze_compliance(self, url):
        """
        Analyze a website for compliance indicators
        
        Args:
            url: The website URL
            
        Returns:
            dict: Compliance findings
        """
        try:
            # Fetch webpage
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            results = {
                "cookie_consent": self._check_cookie_consent(soup),
                "privacy_policy": self._check_privacy_policy(soup, url),
                "contact_info": self._check_contact_info(soup),
                "trackers": self._detect_trackers(soup)
            }
            
            return results
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
            raise Exception(f"Analysis error: {str(e)}")
    
    def _check_cookie_consent(self, soup):
        """Check for cookie consent banner"""
        cookie_keywords = [
            "cookie", "consent", "privacy notice", "we use cookies",
            "accept cookies", "cookie policy", "cookie banner"
        ]
        
        # Check for common cookie banner elements
        for keyword in cookie_keywords:
            # Check in text content
            if soup.find(string=re.compile(keyword, re.IGNORECASE)):
                return "Found - Cookie consent detected"
            
            # Check in div IDs and classes
            if soup.find(["div", "section"], {"id": re.compile(keyword, re.IGNORECASE)}):
                return "Found - Cookie consent banner detected"
            
            if soup.find(["div", "section"], {"class": re.compile(keyword, re.IGNORECASE)}):
                return "Found - Cookie consent banner detected"
        
        return "Not Found - No cookie consent banner detected"
    
    def _check_privacy_policy(self, soup, base_url):
        """Check for privacy policy link"""
        privacy_keywords = ["privacy", "privacy policy", "privacy notice", "data protection"]
        
        # Look for links containing privacy keywords
        all_links = soup.find_all("a", href=True)
        
        for link in all_links:
            link_text = link.get_text().lower()
            href = link.get("href", "").lower()
            
            for keyword in privacy_keywords:
                if keyword in link_text or keyword in href:
                    return f"Found - Privacy policy link detected"
        
        return "Not Found - No privacy policy link detected"
    
    def _check_contact_info(self, soup):
        """Check for contact information"""
        # Email pattern
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Phone pattern (simple)
        phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\b\+?\d{1,3}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,9}\b')
        
        page_text = soup.get_text()
        
        has_email = bool(email_pattern.search(page_text))
        has_phone = bool(phone_pattern.search(page_text))
        
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
    
    def _detect_trackers(self, soup):
        """Detect third-party tracking scripts"""
        trackers = []
        
        # Common tracking domains
        tracking_domains = [
            "google-analytics.com",
            "googletagmanager.com",
            "facebook.net",
            "doubleclick.net",
            "scorecardresearch.com",
            "quantserve.com",
            "hotjar.com",
            "mouseflow.com",
            "crazyegg.com",
            "inspectlet.com",
            "hubspot.com",
            "mixpanel.com",
            "segment.com",
            "amplitude.com",
            "heap.io"
        ]
        
        # Check script tags
        scripts = soup.find_all("script", src=True)
        
        for script in scripts:
            src = script.get("src", "")
            for domain in tracking_domains:
                if domain in src:
                    if domain not in trackers:
                        trackers.append(domain)
        
        # Check inline scripts for tracking code
        inline_scripts = soup.find_all("script", src=False)
        for script in inline_scripts:
            script_content = script.string or ""
            for domain in tracking_domains:
                if domain in script_content:
                    if domain not in trackers:
                        trackers.append(domain)
        
        return trackers
