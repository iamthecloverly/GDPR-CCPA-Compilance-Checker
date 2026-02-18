"""Formatting utilities for displaying data."""

from datetime import datetime
from typing import Union


def format_score(score: Union[int, float]) -> str:
    """
    Format score with appropriate styling.
    
    Args:
        score: Compliance score (0-100)
        
    Returns:
        Formatted score string
    """
    score_int = int(score)
    if score_int >= 80:
        return f":green[{score_int}]"
    elif score_int >= 60:
        return f":orange[{score_int}]"
    else:
        return f":red[{score_int}]"


def format_grade(grade: str) -> str:
    """
    Format grade letter with color.
    
    Args:
        grade: Letter grade (A-F)
        
    Returns:
        Colored grade string
    """
    if grade == "A":
        return ":green[**A**]"
    elif grade == "B":
        return ":green[**B**]"
    elif grade == "C":
        return ":orange[**C**]"
    elif grade == "D":
        return ":orange[**D**]"
    else:
        return ":red[**F**]"


def format_date(date: datetime) -> str:
    """
    Format date in human-readable format.
    
    Args:
        date: DateTime object
        
    Returns:
        Formatted date string (e.g., "Feb 17, 2026")
    """
    return date.strftime("%b %d, %Y")


def format_time(date: datetime) -> str:
    """
    Format date and time.
    
    Args:
        date: DateTime object
        
    Returns:
        Formatted datetime string
    """
    return date.strftime("%b %d, %Y %H:%M:%S")


def format_tracker_count(count: int) -> str:
    """
    Format tracker count with status indicator.
    
    Args:
        count: Number of trackers
        
    Returns:
        Formatted tracker status
    """
    if count == 0:
        return "✓ No trackers"
    elif count <= 3:
        return f"⚠️  {count} trackers"
    else:
        return f"🔴 {count} trackers"


def format_file_size(size_bytes: int) -> str:
    """
    Format bytes to human-readable size.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_status(status: str) -> str:
    """
    Format status with emoji and color.
    
    Args:
        status: Status string
        
    Returns:
        Formatted status with emoji
    """
    if "Compliant" in status:
        return "✓ :green[Compliant]"
    elif "Improvement" in status:
        return "⚠️  :orange[Needs Improvement]"
    else:
        return "✗ :red[Non-Compliant]"


def format_duration(seconds: float) -> str:
    """
    Format seconds to human-readable duration.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    else:
        return f"{seconds / 3600:.1f}h"
