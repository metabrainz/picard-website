from website.frontend.testing import FrontendTestCase


class ViewsTestCase(FrontendTestCase):

    def test_home_page(self):
        "Test /"
        response = self.client.get("/")
        self.assert200(response)

    def test_404(self):
        "Test 404 error"
        response = self.client.get("/404")
        self.assert404(response)

    def test_downloads(self):
        "Test /downloads/"
        response = self.client.get("/downloads/")
        self.assert200(response)

    def test_quick_start(self):
        "Test /quick-start/"
        response = self.client.get("/quick-start/")
        self.assert200(response)

    def test_home_page_french_cookie(self):
        "Test / in french (cookie)"
        server_name = self.app.config.get('SERVER_NAME') or 'localhost'
        self.client.set_cookie('language', 'fr', domain=server_name)
        response = self.client.get("/")
        self.assert200(response)
        self.assertIn(b'fichiers audio', response.data)

    def test_home_page_french_url(self):
        "Test / in french (url parameter)"
        response = self.client.get("/?l=fr")
        self.assert200(response)
        self.assertIn(b'fichiers audio', response.data)
