"""Compliance controller orchestrating scanning workflow."""

from typing import Dict, List, Any
import logging
import threading

from models.compliance_model import ComplianceModel
from services.openai_service import OpenAIService
from config import Config
from constants import GRADE_THRESHOLDS
from exceptions import ScanError, NetworkError

logger = logging.getLogger(__name__)


class ComplianceController:
    """Controller for handling compliance scanning operations."""
    
    def __init__(self):
        """Initialize the controller with model and AI service."""
        self.model = ComplianceModel()
        self.openai_service = OpenAIService()
        self._cache_lock = threading.Lock()
        self._cache = {}

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
            logger.info(f"Starting compliance scan for {url}")

            # Perform web scraping and analysis
            results = self.model.analyze_compliance(url)
            
            # Calculate score and metrics
            score = self._calculate_score(results)
            grade = self._calculate_grade(score)
            status = self._determine_status(score)
            score_breakdown = self.get_score_breakdown(results)
            
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
                "findings": results.get("findings", {}),
                "recommendations": results.get("recommendations", []),
                "details": results
            }
            
            # Cache the result
            with self._cache_lock:
                self._cache[url] = response

            return response

        except (ScanError, NetworkError):
            raise
        except Exception as e:
            logger.error(f"Scan failed for {url}: {e}")
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
        if results.get("cookie_consent", "").startswith("Found"):
            score += Config.SCORING_WEIGHTS["cookie_consent"]
        
        # Privacy policy (weighted from config)
        if results.get("privacy_policy", "").startswith("Found"):
            score += Config.SCORING_WEIGHTS["privacy_policy"]
        
        # Contact information (weighted from config)
        if results.get("contact_info", "").startswith("Found"):
            score += Config.SCORING_WEIGHTS["contact_info"]
        
        # Tracker penalty (weighted from config)
        trackers = results.get("trackers", [])
        tracker_weight = Config.SCORING_WEIGHTS["trackers"]
        
        if len(trackers) == 0:
            score += tracker_weight
        elif len(trackers) <= 3:
            score += int(tracker_weight * 0.75)
        elif len(trackers) <= 5:
            score += int(tracker_weight * 0.5)
        elif len(trackers) <= 10:
            score += int(tracker_weight * 0.25)
        # More than 10 trackers = 0 points
        
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
        if results.get("cookie_consent", "").startswith("Found"):
            cookie_points = Config.SCORING_WEIGHTS["cookie_consent"]
        breakdown.append({"Category": "Cookie Consent", "Points": cookie_points})
        
        # Privacy policy points
        privacy_points = 0
        if results.get("privacy_policy", "").startswith("Found"):
            privacy_points = Config.SCORING_WEIGHTS["privacy_policy"]
        breakdown.append({"Category": "Privacy Policy", "Points": privacy_points})
        
        # Contact information points
        contact_points = 0
        if results.get("contact_info", "").startswith("Found"):
            contact_points = Config.SCORING_WEIGHTS["contact_info"]
        breakdown.append({"Category": "Contact Info", "Points": contact_points})
        
        # Tracker points
        trackers = results.get("trackers", [])
        tracker_weight = Config.SCORING_WEIGHTS["trackers"]
        tracker_points = 0
        
        if len(trackers) == 0:
            tracker_points = tracker_weight
        elif len(trackers) <= 3:
            tracker_points = int(tracker_weight * 0.75)
        elif len(trackers) <= 5:
            tracker_points = int(tracker_weight * 0.5)
        elif len(trackers) <= 10:
            tracker_points = int(tracker_weight * 0.25)
        
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
        return "F"
    
    def _determine_status(self, score: int) -> str:
        """
        Determine compliance status based on score.
        
        Args:
            score: Compliance score (0-100)
            
        Returns:
            Status string (Compliant/Needs Improvement/Non-Compliant)
        """
        if score >= 80:
            return "Compliant"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Non-Compliant"
    
    def batch_scan(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scan multiple URLs sequentially.
        
        Args:
            urls: List of URLs to scan
            
        Returns:
            List of scan results dictionaries
        """
        results = []
        for url in urls[:Config.BATCH_SCAN_LIMIT]:  # Respect batch limit
            try:
                result = self.scan_website(url)
                result["url"] = url
                results.append(result)
            except Exception as e:
                logger.error(f"Batch scan error for {url}: {e}")
                results.append({
                    "url": url,
                    "error": str(e),
                    "score": 0,
                    "grade": "F",
                    "status": "Error"
                })
        
        return results
