from models.compliance_model import ComplianceModel
from services.openai_service import OpenAIService

class ComplianceController:
    """Controller for handling compliance scanning operations"""
    
    def __init__(self):
        self.model = ComplianceModel()
        self.openai_service = OpenAIService()
    
    def scan_website(self, url):
        """
        Perform a comprehensive compliance scan on a website
        
        Args:
            url: The website URL to scan
            
        Returns:
            dict: Scan results with score, grade, and details
        """
        try:
            # Fetch and analyze the webpage
            results = self.model.analyze_compliance(url)
            
            # Calculate compliance score
            score = self._calculate_score(results)
            grade = self._calculate_grade(score)
            status = self._determine_status(score)
            
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
            raise Exception(f"Scan failed: {str(e)}")
    
    def _calculate_score(self, results):
        """Calculate compliance score based on findings"""
        score = 0
        
        # Cookie consent (30 points)
        if "Found" in results.get("cookie_consent", ""):
            score += 30
        
        # Privacy policy (30 points)
        if "Found" in results.get("privacy_policy", ""):
            score += 30
        
        # Contact information (20 points)
        if "Found" in results.get("contact_info", ""):
            score += 20
        
        # Tracker penalty (up to 20 points deduction)
        trackers = results.get("trackers", [])
        if len(trackers) == 0:
            score += 20
        elif len(trackers) <= 3:
            score += 15
        elif len(trackers) <= 5:
            score += 10
        elif len(trackers) <= 10:
            score += 5
        # More than 10 trackers = 0 points
        
        return min(100, max(0, score))
    
    def _calculate_grade(self, score):
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _determine_status(self, score):
        """Determine compliance status"""
        if score >= 80:
            return "Compliant"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Non-Compliant"
    
    def batch_scan(self, urls):
        """
        Scan multiple URLs
        
        Args:
            urls: List of URLs to scan
            
        Returns:
            list: List of scan results
        """
        results = []
        for url in urls:
            try:
                result = self.scan_website(url)
                result["url"] = url
                results.append(result)
            except Exception as e:
                results.append({
                    "url": url,
                    "error": str(e),
                    "score": 0,
                    "grade": "F",
                    "status": "Error"
                })
        
        return results
