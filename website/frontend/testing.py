from flask_testing import TestCase
from website.frontend import create_app
from urllib.parse import urlparse, urljoin


class FrontendTestCase(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # This overwrites https://github.com/jarus/flask-testing/blob/17f19d7fee0e1e176703fc7cb04917a77913ba1a/flask_testing/utils.py#L289
    # for status code 308 as used by Werkzeug >= 0.15
    def assertRedirects(self, response, location, message=None):
        """
        Checks if response is an HTTP redirect to the
        given location.
        :param response: Flask response
        :param location: relative URL path to SERVER_NAME or an absolute URL
        """
        parts = urlparse(location)

        if parts.netloc:
            expected_location = location
        else:
            server_name = self.app.config.get('SERVER_NAME') or 'localhost'
            expected_location = urljoin("http://%s" % server_name, location)

        valid_status_codes = (301, 302, 303, 305, 307, 308)
        valid_status_code_str = ', '.join(str(code) for code in valid_status_codes)
        not_redirect = "HTTP Status %s expected but got %d" % (valid_status_code_str, response.status_code)
        self.assertTrue(response.status_code in valid_status_codes, message or not_redirect)
        self.assertEqual(response.location, expected_location, message)
