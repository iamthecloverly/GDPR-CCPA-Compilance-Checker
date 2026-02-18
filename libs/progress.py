"""Progress tracking for long-running operations."""

import time
import logging
from dataclasses import dataclass
from typing import Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class ProgressTracker:
    """Track progress of batch operations."""
    
    total_items: int
    start_time: float = None
    current_item: int = 0
    current_stage: str = ""
    completed: int = 0
    failed: int = 0
    
    def __post_init__(self):
        """Initialize with start time."""
        if self.start_time is None:
            self.start_time = time.time()
    
    def update(self, current: int = None, stage: str = "", completed: int = None, failed: int = None):
        """
        Update progress.
        
        Args:
            current: Current item index
            stage: Current operation stage
            completed: Number of completed items
            failed: Number of failed items
        """
        if current is not None:
            self.current_item = current
        if stage:
            self.current_stage = stage
        if completed is not None:
            self.completed = completed
        if failed is not None:
            self.failed = failed
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get detailed progress information.
        
        Returns:
            Dictionary with progress metrics
        """
        elapsed = time.time() - self.start_time
        current = self.current_item or self.completed
        
        if current == 0:
            rate = 0
            remaining = 0
        else:
            rate = current / elapsed if elapsed > 0 else 0
            remaining = (self.total_items - current) / rate if rate > 0 else 0
        
        return {
            "current": current,
            "total": self.total_items,
            "percentage": min(100, (current / self.total_items * 100)) if self.total_items > 0 else 0,
            "elapsed_seconds": elapsed,
            "estimated_remaining_seconds": remaining,
            "rate_per_second": rate,
            "stage": self.current_stage,
            "completed": self.completed,
            "failed": self.failed
        }
    
    def get_eta_string(self) -> str:
        """Get estimated time of arrival as formatted string."""
        progress = self.get_progress()
        remaining = progress["estimated_remaining_seconds"]
        
        if remaining < 60:
            return f"~{remaining:.0f}s"
        elif remaining < 3600:
            return f"~{remaining / 60:.1f}m"
        else:
            return f"~{remaining / 3600:.1f}h"
    
    def get_status_string(self) -> str:
        """Get human-readable status string."""
        progress = self.get_progress()
        return (
            f"{progress['completed']}/{progress['total']} completed "
            f"| {progress['percentage']:.0f}% | "
            f"ETA: {self.get_eta_string()}"
        )
