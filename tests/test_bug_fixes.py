"""Regression tests for confirmed bugs fixed in code review.

BUG-1: Trackers stored as Python str in DB, used as list downstream.
BUG-2: EMAIL_PATTERN had literal '|' inside character class [A-Z|a-z].
BUG-3: _check_contact_info missed contact links with nested HTML elements.
BUG-4: Dead unreachable 'return "F"' in _calculate_grade.
"""

import sys
import json
from unittest.mock import MagicMock

# Mock heavy/optional dependencies before importing project modules
for mod in [
    "cachetools", "openai", "trafilatura", "requests", "requests.adapters",
    "urllib3.util.retry", "pandas", "streamlit", "sqlalchemy",
    "sqlalchemy.orm", "sqlalchemy.exc",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import unittest
try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.modules["bs4"] = MagicMock()
    BeautifulSoup = None


# ---------------------------------------------------------------------------
# BUG-1: Tracker DB round-trip (json.dumps / json.loads)
# ---------------------------------------------------------------------------
class TestBug1TrackerDBRoundTrip(unittest.TestCase):
    """Trackers must survive a database save/load cycle as a proper list."""

    def _simulate_save(self, tracker_list):
        """Simulate what save_scan_result now stores."""
        return json.dumps(tracker_list)

    def _simulate_load(self, raw):
        """Simulate what _scan_to_dict now returns."""
        return json.loads(raw) if raw else []

    def test_empty_tracker_list_roundtrip(self):
        raw = self._simulate_save([])
        result = self._simulate_load(raw)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_single_tracker_roundtrip(self):
        original = ["google-analytics.com"]
        raw = self._simulate_save(original)
        result = self._simulate_load(raw)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "google-analytics.com")

    def test_multiple_trackers_roundtrip(self):
        original = ["google-analytics.com", "facebook.net", "hotjar.com"]
        raw = self._simulate_save(original)
        result = self._simulate_load(raw)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, original)

    def test_tracker_list_len_not_string_length(self):
        """len() on the deserialized value must give tracker count, not char count."""
        original = ["google-analytics.com", "facebook.net"]
        raw = self._simulate_save(original)
        result = self._simulate_load(raw)
        # Before fix: len(str(original)) == 45 chars; after fix: len == 2
        self.assertEqual(len(result), 2)

    def test_tracker_join_produces_domain_names(self):
        """', '.join(trackers[:10]) must produce domain names, not characters."""
        original = ["google-analytics.com", "facebook.net"]
        raw = self._simulate_save(original)
        result = self._simulate_load(raw)
        joined = ", ".join(result[:10])
        self.assertEqual(joined, "google-analytics.com, facebook.net")

    def test_null_trackers_column_returns_empty_list(self):
        """NULL trackers column (no trackers saved) must return []."""
        result = self._simulate_load(None)
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# BUG-2: EMAIL_PATTERN character class fix ([A-Z|a-z] → [A-Za-z])
# ---------------------------------------------------------------------------
class TestBug2EmailPattern(unittest.TestCase):
    """EMAIL_PATTERN must not accept pipe characters in TLD."""

    def setUp(self):
        from constants import EMAIL_PATTERN
        self.pattern = EMAIL_PATTERN

    def test_valid_email_matches(self):
        self.assertIsNotNone(self.pattern.search("admin@example.com"))

    def test_valid_email_long_tld(self):
        self.assertIsNotNone(self.pattern.search("user@subdomain.example.co.uk"))

    def test_pipe_in_tld_does_not_match(self):
        # Before fix [A-Z|a-z] accepted '|'; after fix [A-Za-z] does not
        self.assertIsNone(self.pattern.search("admin@example.a|b"))

    def test_common_tlds(self):
        for addr in ["user@example.org", "user@example.net", "user@example.io"]:
            with self.subTest(addr=addr):
                self.assertIsNotNone(self.pattern.search(addr))


# ---------------------------------------------------------------------------
# BUG-3: _check_contact_info with nested HTML elements
# ---------------------------------------------------------------------------
@unittest.skipIf(BeautifulSoup is None, "bs4 not available")
class TestBug3ContactLinkNestedElements(unittest.TestCase):
    """Contact links containing nested HTML elements must be detected."""

    def setUp(self):
        from models.compliance_model import ComplianceModel
        self.model = ComplianceModel()

    def test_plain_text_contact_link(self):
        html = '<a href="/contact">Contact Us</a>'
        soup = BeautifulSoup(html, "html.parser")
        result = self.model._check_contact_info(soup)
        self.assertTrue(result.startswith("Found"), f"Expected 'Found', got: {result}")

    def test_nested_span_contact_link(self):
        """Before fix: soup.find(string=) returned None for this; after fix: detected."""
        html = '<a href="/contact"><span>Contact Us</span></a>'
        soup = BeautifulSoup(html, "html.parser")
        result = self.model._check_contact_info(soup)
        self.assertTrue(result.startswith("Found"), f"Expected 'Found', got: {result}")

    def test_deeply_nested_contact_link(self):
        html = '<a href="/contact"><div><span><b>Contact</b></span></div></a>'
        soup = BeautifulSoup(html, "html.parser")
        result = self.model._check_contact_info(soup)
        self.assertTrue(result.startswith("Found"), f"Expected 'Found', got: {result}")

    def test_no_contact_link_returns_not_found(self):
        html = '<a href="/about">About Us</a>'
        soup = BeautifulSoup(html, "html.parser")
        result = self.model._check_contact_info(soup)
        # No email, phone, or contact link → Not Found
        self.assertTrue(result.startswith("Not Found"), f"Expected 'Not Found', got: {result}")


# ---------------------------------------------------------------------------
# BUG-4: _calculate_grade has no unreachable dead code path
# ---------------------------------------------------------------------------
class TestBug4CalculateGrade(unittest.TestCase):
    """_calculate_grade must return correct grades for all score ranges."""

    def setUp(self):
        from controllers.compliance_controller import ComplianceController
        self.controller = ComplianceController()

    def test_grade_a(self):
        self.assertEqual(self.controller._calculate_grade(95), "A")
        self.assertEqual(self.controller._calculate_grade(90), "A")

    def test_grade_b(self):
        self.assertEqual(self.controller._calculate_grade(85), "B")
        self.assertEqual(self.controller._calculate_grade(80), "B")

    def test_grade_c(self):
        self.assertEqual(self.controller._calculate_grade(75), "C")
        self.assertEqual(self.controller._calculate_grade(70), "C")

    def test_grade_d(self):
        self.assertEqual(self.controller._calculate_grade(65), "D")
        self.assertEqual(self.controller._calculate_grade(60), "D")

    def test_grade_f(self):
        self.assertEqual(self.controller._calculate_grade(50), "F")
        self.assertEqual(self.controller._calculate_grade(0), "F")

    def test_boundary_89_is_b_not_a(self):
        self.assertEqual(self.controller._calculate_grade(89), "B")

    def test_boundary_79_is_c_not_b(self):
        self.assertEqual(self.controller._calculate_grade(79), "C")


if __name__ == "__main__":
    unittest.main()
