"""Compliance controller orchestrating scanning workflow."""

from typing import Dict, List, Any
import logging
import threading
from cachetools import TTLCache

from models.compliance_model import ComplianceModel
from services.openai_service import OpenAIService
from config import Config
from constants import GRADE_THRESHOLDS, TRACKER_TIERS, STATUS_THRESHOLDS, SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW, is_detected
from exceptions import ScanError, NetworkError

logger = logging.getLogger(__name__)


class ComplianceController:
    """Controller for handling compliance scanning operations."""
    
    def __init__(self):
        """Initialize the controller with model and AI service."""
        self.model = ComplianceModel()
        self.openai_service = OpenAIService()
        self._cache_lock = threading.Lock()
        self._cache = TTLCache(maxsize=Config.CACHE_MAXSIZE, ttl=Config.CACHE_TTL_SECONDS)

    def scan_website(self, url):
        """
        Perform a comprehensive compliance scan on a website.
        
        Args:
            url: The website URL to scan
            
        Returns:
            Dictionary containing:
                - score: Compliance score (0-100)
                - grade: Letter grade (A-F)
                - status: Status string (Compliant/Needs Improvement/Non-Compliant)
                - cookie_consent: Cookie consent detection result
                - privacy_policy: Privacy policy detection result
                - contact_info: Contact information detection result
                - trackers: List of detected trackers
                - details: Full analysis results
                
        Raises:
            ScanError: If the scan fails
        """
        # Check cache first
        with self._cache_lock:
            if url in self._cache:
                logger.info(f"Returning cached scan results for {url}")
                return self._cache[url]

        try:
            logger.info("AUDIT scan_start url=%s", url)

            # Perform web scraping and analysis
            results = self.model.analyze_compliance(url)
            
            # Calculate score and metrics
            score = self._calculate_score(results)
            grade = self._calculate_grade(score)
            status = self._determine_status(score)
            score_breakdown = self.get_score_breakdown(results)
            
            # Generate findings and recommendations from scan results
            findings = self._generate_findings(results)
            recommendations = self._generate_recommendations(results)

            # Construct response
            response = {
                "score": score,
                "grade": grade,
                "status": status,
                "score_breakdown": {item["Category"]: item["Points"] for item in score_breakdown},
                "cookie_consent": results.get("cookie_consent", "Not Found"),
                "privacy_policy": results.get("privacy_policy", "Not Found"),
                "contact_info": results.get("contact_info", "Not Found"),
                "trackers": results.get("trackers", []),
                "findings": findings,
                "recommendations": recommendations,
                "details": results
            }
            
            logger.info(
                "AUDIT scan_complete url=%s score=%s grade=%s status=%s trackers=%d",
                url, score, grade, status, len(results.get("trackers", [])),
            )

            # Cache the result
            with self._cache_lock:
                self._cache[url] = response

            return response

        except (ScanError, NetworkError):
            logger.warning("AUDIT scan_failed url=%s", url)
            raise
        except Exception as e:
            logger.error("AUDIT scan_error url=%s error=%r", url, str(e))
            raise ScanError(f"Scan failed: {str(e)}") from e

    
    def _calculate_score(self, results: Dict[str, Any]) -> int:
        """
        Calculate compliance score based on findings.
        
        Scoring breakdown:
        - Cookie consent: 30 points
        - Privacy policy: 30 points
        - Contact information: 20 points
        - Tracker penalty: up to 20 points
        
        Args:
            results: Analysis results from ComplianceModel
            
        Returns:
            Compliance score (0-100)
        """
        score = 0
        
        # Cookie consent (weighted from config)
        if is_detected(results.get("cookie_consent", "")):
            score += Config.SCORING_WEIGHTS["cookie_consent"]
        
        # Privacy policy (weighted from config)
        if is_detected(results.get("privacy_policy", "")):
            score += Config.SCORING_WEIGHTS["privacy_policy"]
        
        # Contact information (weighted from config)
        if is_detected(results.get("contact_info", "")):
            score += Config.SCORING_WEIGHTS["contact_info"]
        
        # Tracker penalty (weighted from config)
        trackers = results.get("trackers", [])
        score += self._calculate_tracker_points(len(trackers))
        
        return min(100, max(0, score))
    
    def get_score_breakdown(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get detailed score breakdown by category.
        
        Args:
            results: Scan results dictionary
            
        Returns:
            List of dictionaries with 'Category' and 'Points' keys
        """
        breakdown = []
        
        # Cookie consent points
        cookie_points = 0
        if is_detected(results.get("cookie_consent", "")):
            cookie_points = Config.SCORING_WEIGHTS["cookie_consent"]
        breakdown.append({"Category": "Cookie Consent", "Points": cookie_points})
        
        # Privacy policy points
        privacy_points = 0
        if is_detected(results.get("privacy_policy", "")):
            privacy_points = Config.SCORING_WEIGHTS["privacy_policy"]
        breakdown.append({"Category": "Privacy Policy", "Points": privacy_points})
        
        # Contact information points
        contact_points = 0
        if is_detected(results.get("contact_info", "")):
            contact_points = Config.SCORING_WEIGHTS["contact_info"]
        breakdown.append({"Category": "Contact Info", "Points": contact_points})
        
        # Tracker points
        trackers = results.get("trackers", [])
        tracker_points = self._calculate_tracker_points(len(trackers))
        breakdown.append({"Category": f"Trackers ({len(trackers)} found)", "Points": tracker_points})
        
        return breakdown
    
    def _calculate_grade(self, score: int) -> str:
        """
        Convert score to letter grade.
        
        Args:
            score: Compliance score (0-100)
            
        Returns:
            Letter grade (A-F)
        """
        for grade, threshold in GRADE_THRESHOLDS.items():
            if score >= threshold:
                return grade
    
    def _determine_status(self, score: int) -> str:
        """
        Determine compliance status based on score.
        
        Args:
            score: Compliance score (0-100)
            
        Returns:
            Status string (Compliant/Needs Improvement/Non-Compliant)
        """
        if score >= STATUS_THRESHOLDS["Compliant"]:
            return "Compliant"
        if score >= STATUS_THRESHOLDS["Needs Improvement"]:
            return "Needs Improvement"
        return "Non-Compliant"

    def _generate_findings(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate structured findings from raw scan results.

        Args:
            results: Raw scan results from ComplianceModel

        Returns:
            List of finding dicts with keys: category, issue, severity, passed
        """
        findings = []

        # Cookie consent
        cookie = results.get("cookie_consent", "")
        if is_detected(cookie):
            findings.append({
                "category": "Cookie Consent",
                "issue": "Cookie consent banner detected.",
                "severity": SEVERITY_LOW,
                "passed": True,
            })
        else:
            findings.append({
                "category": "Cookie Consent",
                "issue": "No cookie consent banner detected. GDPR/CCPA require informing users about cookie usage.",
                "severity": SEVERITY_HIGH,
                "passed": False,
            })

        # Privacy policy
        privacy = results.get("privacy_policy", "")
        if is_detected(privacy):
            findings.append({
                "category": "Privacy Policy",
                "issue": "Privacy policy link detected.",
                "severity": SEVERITY_LOW,
                "passed": True,
            })
        else:
            findings.append({
                "category": "Privacy Policy",
                "issue": "No privacy policy link detected. A privacy policy is required under GDPR and CCPA.",
                "severity": SEVERITY_HIGH,
                "passed": False,
            })

        # Contact info
        contact = results.get("contact_info", "")
        if is_detected(contact):
            findings.append({
                "category": "Contact Information",
                "issue": f"Contact information detected — {contact.replace('Found - ', '')}.",
                "severity": SEVERITY_LOW,
                "passed": True,
            })
        else:
            findings.append({
                "category": "Contact Information",
                "issue": "No contact information detected. GDPR requires a data controller contact (email or form).",
                "severity": SEVERITY_MEDIUM,
                "passed": False,
            })

        # Trackers
        trackers = results.get("trackers", [])
        if not trackers:
            findings.append({
                "category": "Third-Party Trackers",
                "issue": "No known third-party trackers detected.",
                "severity": SEVERITY_LOW,
                "passed": True,
            })
        else:
            severity = SEVERITY_HIGH if len(trackers) > 5 else SEVERITY_MEDIUM
            findings.append({
                "category": "Third-Party Trackers",
                "issue": f"{len(trackers)} tracker(s) detected: {', '.join(trackers)}. These require user consent under GDPR/CCPA.",
                "severity": severity,
                "passed": False,
            })

        return findings

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations from scan results.

        Args:
            results: Raw scan results from ComplianceModel

        Returns:
            List of recommendation strings ordered by priority
        """
        recommendations = []

        if not is_detected(results.get("cookie_consent", "")):
            recommendations.append(
                "Implement a cookie consent banner (e.g. using CookieYes, OneTrust, or Cookiebot) "
                "that lets users accept or reject non-essential cookies before they are set."
            )

        if not is_detected(results.get("privacy_policy", "")):
            recommendations.append(
                "Add a visible Privacy Policy page and link it in your site's footer. "
                "It must describe what data you collect, how it is used, and users' rights."
            )

        if not is_detected(results.get("contact_info", "")):
            recommendations.append(
                "Add a Contact page or display an email address so users can exercise their "
                "GDPR/CCPA data rights (access, deletion, opt-out requests)."
            )

        trackers = results.get("trackers", [])
        if trackers:
            recommendations.append(
                f"Review third-party trackers ({', '.join(trackers)}) and ensure each is covered "
                "by your cookie consent mechanism. Block them until consent is granted."
            )
            if len(trackers) > 3:
                recommendations.append(
                    "Consider reducing the number of third-party trackers to minimize compliance risk "
                    "and improve page load performance."
                )

        return recommendations

    def _calculate_tracker_points(self, tracker_count: int) -> int:
        """Calculate tracker points using configured weight and tier multipliers."""
        tracker_weight = Config.SCORING_WEIGHTS["trackers"]
        for max_trackers, multiplier in TRACKER_TIERS:
            if tracker_count <= max_trackers:
                return int(tracker_weight * multiplier)
        return 0
    
