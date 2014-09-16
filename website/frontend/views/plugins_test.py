from website.frontend.testing import FrontendTestCase
from flask import url_for


class ViewsTestCase(FrontendTestCase):

    def test_plugins_404(self):
        "Test /plugins/ invalid subpage"
        response = self.client.get("/plugins/404")
        self.assert404(response)

    def test_plugins_root(self):
        "Test /plugins/"
        response = self.client.get("/plugins/")
        self.assert200(response)
