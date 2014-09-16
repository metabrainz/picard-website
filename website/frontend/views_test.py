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
