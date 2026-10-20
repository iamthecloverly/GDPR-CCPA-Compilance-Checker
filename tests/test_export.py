import unittest
from libs.export import format_full_scan_text

class TestExport(unittest.TestCase):
    def test_format_full_scan_text_empty_findings(self):
        # Scenario A: findings key is empty
        scan_data_empty = {
            "url": "https://example.com",
            "scan_date": "2023-10-01",
            "overall_score": 100.0,
            "grade": "A",
            "status": "Success",
            "findings": {}
        }

        # Should not raise exception
        result_empty = format_full_scan_text(scan_data_empty)
        self.assertIn("No findings recorded", result_empty)

        # Scenario B: findings key is missing
        scan_data_missing = {
            "url": "https://example.com",
            "scan_date": "2023-10-01",
            "overall_score": 100.0,
            "grade": "A",
            "status": "Success"
        }

        # Should not raise exception
        result_missing = format_full_scan_text(scan_data_missing)
        self.assertIn("No findings recorded", result_missing)

    def test_format_full_scan_text_current_findings(self):
        result = format_full_scan_text({
            "score": 70,
            "findings": [
                {
                    "category": "Cookie Consent",
                    "issue": "Cookie consent banner detected.",
                    "severity": "low",
                    "passed": True,
                },
                {
                    "category": "Privacy Policy",
                    "issue": "No privacy policy link detected.",
                    "severity": "high",
                    "passed": False,
                },
            ],
        })

        self.assertIn("Cookie Consent", result)
        self.assertIn("Cookie consent banner detected.", result)
        self.assertIn("PASS", result)
        self.assertIn("Privacy Policy", result)
        self.assertIn("No privacy policy link detected.", result)
        self.assertIn("FAIL", result)
        self.assertIn("high", result)

    def test_format_full_scan_text_legacy_findings(self):
        result = format_full_scan_text({
            "findings": {
                "Privacy Policy": ["Missing link"],
                "Contact Information": 2,
            },
        })

        self.assertIn("Privacy Policy: 1 issue(s)", result)
        self.assertIn("Missing link", result)
        self.assertIn("Contact Information: 2 issue(s)", result)

    def test_format_full_scan_text_score_fallback_preserves_zero(self):
        for scan, expected in [
            ({"score": 85}, "85.0%"),
            ({"overall_score": 75}, "75.0%"),
            ({"score": 0, "overall_score": 95}, "0.0%"),
        ]:
            with self.subTest(scan=scan):
                result = format_full_scan_text(scan)
                self.assertIn(f"Overall Score: {expected}", result)

if __name__ == "__main__":
    unittest.main()
