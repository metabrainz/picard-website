from website.frontend.testing import FrontendTestCase


class HumansViewsTest(FrontendTestCase):
    """Tests for humans.txt route"""

    def test_humans_txt_returns_200(self):
        """Test /humans.txt returns 200"""
        response = self.client.get("/humans.txt")
        self.assert200(response)
