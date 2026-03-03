import sys
from unittest.mock import MagicMock, patch

# Mock dependencies that are missing in the environment
if 'cachetools' not in sys.modules:
    sys.modules['cachetools'] = MagicMock()
if 'openai' not in sys.modules:
    sys.modules['openai'] = MagicMock()
if 'trafilatura' not in sys.modules:
    sys.modules['trafilatura'] = MagicMock()
if 'requests' not in sys.modules:
    sys.modules['requests'] = MagicMock()
if 'requests.adapters' not in sys.modules:
    sys.modules['requests.adapters'] = MagicMock()
if 'urllib3.util.retry' not in sys.modules:
    sys.modules['urllib3.util.retry'] = MagicMock()
if 'bs4' not in sys.modules:
    sys.modules['bs4'] = MagicMock()
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()
if 'streamlit' not in sys.modules:
    sys.modules['streamlit'] = MagicMock()

import unittest
from controllers.compliance_controller import ComplianceController

class TestComplianceControllerBatch(unittest.TestCase):
    def setUp(self):
        # We need to mock the constructor dependencies
        with patch('controllers.compliance_controller.ComplianceModel'), \
             patch('controllers.compliance_controller.OpenAIService'):
            self.controller = ComplianceController()

    @patch('controllers.compliance_controller.ComplianceController.scan_website')
    def test_batch_scan_error_handling(self, mock_scan):
        """Test that batch_scan handles exceptions from scan_website correctly."""
        # Setup mocks to raise an exception
        mock_scan.side_effect = Exception("Test unexpected error")

        urls = ["https://example.com"]
        results = self.controller.batch_scan(urls)

        # Verify the error results structure
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["url"], "https://example.com")
        self.assertEqual(results[0]["error"], "Test unexpected error")
        self.assertEqual(results[0]["score"], 0)
        self.assertEqual(results[0]["grade"], "F")
        self.assertEqual(results[0]["status"], "Error")

    @patch('controllers.compliance_controller.ComplianceController.scan_website')
    def test_batch_scan_mixed_results(self, mock_scan):
        """Test batch_scan with a mix of successful and failed scans."""
        # First call succeeds, second fails
        mock_scan.side_effect = [
            {"score": 85, "grade": "B", "status": "Compliant"},
            Exception("Second URL failed")
        ]

        urls = ["https://success.com", "https://failure.com"]
        results = self.controller.batch_scan(urls)

        self.assertEqual(len(results), 2)

        # Verify success case
        self.assertEqual(results[0]["url"], "https://success.com")
        self.assertEqual(results[0]["score"], 85)
        self.assertEqual(results[0]["status"], "Compliant")

        # Verify failure case
        self.assertEqual(results[1]["url"], "https://failure.com")
        self.assertEqual(results[1]["error"], "Second URL failed")
        self.assertEqual(results[1]["status"], "Error")
        self.assertEqual(results[1]["score"], 0)
        self.assertEqual(results[1]["grade"], "F")

    @patch('controllers.compliance_controller.Config')
    @patch('controllers.compliance_controller.ComplianceController.scan_website')
    def test_batch_scan_limit(self, mock_scan, mock_config):
        """Test that batch_scan respects the BATCH_SCAN_LIMIT."""
        mock_config.BATCH_SCAN_LIMIT = 2
        mock_scan.return_value = {"score": 100}

        urls = ["https://1.com", "https://2.com", "https://3.com"]
        results = self.controller.batch_scan(urls)

        # Should only have 2 results because of the limit
        self.assertEqual(len(results), 2)
        self.assertEqual(mock_scan.call_count, 2)

if __name__ == "__main__":
    unittest.main()
