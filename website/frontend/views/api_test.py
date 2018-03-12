from website.frontend.testing import FrontendTestCase
from flask import url_for


_MESSAGES = {
    'plugin_not_found': 'Plugin not found.',
    'missing_api_version': 'No API version specified',
    'invalid_endpoint': 'The two endpoints currently available for this api version'
                        ' are /api/v2/plugins and /api/v2/download',
    'missing_id': 'Plugin id not specified.',
    'download_usage': 'Correct usage: /api/v2/download?id=<id>',
}


class ViewsTestCase(FrontendTestCase):

    # api

    def test_api_404(self):
        response = self.client.get("/api/404/")
        self.assert404(response)

    def test_api_root(self):
        for path in ['/api', '/api/']:
            response = self.client.get(path)
            self.assert404(response)
            self.assertEqual(response.json, dict(
                message=_MESSAGES['missing_api_version']))

    def test_api_noroute_path(self):
        "Test API URLs with paths for which no route exists"
        for path in ['/api/v2/:', '/api/v2/:', '/api/v3/:']:
            response = self.client.get(path)
            self.assert404(response)
            self.assertTemplateUsed('errors/404.html')
    # /v2/

    def test_api_v2_redirect(self):
        "Test /api/v2"
        response = self.client.get("/api/v2")
        self.assertRedirects(response, url_for("api.api_root", version='v2'))

    def test_api_v2(self):
        "Test /api/v2/"
        response = self.client.get("/api/v2/")
        self.assert200(response)
        self.assertEqual(response.json, dict(
            message=_MESSAGES['invalid_endpoint']))

    # /v2/plugins/

    def test_api_v2_plugins_redirect(self):
        "Test plugins list redirection"
        response = self.client.get("/api/v2/plugins")
        self.assertRedirects(response, url_for("api.get_plugin", version='v2'))

    def test_api_v2_plugins(self):
        "Test plugins list"
        response = self.client.get("/api/v2/plugins/")
        self.assert200(response)
        self.assertIn('plugins', list(response.json.keys()))

    def test_api_v2_plugins_with_id_not_found(self):
        "Test bad plugin id"
        response = self.client.get("/api/v2/plugins/?id=0")
        self.assert404(response)
        self.assertEqual(
            response.json, dict(error=_MESSAGES['plugin_not_found']))

    def test_api_v2_plugins_with_id(self):
        "Test valid plugin id"
        response = self.client.get("/api/v2/plugins/?id=addrelease")
        self.assert200(response)
        self.assertIn('plugin', list(response.json.keys()))

    # /v2/download

    def test_api_v2_download_with_id_redirect(self):
        "Test download redirection"
        response = self.client.get("/api/v2/download")
        self.assertRedirects(response, url_for("api.download_plugin", version='v2'))

    def test_api_v2_download_with_id_not_found(self):
        "Test download with invalid plugin id"
        response = self.client.get("/api/v2/download/?id=0")
        self.assert404(response)
        self.assertEqual(
            response.json, dict(error=_MESSAGES['plugin_not_found']))

    def test_api_v2_download_with_no_id(self):
        "Test download with no plugin id"
        response = self.client.get("/api/v2/download/")
        self.assert400(response)
        self.assertEqual(response.json, dict(error=_MESSAGES['missing_id'],
                                              message=_MESSAGES['download_usage']))

    def test_api_v2_download_with_id(self):
        "Test download with a valid plugin id"
        response = self.client.get("/api/v2/download/?id=addrelease")
        self.assert200(response)
        self.assertEqual(response.content_type, 'application/zip')
