"""Constants for GDPR/CCPA Compliance Checker."""

import re
from typing import List, Dict

# Status indicators
STATUS_COMPLIANT = "Compliant"
STATUS_NEEDS_IMPROVEMENT = "Needs Improvement"
STATUS_NON_COMPLIANT = "Non-Compliant"

# Grades
GRADES = ["A", "B", "C", "D", "F"]

# Cookie consent keywords
COOKIE_KEYWORDS: List[str] = [
    "cookie",
    "consent",
    "privacy notice",
    "we use cookies",
    "accept cookies",
    "cookie policy",
    "cookie banner"
]

# Privacy policy keywords
PRIVACY_KEYWORDS: List[str] = [
    "privacy",
    "privacy policy",
    "privacy notice",
    "data protection",
    "data privacy",
    "privacy statement",
    "privacy center",
    "data policy",
    "gdpr",
    "ccpa",
    "politica de privacidad",
    "politique de confidentialite",
    "informativa privacy",
    "datenschutz",
    "privacyverklaring",
    "aviso de privacidad",
    "politica de privacidade"
]

# Common privacy policy paths
PRIVACY_POLICY_PATHS: List[str] = [
    "/privacy-policy",
    "/privacy",
    "/privacy-notice",
    "/legal/privacy",
    "/privacy-statement"
]

# Tracking domains
TRACKING_DOMAINS: List[str] = [
    "google-analytics.com",
    "googletagmanager.com",
    "facebook.net",
    "doubleclick.net",
    "scorecardresearch.com",
    "quantserve.com",
    "hotjar.com",
    "mouseflow.com",
    "crazyegg.com",
    "inspectlet.com",
    "hubspot.com",
    "mixpanel.com",
    "segment.com",
    "amplitude.com",
    "heap.io",
    "clarity.ms",
    "fullstory.com",
    "logrocket.com"
]

# Grade thresholds
GRADE_THRESHOLDS: Dict[str, int] = {
    "A": 90,
    "B": 80,
    "C": 70,
    "D": 60,
    "F": 0
}

# Status thresholds
STATUS_THRESHOLDS: Dict[str, int] = {
    STATUS_COMPLIANT: 80,
    STATUS_NEEDS_IMPROVEMENT: 60,
    STATUS_NON_COMPLIANT: 0
}

# Tracker scoring tiers (max tracker count, score multiplier)
TRACKER_TIERS: List[tuple] = [
    (0, 1.0),    # 0 trackers = 100% of tracker points
    (3, 0.75),   # 1-3 trackers = 75%
    (5, 0.5),    # 4-5 trackers = 50%
    (10, 0.25),  # 6-10 trackers = 25%
    # >10 trackers = 0%
]

# HTTP headers
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Regex patterns
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\b\+?\d{1,3}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,9}\b')

# Compiled Keyword Patterns
# These are pre-compiled for efficiency during scanning
COOKIE_PATTERNS = [re.compile(keyword, re.IGNORECASE) for keyword in COOKIE_KEYWORDS]
PRIVACY_PATTERNS = [re.compile(keyword, re.IGNORECASE) for keyword in PRIVACY_KEYWORDS]
