import sys
from unittest.mock import MagicMock, patch

# Mock dependencies that are missing in the environment
# We only mock them if they are not already available
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

import unittest
from services.openai_service import OpenAIService

class TestOpenAIService(unittest.TestCase):
    def setUp(self):
        with patch('config.Config.OPENAI_API_KEY', 'test_key'):
            self.service = OpenAIService()

    @patch('services.openai_service.requests.Session')
    @patch('services.openai_service.BeautifulSoup')
    @patch('services.openai_service.trafilatura.extract')
    def test_fetch_privacy_policy_link_finding(self, mock_extract, mock_soup_cls, mock_session_cls):
        # Mock session and response
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}

        # Scenario: Link text doesn't contain "privacy", but href does.
        html_content = "<html><body><a href='/data-protection-policy'>Data Protection</a></body></html>"
        mock_response.content = html_content.encode('utf-8')
        mock_response.text = html_content

        # Setup get calls: first for homepage, second for policy page
        policy_response = MagicMock()
        policy_response.status_code = 200
        policy_response.text = "This is the Data Protection Policy content."
        policy_response.content = policy_response.text.encode('utf-8')
        policy_response.headers = {'Content-Type': 'text/html'}

        mock_session.get.side_effect = [mock_response, policy_response]
        mock_session.head.return_value = MagicMock(status_code=404)

        # Mock BeautifulSoup to find the link
        mock_link = MagicMock()
        mock_link.get_text.return_value = "Data Protection"
        mock_link.__getitem__.return_value = "/data-protection-policy"
        mock_soup = mock_soup_cls.return_value
        mock_soup.find_all.return_value = [mock_link]

        # Mock trafilatura to return the policy content
        mock_extract.return_value = "This is the Data Protection Policy content."

        self.service.session = mock_session

        policy_text = self.service._fetch_privacy_policy("https://example.com")

        self.assertIsNotNone(policy_text)
        self.assertIn("Data Protection Policy content", policy_text)

        # Verify calls
        calls = mock_session.get.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0][0], "https://example.com")
        self.assertTrue(calls[1][0][0].endswith("/data-protection-policy"))

    @patch('services.openai_service.requests.Session')
    @patch('services.openai_service.trafilatura.extract')
    @patch('services.openai_service.BeautifulSoup')
    def test_fetch_privacy_policy_trafilatura(self, mock_soup_cls, mock_extract, mock_session_cls):
        mock_session = mock_session_cls.return_value

        # Homepage has clear link
        home_response = MagicMock()
        home_response.status_code = 200
        home_response.headers = {'Content-Type': 'text/html'}
        home_response.content = b'<html><a href="/privacy">Privacy</a></html>'

        # Policy page
        policy_response = MagicMock()
        policy_response.status_code = 200
        policy_response.text = "<html><body><p>Privacy Policy Content</p></body></html>"
        policy_response.headers = {'Content-Type': 'text/html'}

        mock_session.get.side_effect = [home_response, policy_response]

        # Mock BeautifulSoup
        mock_link = MagicMock()
        mock_link.get_text.return_value = "Privacy"
        mock_link.__getitem__.return_value = "/privacy"
        mock_soup = mock_soup_cls.return_value
        mock_soup.find_all.return_value = [mock_link]

        # Mock trafilatura extraction
        mock_extract.return_value = "Extracted Privacy Policy Content"

        self.service.session = mock_session

        policy_text = self.service._fetch_privacy_policy("https://example.com")

        self.assertEqual(policy_text, "Extracted Privacy Policy Content")
        mock_extract.assert_called_with(policy_response.text)

if __name__ == '__main__':
    unittest.main()
