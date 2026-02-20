import sys
from unittest.mock import MagicMock, patch

# Mock dependencies that are missing in the environment
sys.modules['openai'] = MagicMock()
sys.modules['trafilatura'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['requests.adapters'] = MagicMock()
sys.modules['urllib3.util.retry'] = MagicMock()
sys.modules['bs4'] = MagicMock()

import unittest
from validators import validate_url
from exceptions import InvalidURLError
from services.openai_service import OpenAIService

class TestSSRFProtection(unittest.TestCase):
    def test_validate_url_ssrf_protection(self):
        # Forbidden hosts
        forbidden_urls = [
            "http://localhost",
            "http://127.0.0.1",
            "http://169.254.169.254",
            "http://10.0.0.1",
            "http://172.16.0.1",
            "http://192.168.1.1",
            "http://[::1]",
            "https://localhost:8080",
            "http://0.0.0.0",
        ]

        for url in forbidden_urls:
            with self.subTest(url=url):
                with self.assertRaises(InvalidURLError) as cm:
                    validate_url(url)
                self.assertIn("not allowed", str(cm.exception))

    def test_validate_url_legitimate_urls(self):
        # Legitimate hosts
        legitimate_urls = [
            "https://google.com",
            "http://example.org/privacy",
            "https://8.8.8.8", # Public IP
            "https://1.1.1.1", # Public IP
        ]

        for url in legitimate_urls:
            with self.subTest(url=url):
                is_valid, normalized = validate_url(url)
                self.assertTrue(is_valid)
                self.assertTrue(normalized.startswith("http"))

    @patch("services.openai_service.requests.Session")
    @patch("services.openai_service.BeautifulSoup")
    def test_openai_service_ssrf_prevention(self, mock_soup_cls, mock_session_cls):
        # This test ensures that OpenAIService correctly uses validation
        service = OpenAIService()
        mock_session = mock_session_cls.return_value
        service.session = mock_session

        # Mock homepage response that returns a link to an internal IP
        home_response = MagicMock()
        home_response.status_code = 200
        home_response.headers = {"Content-Type": "text/html", "Content-Length": "64"}
        home_response.iter_content.return_value = [b"<html><a href='http://169.254.169.254/'>Privacy</a></html>"]

        # We need to mock BeautifulSoup behavior
        mock_link = MagicMock()
        mock_link.get_text.return_value = "Privacy Policy"
        mock_link.__getitem__.return_value = "http://169.254.169.254/latest/meta-data/"

        mock_soup = mock_soup_cls.return_value
        mock_soup.find_all.return_value = [mock_link]

        # Setup session.get to return home_response
        mock_session.get.return_value = home_response

        # Call _fetch_privacy_policy
        policy_text = service._fetch_privacy_policy("https://example.com")

        # It should return None because the policy_url is unsafe
        self.assertIsNone(policy_text)

        # Session.get should only have been called once (for the homepage)
        # and NOT for the internal IP
        calls = mock_session.get.call_args_list
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0][0], "https://example.com")

if __name__ == "__main__":
    unittest.main()
