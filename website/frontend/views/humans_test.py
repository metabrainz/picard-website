from website.frontend.testing import FrontendTestCase

class ViewsTestCase(FrontendTestCase):

    def test_humans_txt(self):
        response = self.client.get("/humans.txt")
        self.assert200(response)
