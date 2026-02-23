from flask import current_app as app

from website.frontend.testing import FrontendTestCase


class DocsViewsTest(FrontendTestCase):
    """Tests for docs routes"""

    def test_docs_root_redirects(self):
        """Test /docs/ redirects to external docs"""
        response = self.client.get("/docs/")
        self.assertStatus(response, status_code=301)
        self.assert_redirects(response, app.config['DOCS_BASE_URL'] + '/')

    def test_docs_basics_redirects(self):
        """Test /docs/basics/ redirects to external docs"""
        response = self.client.get("/docs/basics/")
        self.assertStatus(response, status_code=301)
        self.assert_redirects(response, app.config['DOCS_BASE_URL'] + '/en/introduction.html')

    def test_docs_development_page_returns_200(self):
        """Test /docs/development/ returns 200"""
        response = self.client.get("/docs/development/")
        self.assert200(response)

    def test_docs_invalid_page_returns_404(self):
        """Test /docs/404/ returns 404"""
        response = self.client.get("/docs/404/")
        self.assert404(response)
