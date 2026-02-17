import unittest
from validators import validate_api_key
from exceptions import ValidationError

class TestValidators(unittest.TestCase):
    def test_validate_api_key_valid(self):
        """Test valid API keys."""
        # Default minimum length (20)
        self.assertTrue(validate_api_key("a" * 20))
        self.assertTrue(validate_api_key("ABCDEFGHIJKLMNOPQRST"))
        self.assertTrue(validate_api_key("12345678901234567890"))

        # Longer keys
        self.assertTrue(validate_api_key("a" * 30))

        # Custom minimum length
        self.assertTrue(validate_api_key("abcde12345", min_length=10))

        # Allowed characters: alphanumeric, underscore, hyphen
        self.assertTrue(validate_api_key("API-KEY_1234567890abc"))

    def test_validate_api_key_invalid_length(self):
        """Test API keys that are too short."""
        # Too short for default (20)
        with self.assertRaises(ValidationError) as cm:
            validate_api_key("a" * 19)
        self.assertIn("too short", str(cm.exception))

        # Too short for custom length
        with self.assertRaises(ValidationError) as cm:
            validate_api_key("abc", min_length=5)
        self.assertIn("too short", str(cm.exception))

    def test_validate_api_key_empty(self):
        """Test empty API key."""
        with self.assertRaises(ValidationError) as cm:
            validate_api_key("")
        self.assertIn("cannot be empty", str(cm.exception))

    def test_validate_api_key_none_null(self):
        """Test 'none' or 'null' API keys."""
        for invalid in ["none", "NONE", "None", "null", "NULL", "Null"]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValidationError) as cm:
                    # Need to make sure it's long enough to not trigger length error first
                    # Actually 'none' and 'null' are short (4), so they trigger length error if min_length > 4
                    # To test the specific 'none'/'null' check, we should set min_length <= 4
                    validate_api_key(invalid, min_length=4)
                self.assertIn("cannot be 'none' or 'null'", str(cm.exception))

    def test_validate_api_key_invalid_characters(self):
        """Test API keys with invalid characters."""
        invalid_keys = [
            "api key with spaces 12345",
            "api.key.with.dots.12345",
            "api!@#$123456789012345",
            "api_key_with_newline\n1234"
        ]
        for key in invalid_keys:
            with self.subTest(key=key):
                with self.assertRaises(ValidationError) as cm:
                    validate_api_key(key)
                self.assertIn("contains invalid characters", str(cm.exception))

    def test_validate_api_key_non_string(self):
        """Test non-string inputs."""
        for invalid in [None, 12345678901234567890, [], {}]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValidationError) as cm:
                    validate_api_key(invalid)
                self.assertIn("cannot be empty", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
