from flask import url_for

from website.frontend.testing import FrontendTestCase


class ViewsTestCase(FrontendTestCase):
    def test_changelog(self):
        "Test /changelog/"
        response = self.client.get("/changelog/")
        self.assert200(response)
        self.assertIn(b'Version', response.data)

    def test_changelog_redirect(self):
        "Test /changelog"
        response = self.client.get("/changelog")
        self.assertRedirects(response, url_for("changelog.show_changelog"))
