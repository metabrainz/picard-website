from collections import OrderedDict
from unittest.mock import patch

from website.frontend.testing import FrontendTestCase
from website.frontend.views.plugins import _load_v3_plugins, _localized


class LocalizedHelperTest(FrontendTestCase):
    """Tests for the _localized translation-picking helper"""

    def test_exact_language_match(self):
        self.assertEqual(_localized({'de': 'Hallo', 'fr': 'Salut'}, 'Hello', 'de'), 'Hallo')

    def test_territory_falls_back_to_base_language(self):
        self.assertEqual(_localized({'de': 'Hallo'}, 'Hello', 'de_AT'), 'Hallo')

    def test_missing_language_falls_back_to_default(self):
        self.assertEqual(_localized({'de': 'Hallo'}, 'Hello', 'it'), 'Hello')

    def test_empty_translation_falls_back_to_default(self):
        self.assertEqual(_localized({'de': ''}, 'Hello', 'de'), 'Hello')

    def test_empty_base_translation_falls_back_to_default(self):
        self.assertEqual(_localized({'de': ''}, 'Hello', 'de_AT'), 'Hello')

    def test_empty_i18n_returns_default(self):
        self.assertEqual(_localized({}, 'Hello', 'de'), 'Hello')

    def test_none_lang_returns_default(self):
        self.assertEqual(_localized({'de': 'Hallo'}, 'Hello', None), 'Hello')


class LoadV3PluginsLocalizationTest(FrontendTestCase):
    """Tests that _load_v3_plugins resolves localized name/description"""

    _REGISTRY = OrderedDict({
        'aad': {
            'name': 'Additional Artists Details',
            'description': 'English description.',
            'author': 'Bob Swift',
            'version': '',
            'git_url': 'https://example/aad',
            'name_i18n': {'de': 'Weitere Details', 'fr': 'Détails supplémentaires'},
            'description_i18n': {'de': 'Deutsche Beschreibung.', 'fr': 'Description française.'},
        },
    })

    def _load_for_lang(self, lang):
        with patch('website.frontend.views.plugins.load_plugin_list', return_value=self._REGISTRY), \
                patch('website.frontend.views.plugins.get_locale', return_value=lang):
            with self.app.test_request_context('/plugins/'):
                return _load_v3_plugins()

    def test_german_localization(self):
        plugins = self._load_for_lang('de')
        self.assertEqual(plugins['aad']['name'], 'Weitere Details')
        self.assertEqual(plugins['aad']['description'], 'Deutsche Beschreibung.')

    def test_french_localization(self):
        plugins = self._load_for_lang('fr')
        self.assertEqual(plugins['aad']['name'], 'Détails supplémentaires')
        self.assertEqual(plugins['aad']['description'], 'Description française.')

    def test_untranslated_language_uses_english(self):
        plugins = self._load_for_lang('it')
        self.assertEqual(plugins['aad']['name'], 'Additional Artists Details')
        self.assertEqual(plugins['aad']['description'], 'English description.')

    def test_original_cached_data_not_mutated(self):
        self._load_for_lang('de')
        # The shared/cached registry dict must keep its English base values.
        self.assertEqual(self._REGISTRY['aad']['name'], 'Additional Artists Details')
        self.assertEqual(self._REGISTRY['aad']['description'], 'English description.')


class PluginsViewsTest(FrontendTestCase):
    """Tests for plugins routes"""

    def test_plugins_root_returns_200(self):
        """Test /plugins/ returns 200"""
        response = self.client.get("/plugins/")
        self.assert200(response)

    def test_plugins_invalid_subpage_returns_404(self):
        """Test /plugins/404 returns 404"""
        response = self.client.get("/plugins/404")
        self.assert404(response)


class PluginsMissingDataTest(FrontendTestCase):
    """Tests that missing plugin data returns 503"""

    def create_app(self):
        from website.frontend import create_app

        return create_app(config_overrides={
            'TESTING': True,
            'SCHEDULER_API_ENABLED': True,
            'PLUGINS_BUILD_DIR': '/nonexistent/path',
        })

    def test_plugins_root_missing_data_returns_503(self):
        """Test /plugins/ returns 503 when plugin data not generated"""
        response = self.client.get("/plugins/")
        self.assertEqual(response.status_code, 503)

    def test_api_v1_plugins_missing_data_returns_503(self):
        """Test /api/v1/plugins/ returns 503 when plugin data not generated"""
        response = self.client.get("/api/v1/plugins/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json, {'error': 'Plugin data unavailable.'})
