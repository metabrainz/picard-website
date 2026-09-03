"""Health check endpoint.

A small, cheap, side-effect-free endpoint used by Consul health checks (and the
uwsgi->HTTP migration's protocol probe — see syswiki UwsgiToHttpMigration.md).

It is intentionally kept out of `/` (no templates, no dependencies) so it stays
fast and cannot be broken by a slow home page.

Access is restricted to configured IP ranges via ``HEALTH_ALLOWED_IPS`` — the
check reaches the backend directly on its (internal) address, so the default
allows loopback and the private ranges. An empty list allows everyone.

This mirrors the scheduler API restriction (see ``scheduler.py``): a
``before_request`` guard keyed on the path, using ``request.remote_addr``
(never a spoofable ``X-Forwarded-For``), logging a warning and returning 403.
Unlike the scheduler's exact-host list, the health allow-list supports CIDR
**ranges**, which are parsed once at init.
"""

import ipaddress

from flask import abort, request


def _parse_networks(values, logger):
    """Parse CIDR/IP strings into ip_network objects, skipping (and logging) bad ones."""
    networks = []
    for value in values or []:
        try:
            networks.append(ipaddress.ip_network(value, strict=False))
        except ValueError:
            logger.warning("HEALTH_ALLOWED_IPS: ignoring invalid entry %r", value)
    return networks


def _is_allowed(client_ip, allowed_networks):
    """True if ``client_ip`` is within any of ``allowed_networks`` (empty = allow all)."""
    if not allowed_networks:
        return True
    if client_ip is None:
        return False
    try:
        addr = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    return any(addr in net for net in allowed_networks)


def init_healthz(app):
    logger = app.logger
    # Parse the allow-list once; config does not change at runtime.
    allowed_networks = _parse_networks(app.config.get('HEALTH_ALLOWED_IPS'), logger)

    # Restrict the health endpoint to allowed IP ranges only.
    @app.before_request
    def restrict_healthz():
        if request.path == '/healthz':
            if not _is_allowed(request.remote_addr, allowed_networks):
                logger.warning('Health check access denied from %s', request.remote_addr)
                abort(403)

    @app.get('/healthz')
    def healthz():
        return 'ok\n', 200, {'Content-Type': 'text/plain; charset=utf-8'}
