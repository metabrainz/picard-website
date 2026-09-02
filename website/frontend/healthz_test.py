import ipaddress
import logging

from website.frontend import create_app
from website.frontend.healthz import _is_allowed, _parse_networks


class _App:
    """Minimal helper to build an app with specific HEALTH_ALLOWED_IPS."""

    @staticmethod
    def client(allowed_ips):
        app = create_app(config_overrides={'TESTING': True, 'HEALTH_ALLOWED_IPS': allowed_ips})
        return app.test_client()


def test_healthz_allowed_from_loopback():
    # 127.0.0.1 (the test client default) is inside 127.0.0.0/8
    client = _App.client(['127.0.0.0/8'])
    resp = client.get('/healthz')
    assert resp.status_code == 200
    assert resp.data == b'ok\n'


def test_healthz_denied_from_outside_range():
    client = _App.client(['10.0.0.0/8'])  # loopback not included
    resp = client.get('/healthz', environ_overrides={'REMOTE_ADDR': '8.8.8.8'})
    assert resp.status_code == 403


def test_healthz_allowed_within_range():
    client = _App.client(['10.0.0.0/8'])
    resp = client.get('/healthz', environ_overrides={'REMOTE_ADDR': '10.2.2.20'})
    assert resp.status_code == 200


def test_healthz_empty_list_allows_all():
    client = _App.client([])
    resp = client.get('/healthz', environ_overrides={'REMOTE_ADDR': '203.0.113.1'})
    assert resp.status_code == 200


def test_healthz_ignores_x_forwarded_for():
    # An outside peer must not bypass the allow-list by spoofing X-Forwarded-For.
    client = _App.client(['10.0.0.0/8'])
    resp = client.get(
        '/healthz',
        environ_overrides={'REMOTE_ADDR': '8.8.8.8'},
        headers={'X-Forwarded-For': '10.2.2.20'},
    )
    assert resp.status_code == 403


# --- unit tests for the helpers ---


def test_is_allowed_empty_means_all():
    assert _is_allowed('8.8.8.8', []) is True


def test_is_allowed_membership():
    nets = [ipaddress.ip_network('10.0.0.0/8')]
    assert _is_allowed('10.9.9.9', nets) is True
    assert _is_allowed('11.0.0.1', nets) is False


def test_is_allowed_bad_ip():
    nets = [ipaddress.ip_network('10.0.0.0/8')]
    assert _is_allowed('not-an-ip', nets) is False
    assert _is_allowed(None, nets) is False


def test_parse_networks_skips_invalid(caplog):
    logger = logging.getLogger('test')
    with caplog.at_level(logging.WARNING):
        nets = _parse_networks(['10.0.0.0/8', 'garbage', '192.168.0.0/16'], logger)
    assert len(nets) == 2
