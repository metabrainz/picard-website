from website.frontend.testing import FrontendTestCase


class ChangelogViewsTest(FrontendTestCase):
    """Tests for changelog routes"""

    def test_changelog_returns_200(self):
        """Test /changelog/ returns 200 with content"""
        response = self.client.get("/changelog/")
        self.assert200(response)
        self.assertIn(b'Version', response.data)
