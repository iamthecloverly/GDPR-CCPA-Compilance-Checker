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

if __name__ == "__main__":
    unittest.main()
