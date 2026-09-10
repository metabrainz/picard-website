"""Production WSGI entrypoint.

granian serves this factory (``website.wsgi:create_wsgi_app``) rather than
``website.frontend:create_app`` directly, so that behaviour specific to running
behind a reverse proxy stays out of the plain app used by the dev server and
the tests.

Behind a reverse proxy, ``REMOTE_ADDR`` is the proxy's address, and the real
client address arrives in the ``X-Forwarded-For`` header. granian provides a
WSGI wrapper that rewrites ``REMOTE_ADDR`` (and ``wsgi.url_scheme`` from
``X-Forwarded-Proto``) from those forwarded headers, but only when the request
comes from a trusted host. This restores the previous uWSGI
``log-x-forwarded-for`` behaviour and, importantly, makes the ``/healthz``
IP guard (which keys on ``request.remote_addr``) see the real client.

The set of trusted proxies is configured via ``TRUSTED_PROXIES`` (see
``default_config.py``). Keep it as tight as possible: a too-broad value would
let clients spoof their address via ``X-Forwarded-For``.
"""

from granian.utils.proxies import wrap_wsgi_with_proxy_headers

from website.frontend import create_app


def create_wsgi_app():
    app = create_app()
    trusted_proxies = app.config.get('TRUSTED_PROXIES', '127.0.0.1')
    return wrap_wsgi_with_proxy_headers(app.wsgi_app, trusted_hosts=trusted_proxies)
