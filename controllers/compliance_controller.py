"""
Compliance Controller Module

This module orchestrates the compliance scanning workflow. It acts as a controller
layer between the UI and lower-level services, handling:

- Compliance scoring based on scan results
- Letter grade assignment
- Compliance status determination
- Batch scanning operations

Classes:
    ComplianceController: Main orchestrator for compliance scans

Architecture:
    The controller follows the MVC pattern and coordinates between:
    - ComplianceModel: Web scraping and analysis
    - OpenAIService: AI-powered policy analysis
    - Scoring Engine: Weighted score calculation

Example:
    >>> controller = ComplianceController()
    >>> results = controller.scan_website('https://example.com')
    >>> print(f"Score: {results['score']}, Grade: {results['grade']}")
"""

from typing import Dict, List, Any
import logging

from models.compliance_model import ComplianceModel
from services.openai_service import OpenAIService
from config import Config
from constants import GRADE_THRESHOLDS
from exceptions import ScanError

logger = logging.getLogger(__name__)


class ComplianceController:
    """
    Controller for handling compliance scanning operations.
    
    Orchestrates the compliance scanning workflow including:
    - Web scraping and analysis
    - Score calculation
    - Grade assignment
    - Batch scanning
    
    Attributes:
        model: ComplianceModel instance for web scraping
        openai_service: OpenAIService instance for AI analysis
    """
    
    def __init__(self):
        """Initialize the controller with model and AI service."""
        self.model = ComplianceModel()
        self.openai_service = OpenAIService()
    
    def scan_website(self, url: str) -> Dict[str, Any]:
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
        try:
            # Fetch and analyze the webpage
            results = self.model.analyze_compliance(url)
            
            # Calculate compliance score
            score = self._calculate_score(results)
            grade = self._calculate_grade(score)
            status = self._determine_status(score)
            
            logger.info(f"Scanned {url}: score={score}, grade={grade}")
            
            return {
                "score": score,
                "grade": grade,
                "status": status,
                "cookie_consent": results.get("cookie_consent", "Not Found"),
                "privacy_policy": results.get("privacy_policy", "Not Found"),
                "contact_info": results.get("contact_info", "Not Found"),
                "trackers": results.get("trackers", []),
                "details": results
            }
            
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
        if "Found" in results.get("cookie_consent", ""):
            score += Config.SCORING_WEIGHTS["cookie_consent"]
        
        # Privacy policy (weighted from config)
        if "Found" in results.get("privacy_policy", ""):
            score += Config.SCORING_WEIGHTS["privacy_policy"]
        
        # Contact information (weighted from config)
        if "Found" in results.get("contact_info", ""):
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
