import unittest
from datetime import datetime, timedelta
from libs.cache import ScanCache
from unittest.mock import patch

class TestScanCache(unittest.TestCase):
    def setUp(self):
        # Initialize a new cache instance for each test
        self.cache = ScanCache(ttl_hours=1)

    def test_set_and_get(self):
        """Test basic set and get functionality."""
        url = "https://example.com"
        results = {"score": 85, "grade": "B"}

        self.cache.set(url, results)
        cached_results = self.cache.get(url)

        self.assertEqual(cached_results, results)
        self.assertIsNone(self.cache.get("https://nonexistent.com"))

    def test_clear_all(self):
        """Test clearing all items from the cache."""
        # Add 2 items
        self.cache.set("https://example.com", {"score": 80})
        self.cache.set("https://test.com", {"score": 70})

        # Check they were added
        stats = self.cache.get_stats()
        self.assertEqual(stats["items"], 2)

        # Clear all
        self.cache.clear_all()

        # Verify cache is empty
        stats = self.cache.get_stats()
        self.assertEqual(stats["items"], 0)
        self.assertEqual(len(self.cache.cache), 0)

    def test_expiration(self):
        """Test that items expire after TTL."""
        url = "https://example.com"
        self.cache.set(url, {"score": 80})

        # Manually expire the entry by reaching into the internal cache
        key = self.cache._get_key(url)
        self.cache.cache[key]["timestamp"] = datetime.now() - timedelta(hours=2)

        # Should return None because it's expired
        self.assertIsNone(self.cache.get(url))
        # Internal cache should also be cleaned up
        self.assertNotIn(key, self.cache.cache)

    def test_clear_expired(self):
        """Test explicit clearing of expired entries."""
        self.cache.set("url1", {"val": 1})
        self.cache.set("url2", {"val": 2})

        # Expire url1
        key1 = self.cache._get_key("url1")
        self.cache.cache[key1]["timestamp"] = datetime.now() - timedelta(hours=2)

        self.cache.clear_expired()

        self.assertEqual(len(self.cache.cache), 1)
        self.assertIn(self.cache._get_key("url2"), self.cache.cache)
        self.assertNotIn(key1, self.cache.cache)

    def test_max_items(self):
        """Test cache eviction when max_items is reached."""
        # Create cache with small limit and large TTL to avoid expiration issues during test
        cache = ScanCache(max_items=2, ttl_hours=100)

        # Add items with distinct timestamps
        with patch('libs.cache.datetime') as mock_datetime:
            # Use a time that is close to now, or just make sure TTL is large enough
            # Actually, if we mock it, we should mock it for both set and get if we want consistency
            base_time = datetime.now()

            mock_datetime.now.return_value = base_time
            cache.set("url1", {"val": 1})

            mock_datetime.now.return_value = base_time + timedelta(seconds=1)
            cache.set("url2", {"val": 2})

            mock_datetime.now.return_value = base_time + timedelta(seconds=2)
            cache.set("url3", {"val": 3})

            # Should only have 2 items
            self.assertEqual(len(cache.cache), 2)
            # url1 should have been evicted as it was the oldest
            self.assertIsNone(cache.get("url1"))
            self.assertIsNotNone(cache.get("url2"))
            self.assertIsNotNone(cache.get("url3"))

    def test_get_stats(self):
        """Test getting cache statistics."""
        self.cache.set("https://example.com", {"score": 80})
        self.cache.set("https://test.com", {"score": 70})

        stats = self.cache.get_stats()
        self.assertEqual(stats["items"], 2)
        self.assertEqual(stats["ttl_hours"], 1.0)
        self.assertIn("https://example.com", stats["urls"])
        self.assertIn("https://test.com", stats["urls"])

if __name__ == "__main__":
    unittest.main()
