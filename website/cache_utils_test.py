"""Tests for cache_utils.py"""

import unittest

from website.cache_utils import cached


class TestCachedDecorator(unittest.TestCase):
    def test_cached_without_app_raises_error(self):
        """Should raise ValueError when app is not provided"""

        @cached('test_key')
        def test_func():
            return "data"

        with self.assertRaises(ValueError) as cm:
            test_func()

        self.assertIn("First argument must be 'app'", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
