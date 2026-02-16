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
import asyncio
from datetime import datetime, timedelta
from threading import Lock
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor

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
        self._cache_ttl = timedelta(hours=1)
        self._cache = TTLCache(maxsize=1000, ttl=self._cache_ttl.total_seconds())
        self._cache_lock = Lock()
    
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
            
            # Construct response
            response = {
                "score": score,
                "grade": grade,
                "status": status,
                "cookie_consent": results.get("cookie_consent", "Not Found"),
                "privacy_policy": results.get("privacy_policy", "Not Found"),
                "ccpa_compliance": results.get("ccpa_compliance", "Not Found"),
                "contact_info": results.get("contact_info", "Not Found"),
                "trackers": results.get("trackers", []),
                "details": results
            }
            
            # Cache the result
            with self._cache_lock:
                self._cache[url] = response

            return response

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

        # CCPA compliance (weighted from config)
        if results.get("ccpa_compliance", "").startswith("Found"):
            score += Config.SCORING_WEIGHTS.get("ccpa_compliance", 0)
        
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
        Get detailed score breakdown for UI visualization.

        Args:
            results: Scan results dictionary

        Returns:
            List of dictionaries containing category, points, and max points
        """
        breakdown_data = []

        # Cookie Consent
        cookie_score = Config.SCORING_WEIGHTS["cookie_consent"] if results.get("cookie_consent", "").startswith("Found") else 0
        breakdown_data.append({
            "Category": "Cookie Consent",
            "Points": cookie_score,
            "Max": Config.SCORING_WEIGHTS["cookie_consent"]
        })

        # Privacy Policy
        privacy_score = Config.SCORING_WEIGHTS["privacy_policy"] if results.get("privacy_policy", "").startswith("Found") else 0
        breakdown_data.append({
            "Category": "Privacy Policy",
            "Points": privacy_score,
            "Max": Config.SCORING_WEIGHTS["privacy_policy"]
        })

        # CCPA
        ccpa_max = Config.SCORING_WEIGHTS.get("ccpa_compliance", 0)
        ccpa_score = ccpa_max if results.get("ccpa_compliance", "").startswith("Found") else 0
        breakdown_data.append({
            "Category": "CCPA Compliance",
            "Points": ccpa_score,
            "Max": ccpa_max
        })

        # Contact Info
        contact_score = Config.SCORING_WEIGHTS["contact_info"] if results.get("contact_info", "").startswith("Found") else 0
        breakdown_data.append({
            "Category": "Contact Info",
            "Points": contact_score,
            "Max": Config.SCORING_WEIGHTS["contact_info"]
        })

        # Trackers
        tracker_max = Config.SCORING_WEIGHTS["trackers"]
        tracker_count = len(results.get("trackers", []))
        tracker_score = 0

        if tracker_count == 0:
            tracker_score = tracker_max
        elif tracker_count <= 3:
            tracker_score = int(tracker_max * 0.75)
        elif tracker_count <= 5:
            tracker_score = int(tracker_max * 0.5)
        elif tracker_count <= 10:
            tracker_score = int(tracker_max * 0.25)

        breakdown_data.append({
            "Category": "Tracker Safety",
            "Points": tracker_score,
            "Max": tracker_max
        })

        return breakdown_data

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
        Scan multiple URLs (sync wrapper for async implementation).
        
        Args:
            urls: List of URLs to scan
            
        Returns:
            List of scan results dictionaries
        """
        # Run async batch scan
        try:
            # Check if there's already a running loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # If we're already in a loop, run the async work in a separate thread
                # because we cannot nest asyncio.run() or use run_until_complete on a running loop
                with ThreadPoolExecutor(max_workers=1) as executor:
                    # Note: We must pass a callable to executor.submit, not the coroutine object directly
                    # However, asyncio.run expects a coroutine. So we define a helper.
                    def run_async_in_thread():
                        return asyncio.run(self._async_batch_scan(urls))

                    future = executor.submit(run_async_in_thread)
                    return future.result()
            else:
                return asyncio.run(self._async_batch_scan(urls))

        except Exception as e:
            logger.error(f"Async batch scan failed, falling back to sync: {e}")
            # Fallback to sync
            results = []
            for url in urls[:Config.BATCH_SCAN_LIMIT]:
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

    async def _async_batch_scan(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Asynchronously scan multiple URLs.
        
        Args:
            urls: List of URLs to scan

        Returns:
            List of scan results dictionaries
        """
        limited_urls = urls[:Config.BATCH_SCAN_LIMIT]
        tasks = [self._async_scan_wrapper(url) for url in limited_urls]
        return await asyncio.gather(*tasks)

    async def _async_scan_wrapper(self, url: str) -> Dict[str, Any]:
        """
        Async wrapper for single URL scan.
        """
        try:
            # Offload the blocking sync call to a thread
            result = await asyncio.to_thread(self.scan_website, url)
            result["url"] = url
            return result
        except Exception as e:
            logger.error(f"Async scan error for {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "score": 0,
                "grade": "F",
                "status": "Error"
            }
