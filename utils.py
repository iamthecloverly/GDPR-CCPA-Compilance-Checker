"""Utility functions for GDPR/CCPA Compliance Checker."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin, urlparse
from typing import Optional, Dict, Any

from config import Config
from validators import validate_url


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


def safe_request(
    session: requests.Session,
    method: str,
    url: str,
    max_redirects: int = 5,
    **kwargs: Any
) -> requests.Response:
    """
    Perform a request while manually following and validating redirects to prevent SSRF.

    Args:
        session: The requests Session object to use
        method: HTTP method (GET, POST, etc.)
        url: Initial URL
        max_redirects: Maximum number of redirects to follow
        **kwargs: Additional arguments to pass to session.request

    Returns:
        requests.Response: The final HTTP response

    Raises:
        InvalidURLError: If any URL in the redirect chain is unsafe
        requests.exceptions.TooManyRedirects: If the redirect limit is exceeded
        requests.exceptions.RequestException: For other network errors
    """
    redirect_count = 0
    # Security: Validate the initial URL before following it
    _, current_url = validate_url(url)

    # Keep track of initial hostname for header sanitization
    initial_hostname = urlparse(current_url).hostname

    while redirect_count <= max_redirects:
        # Ensure allow_redirects is always False for manual handling
        kwargs["allow_redirects"] = False

        response = session.request(method, current_url, **kwargs)

        # Manual redirect handling (status codes 301, 302, 303, 307, 308)
        if response.is_redirect or response.status_code in {301, 302, 303, 307, 308}:
            redirect_count += 1
            if redirect_count > max_redirects:
                raise requests.exceptions.TooManyRedirects("Too many redirects")

            next_url = response.headers.get("Location")
            if not next_url:
                return response

            # Resolve relative URLs
            next_url = urljoin(current_url, next_url)

            # Security: Validate the redirect URL before following it
            _, current_url = validate_url(next_url)

            # Security: Sanitize headers if redirecting to a different host
            next_hostname = urlparse(current_url).hostname
            if next_hostname != initial_hostname:
                # Strip sensitive headers
                for header in ["Authorization", "Proxy-Authorization", "Cookie"]:
                    kwargs.get("headers", {}).pop(header, None)

            # For 303 See Other, the method should change to GET
            if response.status_code == 303:
                method = "GET"
                # Also strip body if it was a POST
                kwargs.pop("data", None)
                kwargs.pop("json", None)

            continue

        return response

    raise requests.exceptions.TooManyRedirects("Too many redirects")
