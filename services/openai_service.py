import os
from openai import OpenAI
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class OpenAIService:
    """Service for OpenAI-powered privacy policy analysis"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
    
    def analyze_privacy_policy(self, url, scan_results):
        """
        Analyze privacy policy using OpenAI
        
        Args:
            url: The website URL
            scan_results: Dictionary containing scan results
            
        Returns:
            str: AI-generated analysis or None if unavailable
        """
        if not self.client:
            return None
        
        try:
            # Get privacy policy URL from scan results
            privacy_policy_status = scan_results.get("privacy_policy", "")
            
            if "Found" not in privacy_policy_status:
                return "**No privacy policy detected** - Cannot perform AI analysis without a privacy policy."
            
            # Extract privacy policy content
            policy_text = self._fetch_privacy_policy(url, scan_results)
            
            if not policy_text:
                return "**Unable to fetch privacy policy content** - The policy may be behind authentication or dynamically loaded."
            
            # Truncate if too long (to stay within token limits)
            max_length = 8000
            if len(policy_text) > max_length:
                policy_text = policy_text[:max_length] + "...\n[Content truncated]"
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(url, policy_text, scan_results)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
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
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"**AI Analysis Error:** {str(e)}"
    
    def _fetch_privacy_policy(self, base_url, scan_results):
        """Fetch privacy policy content from the website"""
        try:
            # Common privacy policy paths
            policy_paths = [
                "/privacy-policy",
                "/privacy",
                "/privacy-notice",
                "/legal/privacy",
                "/privacy-statement"
            ]
            
            # Try to find privacy policy link in the page
            response = self.session.get(base_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }, allow_redirects=True)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Look for privacy policy links
            privacy_links = soup.find_all("a", href=True, string=lambda s: s and "privacy" in s.lower())
            
            policy_url = None
            if privacy_links:
                href = privacy_links[0]["href"]
                if href.startswith("http"):
                    policy_url = href
                elif href.startswith("//"):
                    policy_url = "https:" + href
                else:
                    policy_url = urljoin(base_url.rstrip("/") + "/", href)
            else:
                # Try common paths
                for path in policy_paths:
                    test_url = base_url.rstrip("/") + path
                    try:
                        test_response = self.session.head(test_url, timeout=5, allow_redirects=True)
                        if test_response.status_code == 200:
                            policy_url = test_url
                            break
                        if test_response.status_code in {403, 405}:
                            get_response = self.session.get(test_url, timeout=5, allow_redirects=True)
                            if get_response.status_code == 200:
                                policy_url = test_url
                                break
                    except:
                        continue
            
            if not policy_url:
                return None
            
            # Fetch privacy policy content
            policy_response = self.session.get(policy_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }, allow_redirects=True)
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
            
            return clean_text
            
        except Exception as e:
            return None
    
    def _create_analysis_prompt(self, url, policy_text, scan_results):
        """Create the analysis prompt for OpenAI"""
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
    
    def get_remediation_advice(self, scan_results):
        """Get AI-powered remediation advice based on scan results"""
        if not self.client:
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
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a privacy compliance expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"**Error generating advice:** {str(e)}"
