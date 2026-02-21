from flask import current_app as app

from website.frontend.testing import FrontendTestCase


class ViewsTestCase(FrontendTestCase):
    def test_docs_root(self):
        "Test /docs/ main page"
        response = self.client.get("/docs/")
        self.assertStatus(response, status_code=301)
        self.assert_redirects(response, app.config['DOCS_BASE_URL'] + '/')

    def test_docs_redirect(self):
        "Test /docs/ valid sub-page"
        response = self.client.get("/docs/basics/")
        self.assertStatus(response, status_code=301)
        self.assert_redirects(response, app.config['DOCS_BASE_URL'] + '/en/introduction.html')

    def test_docs_subpage(self):
        "Test /docs/ valid sub-page"
        response = self.client.get("/docs/development/")
        self.assert200(response)

    def test_docs_404(self):
        "Test /docs/ invalid sub-page"
        response = self.client.get("/docs/404/")
        self.assert404(response)
