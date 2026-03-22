"""Session-scoped rate limiting for scan operations."""

from datetime import datetime, timedelta
from typing import Callable, Tuple
import streamlit as st


def _prune(timestamps: list, window: timedelta) -> list:
    """Return only timestamps within the rolling window."""
    cutoff = datetime.now() - window
    return [t for t in timestamps if t > cutoff]


def _check_rate_limit(
    key: str,
    window: timedelta,
    limit: int,
    make_msg: Callable[[int], str],
) -> Tuple[bool, str]:
    """
    Generic rolling-window rate limiter backed by st.session_state.

    Args:
        key: Session state key for storing timestamps.
        window: Rolling time window.
        limit: Maximum allowed calls within the window.
        make_msg: Called with remaining seconds when limit is exceeded; returns error message.

    Returns:
        (allowed, message)
    """
    if key not in st.session_state:
        st.session_state[key] = []

    st.session_state[key] = _prune(st.session_state[key], window)

    if len(st.session_state[key]) >= limit:
        oldest = st.session_state[key][0]
        wait_secs = int((oldest + window - datetime.now()).total_seconds()) + 1
        return False, make_msg(wait_secs)

    st.session_state[key].append(datetime.now())
    return True, ""


def check_scan_rate_limit(limit_per_minute: int) -> Tuple[bool, str]:
    """
    Check whether the current session may trigger a single scan.

    Uses a 1-minute rolling window.

    Args:
        limit_per_minute: Maximum scans allowed per minute.

    Returns:
        (allowed, message) — if allowed is False, message explains the cooldown.
    """
    return _check_rate_limit(
        key="_scan_timestamps",
        window=timedelta(minutes=1),
        limit=limit_per_minute,
        make_msg=lambda secs: (
            f"Rate limit reached — you can run up to {limit_per_minute} scans per minute. "
            f"Please wait {secs}s before scanning again."
        ),
    )


def check_batch_rate_limit(limit_per_hour: int) -> Tuple[bool, str]:
    """
    Check whether the current session may trigger a batch scan.

    Uses a 1-hour rolling window.

    Args:
        limit_per_hour: Maximum batch scans allowed per hour.

    Returns:
        (allowed, message) — if allowed is False, message explains the cooldown.
    """
    return _check_rate_limit(
        key="_batch_timestamps",
        window=timedelta(hours=1),
        limit=limit_per_hour,
        make_msg=lambda secs: (
            f"Rate limit reached — you can run up to {limit_per_hour} batch scans per hour. "
            f"Please wait {max(1, secs // 60)} minute(s) before trying again."
        ),
    )
