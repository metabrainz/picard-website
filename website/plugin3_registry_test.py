"""Tests for plugin3_registry.py ETag caching functionality"""

import unittest
from unittest.mock import MagicMock, Mock, patch
from urllib.error import HTTPError

from website.plugin3_registry import RegistryCacheEntry, load_registry_toml


class TestRegistryCacheEntry(unittest.TestCase):
    def test_cache_entry_stores_etag(self):
        entry = RegistryCacheEntry("test content", "etag-123")
        self.assertEqual(entry.registry, "test content")
        self.assertEqual(entry.etag, "etag-123")
        self.assertIsNotNone(entry.timestamp)

    def test_cache_entry_without_etag(self):
        entry = RegistryCacheEntry("test content")
        self.assertEqual(entry.registry, "test content")
        self.assertIsNone(entry.etag)

    def test_is_valid_within_timeout(self):
        entry = RegistryCacheEntry("test")
        self.assertTrue(entry.is_valid(3600))

    def test_is_valid_expired(self):
        entry = RegistryCacheEntry("test")
        entry.timestamp = 0
        self.assertFalse(entry.is_valid(3600))


class TestLoadRegistryToml(unittest.TestCase):
    def setUp(self):
        self.app = Mock()
        self.app.config = {
            'PLUGINS_V3_REGISTRY_URL': 'https://example.com/plugins.toml',
            'PLUGINS_V3_REGISTRY_CACHE_TIMEOUT': 300,
            'PLUGINS_V3_REGISTRY_REQUEST_TIMEOUT': 5,
        }
        self.app.cache = Mock()
        self.app.logger = Mock()

    @patch('website.plugin3_registry.urlopen')
    def test_fresh_cache_returns_without_request(self, mock_urlopen):
        """Should return cached data without making HTTP request if cache is fresh"""
        cache_entry = RegistryCacheEntry("cached content", "etag-old")
        self.app.cache.get.return_value = cache_entry

        result = load_registry_toml(self.app)

        self.assertEqual(result, "cached content")
        mock_urlopen.assert_not_called()

    @patch('website.plugin3_registry.urlopen')
    def test_stale_cache_makes_conditional_request(self, mock_urlopen):
        """Should send If-None-Match header when cache is stale"""
        cache_entry = RegistryCacheEntry("[plugins]\n", "etag-123")
        cache_entry.timestamp = 0  # Make it stale
        self.app.cache.get.return_value = cache_entry

        mock_response = MagicMock()
        mock_response.read.return_value = b"[plugins]\n[[plugins.plugin]]\nid = \"test\"\n"
        mock_response.headers.get.return_value = "etag-456"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        result = load_registry_toml(self.app)

        # Verify If-None-Match header was added
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        self.assertEqual(request.get_header('If-none-match'), 'etag-123')
        self.assertEqual(result, "[plugins]\n[[plugins.plugin]]\nid = \"test\"\n")

    @patch('website.plugin3_registry.urlopen')
    def test_304_not_modified_refreshes_timestamp(self, mock_urlopen):
        """Should refresh timestamp and keep old content on 304 response"""
        old_timestamp = 100
        cache_entry = RegistryCacheEntry("old content", "etag-123")
        cache_entry.timestamp = old_timestamp
        self.app.cache.get.return_value = cache_entry

        # Simulate 304 Not Modified
        mock_urlopen.side_effect = HTTPError(None, 304, 'Not Modified', {}, None)

        result = load_registry_toml(self.app)

        self.assertEqual(result, "old content")
        # Verify timestamp was updated
        saved_entry = self.app.cache.set.call_args[0][1]
        self.assertGreater(saved_entry.timestamp, old_timestamp)
        self.assertEqual(saved_entry.etag, "etag-123")

    @patch('website.plugin3_registry.urlopen')
    def test_404_returns_stale_cache(self, mock_urlopen):
        """Should return stale cache on 404 (migration scenario)"""
        cache_entry = RegistryCacheEntry("stale content", "etag-old")
        cache_entry.timestamp = 0
        self.app.cache.get.return_value = cache_entry

        mock_urlopen.side_effect = HTTPError(None, 404, 'Not Found', {}, None)

        result = load_registry_toml(self.app)

        self.assertEqual(result, "stale content")
        self.app.logger.warning.assert_called_once()

    @patch('website.plugin3_registry.urlopen')
    def test_network_error_returns_stale_cache(self, mock_urlopen):
        """Should return stale cache on network errors"""
        cache_entry = RegistryCacheEntry("stale content", "etag-old")
        cache_entry.timestamp = 0
        self.app.cache.get.return_value = cache_entry

        mock_urlopen.side_effect = Exception("Network error")

        result = load_registry_toml(self.app)

        self.assertEqual(result, "stale content")
        self.app.logger.error.assert_called_once()

    @patch('website.plugin3_registry.urlopen')
    def test_no_cache_and_error_returns_none(self, mock_urlopen):
        """Should return None if no cache exists and request fails"""
        self.app.cache.get.return_value = None
        mock_urlopen.side_effect = HTTPError(None, 500, 'Server Error', {}, None)

        result = load_registry_toml(self.app)

        self.assertIsNone(result)

    @patch('website.plugin3_registry.urlopen')
    def test_successful_fetch_stores_etag(self, mock_urlopen):
        """Should store ETag from successful response"""
        self.app.cache.get.return_value = None

        mock_response = MagicMock()
        mock_response.read.return_value = b"[plugins]\n"
        mock_response.headers.get.return_value = "etag-new-123"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        result = load_registry_toml(self.app)

        self.assertEqual(result, "[plugins]\n")
        saved_entry = self.app.cache.set.call_args[0][1]
        self.assertEqual(saved_entry.etag, "etag-new-123")
        self.assertEqual(saved_entry.registry, "[plugins]\n")

    @patch('website.plugin3_registry.urlopen')
    def test_invalid_toml_returns_stale_cache(self, mock_urlopen):
        """Should reject invalid TOML and return stale cache"""
        cache_entry = RegistryCacheEntry("[plugins]\n", "etag-old")
        cache_entry.timestamp = 0
        self.app.cache.get.return_value = cache_entry

        mock_response = MagicMock()
        mock_response.read.return_value = b"invalid toml {{"
        mock_response.headers.get.return_value = "etag-new"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        result = load_registry_toml(self.app)

        self.assertEqual(result, "[plugins]\n")  # Returns stale cache
        self.app.logger.error.assert_called_once()
        self.assertIn('not valid TOML', self.app.logger.error.call_args[0][0])

    @patch('website.plugin3_registry.urlopen')
    def test_invalid_toml_no_cache_returns_none(self, mock_urlopen):
        """Should return None if TOML is invalid and no cache exists"""
        self.app.cache.get.return_value = None

        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>Error</html>"
        mock_response.headers.get.return_value = "etag-new"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        result = load_registry_toml(self.app)

        self.assertIsNone(result)
        self.app.logger.error.assert_called_once()

    @patch('website.plugin3_registry.urlopen')
    def test_unicode_decode_error_returns_stale_cache(self, mock_urlopen):
        """Should handle decode errors gracefully"""
        cache_entry = RegistryCacheEntry("[plugins]\n", "etag-old")
        cache_entry.timestamp = 0
        self.app.cache.get.return_value = cache_entry

        mock_response = MagicMock()
        mock_response.read.return_value.decode.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        result = load_registry_toml(self.app)

        self.assertEqual(result, "[plugins]\n")
        self.app.logger.error.assert_called_once()

    @patch('website.plugin3_registry.urlopen')
    def test_304_with_none_cache_defensive(self, mock_urlopen):
        """Should handle impossible 304 with None cache_entry defensively"""
        self.app.cache.get.return_value = None

        # This shouldn't happen in practice, but test defensive code
        mock_urlopen.side_effect = HTTPError(None, 304, 'Not Modified', {}, None)

        result = load_registry_toml(self.app)

        self.assertIsNone(result)
        self.app.logger.error.assert_called_once()
        self.assertIn('304 but cache_entry is None', self.app.logger.error.call_args[0][0])

    def test_load_plugin_list_skips_invalid_plugins(self):
        """Should skip plugins without id or name"""
        from unittest.mock import patch
        from website.plugin3_registry import load_plugin_list

        # Mock registry with invalid plugins
        invalid_toml = "[[plugins]]\nid = \"valid\"\nname = \"Valid Plugin\"\n\n[[plugins]]\nname = \"No ID\"\n\n[[plugins]]\nid = \"no-name\"\n"

        # Need to bypass cache
        self.app.cache.get.return_value = None
        with patch('website.plugin3_registry.load_registry_toml', return_value=invalid_toml):
            result = load_plugin_list(self.app, force_refresh=True)

        # Should only have the valid plugin
        self.assertEqual(len(result), 1)
        self.assertIn('valid', result)
        self.assertNotIn('no-name', result)


if __name__ == '__main__':
    unittest.main()
