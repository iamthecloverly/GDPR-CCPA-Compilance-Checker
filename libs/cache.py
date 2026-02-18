"""Simple client-side caching system for scan results."""

import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ScanCache:
    """Simple time-based cache for scan results."""
    
    def __init__(self, ttl_hours: int = 24):
        """
        Initialize cache.
        
        Args:
            ttl_hours: Time-to-live in hours (default: 24)
        """
        self.cache: Dict[str, Dict] = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_key(self, url: str) -> str:
        """Generate cache key from URL."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result for URL.
        
        Args:
            url: Website URL
            
        Returns:
            Cached results or None if not found/expired
        """
        key = self._get_key(url)
        if key not in self.cache:
            return None
        
        cached_data = self.cache[key]
        if datetime.now() - cached_data["timestamp"] > self.ttl:
            del self.cache[key]
            return None
        
        logger.info(f"Cache hit for {url}")
        return cached_data["results"]
    
    def set(self, url: str, results: Dict[str, Any]) -> None:
        """
        Store result in cache.
        
        Args:
            url: Website URL
            results: Scan results to cache
        """
        key = self._get_key(url)
        self.cache[key] = {
            "results": results,
            "timestamp": datetime.now(),
            "url": url
        }
        logger.info(f"Cached result for {url}")
    
    def clear_expired(self) -> None:
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_keys = [
            k for k, v in self.cache.items()
            if now - v["timestamp"] > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def clear_all(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
        logger.info("Cleared entire cache")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self.clear_expired()
        return {
            "items": len(self.cache),
            "ttl_hours": self.ttl.total_seconds() / 3600,
            "urls": [v["url"] for v in self.cache.values()]
        }


# Global cache instance
_scan_cache = ScanCache(ttl_hours=24)


def get_scan_cache() -> ScanCache:
    """Get the global scan cache instance."""
    return _scan_cache
