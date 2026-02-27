from website.frontend.testing import FrontendTestCase


class FrontendViewsTest(FrontendTestCase):
    """Tests for main frontend routes"""

    def test_routes_return_200(self):
        """Test that main routes return 200"""
        routes = ["/", "/downloads/", "/quick-start/"]
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assert200(response)

    def test_404(self):
        """Test 404 error"""
        response = self.client.get("/404")
        self.assert404(response)

    def test_home_page_french_cookie(self):
        """Test / in french (cookie)"""
        server_name = self.app.config.get('SERVER_NAME') or 'localhost'
        self.client.set_cookie('language', 'fr', domain=server_name)
        response = self.client.get("/")
        self.assert200(response)
        self.assertIn(b'fichiers audio', response.data)

    def test_home_page_french_url(self):
        """Test / in french (url parameter)"""
        response = self.client.get("/?l=fr")
        self.assert200(response)
        self.assertIn(b'fichiers audio', response.data)

    def test_registry_redirect(self):
        """Test /registry/plugins.toml redirects to /api/v3/registry/plugins.toml"""
        response = self.client.get("/registry/plugins.toml")
        self.assertStatus(response, 302)
        self.assertEqual(response.location, '/api/v3/registry/plugins.toml')

    def test_registry_redirect_no_follow(self):
        """Test /registry/plugins.toml redirect is temporary (302)"""
        response = self.client.get("/registry/plugins.toml", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
