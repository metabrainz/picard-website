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
