"""
OpenAI Service Module

This module provides AI-powered privacy policy analysis using OpenAI's GPT models.
It integrates with the compliance scanning pipeline to offer intelligent insights
about GDPR/CCPA compliance.

Classes:
    OpenAIService: Main service for AI-powered analysis

Features:
    - Privacy policy fetching from websites
    - GDPR/CCPA compliance analysis
    - Remediation advice generation
    - Robust error handling with retries
    
Configuration:
    Requires OPENAI_API_KEY environment variable to be set for AI features.
    Without this, the service gracefully degrades to manual analysis only.

Example:
    >>> service = OpenAIService()
    >>> analysis = service.analyze_privacy_policy(url, scan_results)
    >>> print(analysis)
"""

import os
from typing import Dict, Any, Optional
import logging
from openai import OpenAI
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from config import Config
from exceptions import AIServiceError, NetworkError

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Service for OpenAI-powered privacy policy analysis.
    
    Provides AI-powered analysis of privacy policies including:
    - GDPR/CCPA compliance assessment
    - Data collection practices
    - User rights documentation
    - Remediation recommendations
    
    Attributes:
        api_key: OpenAI API key from environment
        client: OpenAI client instance
        session: HTTP session for fetching policy content
    """
    
    def __init__(self):
        """Initialize the OpenAI service with API key and HTTP session."""
        self.api_key = Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.
        
        Returns:
            Configured requests.Session instance.
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
    
    def analyze_privacy_policy(self, url: str, scan_results: Dict[str, Any]) -> Optional[str]:
        """
        Analyze privacy policy using OpenAI.
        
        Args:
            url: The website URL
            scan_results: Dictionary containing scan results
            
        Returns:
            AI-generated analysis string or None if unavailable
        """
        if not self.client:
            logger.warning("OpenAI API key not configured - skipping AI analysis")
            return None
        
        try:
            # Get privacy policy URL from scan results
            privacy_policy_status = scan_results.get("privacy_policy", "")
            
            if "Found" not in privacy_policy_status:
                return "**No privacy policy detected** - Cannot perform AI analysis without a privacy policy."
            
            # Extract privacy policy content
            policy_text = self._fetch_privacy_policy(url)
            
            if not policy_text:
                return "**Unable to fetch privacy policy content** - The policy may be behind authentication or dynamically loaded."
            
            # Truncate if too long (to stay within token limits)
            max_length = Config.OPENAI_MAX_TOKENS * 2
            if len(policy_text) > max_length:
                policy_text = policy_text[:max_length] + "...\n[Content truncated]"
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(url, policy_text, scan_results)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a privacy compliance expert specializing in GDPR and CCPA regulations. Provide clear, actionable analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=Config.OPENAI_MAX_TOKENS
            )
            
            logger.info(f"Successfully analyzed privacy policy for {url}")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI analysis error for {url}: {e}")
            raise AIServiceError(f"AI Analysis Error: {str(e)}") from e
    
    def _fetch_privacy_policy(self, base_url: str) -> Optional[str]:
        """
        Fetch privacy policy content from the website.
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            Privacy policy text or None if not found
        """
        try:
            # Common privacy policy paths
            policy_paths = [
                "/privacy-policy",
                "/privacy",
                "/privacy-notice",
                "/legal/privacy",
                "/privacy-statement"
            ]
            
            headers = {"User-Agent": Config.USER_AGENT}
            
            # Try to find privacy policy link in the page
            response = self.session.get(
                base_url,
                timeout=Config.REQUEST_TIMEOUT,
                headers=headers,
                allow_redirects=True
            )
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Look for privacy policy links
            privacy_links = soup.find_all(
                "a",
                href=True,
                string=lambda s: s and "privacy" in s.lower()
            )
            
            policy_url = None
            if privacy_links:
                href = privacy_links[0]["href"]
                if href.startswith("http"):
                    policy_url = href
                elif href.startswith("//"):
                    policy_url = "https:" + href
                else:
                    policy_url = urljoin(base_url, href)
            else:
                # Try common paths
                for path in policy_paths:
                    test_url = base_url.rstrip("/") + path
                    try:
                        test_response = self.session.head(
                            test_url,
                            timeout=5,
                            allow_redirects=True
                        )
                        if test_response.status_code == 200:
                            policy_url = test_url
                            break
                        if test_response.status_code in {403, 405}:
                            get_response = self.session.get(
                                test_url,
                                timeout=5,
                                allow_redirects=True
                            )
                            if get_response.status_code == 200:
                                policy_url = test_url
                                break
                    except requests.RequestException:
                        continue
            
            if not policy_url:
                return None
            
            # Fetch privacy policy content
            policy_response = self.session.get(
                policy_url,
                timeout=Config.REQUEST_TIMEOUT,
                headers=headers,
                allow_redirects=True
            )
            policy_response.raise_for_status()
            policy_content_type = policy_response.headers.get("Content-Type", "")
            if "text/html" not in policy_content_type:
                return None
            
            policy_soup = BeautifulSoup(policy_response.content, "html.parser")
            
            # Remove script and style elements
            for script in policy_soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Get text
            text = policy_soup.get_text(separator="\n", strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)
            
            logger.info(f"Successfully fetched privacy policy from {policy_url}")
            return clean_text
            
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch privacy policy from {base_url}: {e}")
            return None
    
    def _create_analysis_prompt(self, url: str, policy_text: str, scan_results: Dict[str, Any]) -> str:
        """
        Create the analysis prompt for OpenAI.
        
        Args:
            url: Website URL
            policy_text: Privacy policy content
            scan_results: Scan results dictionary
            
        Returns:
            Formatted prompt for OpenAI API
        """
        prompt = f"""Analyze the following privacy policy for GDPR and CCPA compliance.

**Website:** {url}

**Automated Scan Results:**
- Cookie Consent: {scan_results.get('cookie_consent', 'Unknown')}
- Privacy Policy: {scan_results.get('privacy_policy', 'Unknown')}
- Contact Information: {scan_results.get('contact_info', 'Unknown')}
- Third-party Trackers: {len(scan_results.get('trackers', []))} detected

**Privacy Policy Content:**
{policy_text}

Please provide:

1. **Compliance Summary** - Brief assessment of GDPR/CCPA compliance
2. **Strengths** - What the policy does well
3. **Gaps** - Missing or unclear elements
4. **Recommendations** - Specific improvements needed
5. **Risk Level** - Low/Medium/High compliance risk

Keep the analysis concise and actionable."""
        
        return prompt
    
    def get_remediation_advice(self, scan_results: Dict[str, Any]) -> Optional[str]:
        """
        Get AI-powered remediation advice based on scan results.
        
        Args:
            scan_results: Dictionary containing scan results
            
        Returns:
            AI-generated remediation advice or None if unavailable
        """
        if not self.client:
            logger.warning("OpenAI API key not configured - skipping remediation advice")
            return None
        
        try:
            issues = []
            
            if "Not Found" in scan_results.get("cookie_consent", ""):
                issues.append("Missing cookie consent banner")
            
            if "Not Found" in scan_results.get("privacy_policy", ""):
                issues.append("Missing privacy policy")
            
            if "Not Found" in scan_results.get("contact_info", ""):
                issues.append("Missing contact information")
            
            if not issues:
                return "**All basic compliance indicators present!** Continue with detailed policy review."
            
            prompt = f"""As a privacy compliance expert, provide specific remediation steps for these issues:

Issues found:
{chr(10).join(f'- {issue}' for issue in issues)}

Provide:
1. Priority order for fixing these issues
2. Specific implementation steps for each
3. Estimated effort (hours/days)
4. Legal risks if left unaddressed

Be concise and actionable."""
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a privacy compliance expert specializing in GDPR and CCPA."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=Config.OPENAI_MAX_TOKENS // 2
            )
            
            logger.info("Successfully generated remediation advice")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating remediation advice: {e}")
            raise AIServiceError(f"Error generating advice: {str(e)}") from e
