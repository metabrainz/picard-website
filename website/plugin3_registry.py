from collections import OrderedDict
from dataclasses import dataclass
from time import time
from urllib.error import HTTPError
from urllib.request import urlopen

from tomllib import loads

@dataclass
class RegistryCacheEntry:
    registry: str
    timestamp: int

    def __init__(self, registry: str):
        self.registry = registry
        self.timestamp = int(time())

    def is_valid(self, timeout_seconds: int):
        return int(time()) - self.timestamp <= timeout_seconds


def load_registry_toml(app, force_refresh=False) -> str | None:
    """Load the registry TOML file from PLUGINS_V3_REGISTRY_URL"""
    key = 'plugin3_registry'
    cache_timeout = app.config['PLUGINS_V3_REGISTRY_CACHE_TIMEOUT_SECONDS']
    cache_entry = app.cache.get(key) if not force_refresh else None
    if cache_entry and cache_entry.is_valid(cache_timeout):
        return cache_entry.registry

    url = app.config['PLUGINS_V3_REGISTRY_URL']
    app.logger.debug('Refreshing v3 plugin registry from %s', url)
    try:
        with urlopen(url, timeout=app.config['PLUGINS_V3_REGISTRY_REQUEST_TIMEOUT_SECONDS']) as conn:
            registry = conn.read().decode("utf-8")
            cache_entry = RegistryCacheEntry(registry)
            app.cache.set(key, cache_entry, timeout=0)
    except HTTPError as err:
        app.logger.error('Failed loading v3 plugin registry: %s',  err)
    return cache_entry.registry if cache_entry else None


def load_plugin_list(app, force_refresh=False) -> OrderedDict:
    """Return the plugins from the registry in a format compatible with other versions."""
    key = 'plugin3_full_list'
    plugins = app.cache.get(key) if not force_refresh else None
    if plugins:
        return plugins

    registry_toml = load_registry_toml(app, force_refresh)
    registry = loads(registry_toml) if registry_toml else {}
    plugins = OrderedDict()
    for plugin in registry.get('plugins', []):
        id = plugin.get('id')
        name = plugin.get('name', '')
        if not id or not name:
            continue

        # Convert to expected format for frontend
        plugins[id] = {
            'name': name,
            'description': plugin.get('description', ''),
            'author': ', '.join(plugin.get('authors', [])),
            'version': '',
        }

    app.cache.set(key, plugins, timeout=app.config['PLUGINS_V3_REGISTRY_CACHE_TIMEOUT_SECONDS'])
    return plugins
