from website.frontend.testing import FrontendTestCase
from flask import url_for


_MESSAGES = {
    'plugin_not_found': 'Plugin not found.',
    'missing_api_version': 'No API version specified',
    'invalid_endpoint': 'The two endpoints currently available for this api version'
                        ' are /api/v1/plugins and /api/v1/download',
    'missing_id': 'Plugin id not specified.',
    'download_usage': 'Correct usage: /api/v1/download?id=<id>',
}


class ViewsTestCase(FrontendTestCase):

    # api

    def test_api_404(self):
        response = self.client.get("/api/404/")
        self.assert404(response)

    def test_api_root(self):
        response = self.client.get("/api")
        self.assert404(response)
        self.assertEquals(response.json, dict(
            message=_MESSAGES['missing_api_version']))

    # /v1/

    def test_api_v1_redirect(self):
        "Test /api/v1"
        response = self.client.get("/api/v1")
        self.assertRedirects(response, url_for("api.api_root", version='v1'))

    def test_api_v1(self):
        "Test /api/v1/"
        response = self.client.get("/api/v1/")
        self.assert200(response)
        self.assertEquals(response.json, dict(
            message=_MESSAGES['invalid_endpoint']))

    # /v1/plugins/

    def test_api_v1_plugins_redirect(self):
        "Test plugins list redirection"
        response = self.client.get("/api/v1/plugins")
        self.assertRedirects(response, url_for("api.get_plugin", version='v1'))

    def test_api_v1_plugins(self):
        "Test plugins list"
        response = self.client.get("/api/v1/plugins/")
        self.assert200(response)
        self.assertIn('plugins', response.json.keys())

    def test_api_v1_plugins_with_id_not_found(self):
        "Test bad plugin id"
        response = self.client.get("/api/v1/plugins/?id=0")
        self.assert404(response)
        self.assertEquals(
            response.json, dict(error=_MESSAGES['plugin_not_found']))

    def test_api_v1_plugins_with_id(self):
        "Test valid plugin id"
        response = self.client.get("/api/v1/plugins/?id=addrelease")
        self.assert200(response)
        self.assertIn('plugin', response.json.keys())

    # /v1/download

    def test_api_v1_download_with_id_redirect(self):
        "Test download redirection"
        response = self.client.get("/api/v1/download")
        self.assertRedirects(response, url_for("api.download_plugin", version='v1'))

    def test_api_v1_download_with_id_not_found(self):
        "Test download with invalid plugin id"
        response = self.client.get("/api/v1/download/?id=0")
        self.assert404(response)
        self.assertEquals(
            response.json, dict(error=_MESSAGES['plugin_not_found']))

    def test_api_v1_download_with_no_id(self):
        "Test download with no plugin id"
        response = self.client.get("/api/v1/download/")
        self.assert400(response)
        self.assertEquals(response.json, dict(error=_MESSAGES['missing_id'],
                                              message=_MESSAGES['download_usage']))

    def test_api_v1_download_with_id(self):
        "Test download with a valid plugin id"
        response = self.client.get("/api/v1/download/?id=addrelease")
        self.assert200(response)
        self.assertEquals(response.content_type, 'application/zip')
