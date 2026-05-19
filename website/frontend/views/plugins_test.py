from website.frontend.testing import FrontendTestCase


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
