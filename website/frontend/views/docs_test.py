from website.frontend.testing import FrontendTestCase
from flask import url_for


class ViewsTestCase(FrontendTestCase):

    def test_docs_root(self):
        "Test /docs/ main page"
        response = self.client.get("/docs/")
        self.assert200(response)

    def test_docs_subpage(self):
        "Test /docs/ valid sub-page"
        response = self.client.get("/docs/guide/")
        self.assert200(response)

    def test_docs_404(self):
        "Test /docs/ invalid sub-page"
        response = self.client.get("/docs/404/")
        self.assert404(response)
