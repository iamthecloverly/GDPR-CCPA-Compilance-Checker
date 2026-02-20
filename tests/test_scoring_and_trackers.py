import unittest
from bs4 import BeautifulSoup

from controllers.compliance_controller import ComplianceController
from models.compliance_model import ComplianceModel
from config import Config


class TestScoringAndTrackers(unittest.TestCase):
    def setUp(self):
        self.controller = ComplianceController()
        self.model = ComplianceModel()

    def test_tracker_scoring_tiers(self):
        base_results = {
            "cookie_consent": "Not Found",
            "privacy_policy": "Not Found",
            "contact_info": "Not Found",
        }
        tracker_weight = Config.SCORING_WEIGHTS["trackers"]

        results = {**base_results, "trackers": []}
        self.assertEqual(self.controller._calculate_score(results), tracker_weight)

        results = {**base_results, "trackers": ["a", "b"]}
        self.assertEqual(self.controller._calculate_score(results), int(tracker_weight * 0.75))

        results = {**base_results, "trackers": ["a", "b", "c", "d"]}
        self.assertEqual(self.controller._calculate_score(results), int(tracker_weight * 0.5))

        results = {**base_results, "trackers": ["a"] * 7}
        self.assertEqual(self.controller._calculate_score(results), int(tracker_weight * 0.25))

        results = {**base_results, "trackers": ["a"] * 12}
        self.assertEqual(self.controller._calculate_score(results), 0)

    def test_tracker_detection_third_party_only(self):
        html = """
        <html>
            <head>
                <script src="https://www.google-analytics.com/ga.js"></script>
                <script src="https://analytics.example.com/app.js"></script>
            </head>
            <body>
                <script>
                    var s = "https://connect.facebook.net/en_US/fbevents.js";
                </script>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        trackers = self.model._detect_trackers(soup, "https://example.com")

        self.assertIn("google-analytics.com", trackers)
        self.assertIn("facebook.net", trackers)
        self.assertNotIn("analytics.example.com", trackers)

    def test_tracker_detection_first_party(self):
        html = "<script src=\"https://www.google-analytics.com/ga.js\"></script>"
        soup = BeautifulSoup(html, "html.parser")
        trackers = self.model._detect_trackers(soup, "https://google-analytics.com")
        self.assertEqual(trackers, [])


if __name__ == "__main__":
    unittest.main()
