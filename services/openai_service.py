"""AI-powered privacy policy analysis using OpenAI GPT models."""

import os
from typing import Dict, Any, Optional
import logging
from openai import OpenAI
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import trafilatura

from config import Config
from exceptions import AIServiceError, NetworkError, InvalidURLError
from validators import validate_url
from utils import create_session

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI-powered privacy policy analysis."""

    def __init__(self):
        """Initialize the OpenAI service with API key and HTTP session."""
        self.api_key = Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.session = create_session()

    def analyze_privacy_policy(self, url: str, scan_results: Dict[str, Any]) -> Optional[str]:
        """Analyze privacy policy using OpenAI."""
        if not self.client:
            logger.warning("OpenAI API key not configured - skipping AI analysis")
            return None

        try:
            # Try to fetch privacy policy text
            policy_text = self._fetch_privacy_policy(url)

            if policy_text:
                # Truncate if too long (to stay within token limits)
                max_length = Config.OPENAI_MAX_TOKENS * 2
                if len(policy_text) > max_length:
                    policy_text = policy_text[:max_length] + "...\n[Content truncated]"
                prompt = self._create_analysis_prompt(url, policy_text, scan_results)
            else:
                # Fallback: analyse purely from scan results
                logger.info(f"Policy text unavailable for {url} — running scan-based analysis")
                prompt = self._create_scanonly_prompt(url, scan_results)

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a privacy compliance expert specialising in GDPR and CCPA regulations. Provide clear, actionable analysis.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=Config.OPENAI_MAX_TOKENS,
            )

            logger.info(f"Successfully analysed privacy compliance for {url}")
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"AI analysis error for {url}: {e}")
            raise AIServiceError(f"AI Analysis Error: {str(e)}") from e

    def _fetch_privacy_policy(self, base_url: str) -> Optional[str]:
        """Fetch privacy policy content from website."""
        try:
            policy_paths = [
                "/privacy-policy", "/privacy", "/privacy-notice",
                "/legal/privacy", "/privacy-statement", "/data-protection",
                "/legal/data-protection", "/gdpr", "/legal", "/policies/privacy",
                "/en/privacy-policy", "/about/privacy", "/terms-privacy",
                "/cookie-policy", "/data-privacy",
            ]

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
            }

            policy_url = None

            # Try to find privacy policy link in the page
            try:
                response = self.session.get(
                    base_url,
                    timeout=Config.REQUEST_TIMEOUT,
                    headers=headers,
                    allow_redirects=True,
                )
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "")

                if "text/html" in content_type:
                    soup = BeautifulSoup(response.content, "html.parser")
                    keywords = [
                        "privacy", "data protection", "data-protection",
                        "gdpr", "ccpa", "cookie policy", "data policy",
                    ]
                    all_links = soup.find_all("a", href=True)
                    privacy_link = None

                    for link in all_links:
                        if any(k in link.get_text().lower() for k in keywords):
                            privacy_link = link
                            break
                    if not privacy_link:
                        for link in all_links:
                            href = link.get("href", "").lower()
                            if any(k in href for k in keywords):
                                privacy_link = link
                                break

                    if privacy_link:
                        href = privacy_link["href"]
                        if href.startswith("http"):
                            policy_url = href
                        elif href.startswith("//"):
                            policy_url = "https:" + href
                        else:
                            policy_url = urljoin(base_url, href)
            except requests.RequestException:
                pass

            # If not found via scraping, try common paths
            if not policy_url:
                for path in policy_paths:
                    test_url = base_url.rstrip("/") + path
                    try:
                        test_response = self.session.head(
                            test_url, timeout=5, headers=headers, allow_redirects=True
                        )
                        if test_response.status_code == 200:
                            policy_url = test_url
                            break
                        if test_response.status_code in {403, 405}:
                            get_response = self.session.get(
                                test_url, timeout=5, headers=headers, allow_redirects=True
                            )
                            if get_response.status_code == 200:
                                policy_url = test_url
                                break
                    except requests.RequestException:
                        continue

            if not policy_url:
                return None

            try:
                validate_url(policy_url)
            except InvalidURLError as e:
                logger.warning(f"Skipping invalid or unsafe privacy policy URL {policy_url}: {e}")
                return None

            policy_response = self.session.get(
                policy_url,
                timeout=Config.REQUEST_TIMEOUT,
                headers={**headers, "Referer": base_url},
                allow_redirects=True,
            )
            policy_response.raise_for_status()

            text = trafilatura.extract(policy_response.text)

            if not text:
                policy_soup = BeautifulSoup(policy_response.content, "html.parser")
                for tag in policy_soup(["script", "style", "nav", "header", "footer"]):
                    tag.decompose()
                text = policy_soup.get_text(separator="\n", strip=True)

            if not text:
                return None

            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)

            logger.info(f"Successfully fetched privacy policy from {policy_url}")
            return clean_text

        except requests.RequestException as e:
            logger.warning(f"Failed to fetch privacy policy from {base_url}: {e}")
            return None

    def _create_analysis_prompt(self, url: str, policy_text: str, scan_results: Dict[str, Any]) -> str:
        """Create analysis prompt for OpenAI."""
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

    def _create_scanonly_prompt(self, url: str, scan_results: Dict[str, Any]) -> str:
        """Fallback prompt when policy text cannot be fetched — uses scan data only."""
        trackers = scan_results.get("trackers", [])
        tracker_list = ", ".join(trackers[:10]) if trackers else "None detected"
        prompt = f"""You are auditing the GDPR/CCPA compliance posture of a website based on automated scan results only.
The privacy policy page could not be retrieved (it may be dynamically loaded or behind a CDN).

**Website:** {url}

**Automated Scan Findings:**
- Cookie Consent Banner: {scan_results.get('cookie_consent', 'Unknown')}
- Privacy Policy Link: {scan_results.get('privacy_policy', 'Unknown')}
- Contact / DPO Information: {scan_results.get('contact_info', 'Unknown')}
- Third-party Trackers Detected ({len(trackers)}): {tracker_list}
- Score: {scan_results.get('score', 'N/A')}/100
- Grade: {scan_results.get('grade', 'N/A')}

Based on these observable signals, provide:

1. **Compliance Assessment** — what the scan findings suggest about GDPR/CCPA posture
2. **Key Risks** — specific concerns raised by the scan data
3. **Recommended Actions** — prioritised next steps to improve compliance
4. **Risk Level** — Low / Medium / High

Be concise, specific to these findings, and note that a full policy text review was not possible."""
        return prompt

    def get_remediation_advice(self, scan_results: Dict[str, Any]) -> Optional[str]:
        """Get AI-powered remediation advice."""
        if not self.client:
            logger.warning(
                "OpenAI API key not configured - skipping remediation advice"
            )
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
                    {
                        "role": "system",
                        "content": "You are a privacy compliance expert specializing in GDPR and CCPA.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=Config.OPENAI_MAX_TOKENS // 2,
            )

            logger.info("Successfully generated remediation advice")
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating remediation advice: {e}")
            raise AIServiceError(f"Error generating advice: {str(e)}") from e
