"""Utility functions for GDPR/CCPA Compliance Checker."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import Config


def create_session() -> requests.Session:
    """
    Create a requests session with retry logic and connection pooling.

    Returns:
        Configured requests.Session instance with HTTPAdapter and Retry strategy.
    """
    session = requests.Session()
    retries = Retry(
        total=Config.MAX_RETRIES,
        backoff_factor=Config.BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session
