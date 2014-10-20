from flask.ext.testing import TestCase
from website.frontend import create_app


class FrontendTestCase(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass
