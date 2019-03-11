from website.frontend.testing import FrontendTestCase
from flask import url_for
import re

_MESSAGES = {
    'plugin_not_found': 'Plugin not found.',
    'missing_api_version': 'No API version specified',
    'invalid_endpoint': 'The endpoints currently available for this api version'
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
        for path in ['/api', '/api/']:
            response = self.client.get(path)
            self.assert404(response)
            self.assertEqual(response.json, dict(
                message=_MESSAGES['missing_api_version']))

    def test_api_noroute_path(self):
        "Test API URLs with paths for which no route exists"
        for path in ['/api/v1/:', '/api/v2/:', '/api/v3/:']:
            response = self.client.get(path)
            self.assert404(response)
            self.assertTemplateUsed('errors/404.html')
    # /v1/

    def test_api_v1_redirect(self):
        "Test /api/v1"
        response = self.client.get("/api/v1")
        self.assertRedirects(response, url_for("api.api_root", version='v1'))

    def test_api_v1(self):
        "Test /api/v1/"
        response = self.client.get("/api/v1/")
        self.assert200(response)
        self.assertEqual(response.json, dict(
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
        self.assertEqual(
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
        self.assertEqual(
            response.json, dict(error=_MESSAGES['plugin_not_found']))

    def test_api_v1_download_with_no_id(self):
        "Test download with no plugin id"
        response = self.client.get("/api/v1/download/")
        self.assert400(response)
        self.assertEqual(response.json, dict(error=_MESSAGES['missing_id'],
                                              message=_MESSAGES['download_usage']))

    def test_api_v1_download_with_id(self):
        "Test download with a valid plugin id"
        response = self.client.get("/api/v1/download/?id=addrelease")
        self.assert200(response)
        self.assertEqual(response.content_type, 'application/zip')

    # /v2/releases

    def test_api_v2_releases(self):
        "Test /api/v2/releases"
        url_re = re.compile(r'^(ftp|https?)://[^\s"]+$', re.IGNORECASE)
        response = self.client.get("/api/v2/releases/")
        self.assert200(response)
        updates = response.json['versions']
        self.assertIsInstance(updates, dict)
        for testkey in ['stable', 'beta', 'dev']:
            self.assertIn(testkey, updates)
            for subkey in ['tag', 'version', 'urls']:
                self.assertIn(subkey, updates[testkey])
            # Tag tests
            self.assertIsInstance(updates[testkey]['tag'], str)
            self.assertNotEqual(updates[testkey]['tag'], '')
            # Version tests
            self.assertIsInstance(updates[testkey]['version'], list)
            self.assertEqual(len(updates[testkey]['version']), 5)
            for i in [0, 1, 2, 4]:
                self.assertIsInstance(updates[testkey]['version'][i], int)
                self.assertEqual(updates[testkey]['version'][i] >= 0, True)
            self.assertIsInstance(updates[testkey]['version'][3], str)
            self.assertIn(updates[testkey]['version'][3], ['final', 'dev'])
            # Url tests
            self.assertIn('download', updates[testkey]['urls'])     # Confirm download url always exists
            for urlkey in updates[testkey]['urls']:
                # Basic validation on all urls provided
                self.assertIsInstance(updates[testkey]['urls'][urlkey], str)
                self.assertRegex(updates[testkey]['urls'][urlkey], url_re)
