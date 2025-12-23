from collections import OrderedDict
from urllib.request import urlopen

from tomllib import loads


def load_registry_toml(app, force_refresh=False) -> str:
    """Load the registry TOML file from PLUGINS_V3_REGISTRY_URL"""
    key = 'plugin3_registry'
    data = app.cache.get(key) if not force_refresh else None
    if data:
        return data

    url = app.config['PLUGINS_V3_REGISTRY_URL']
    with urlopen(url, timeout=app.config['PLUGINS_V3_REGISTRY_REQUEST_TIMEOUT_SECONDS']) as conn:
        data = conn.read().decode("utf-8")
        app.cache.set(key, data, timeout=app.config['PLUGINS_V3_REGISTRY_CACHE_TIMEOUT_SECONDS'])
    return data


def load_plugin_list(app, force_refresh=False) -> OrderedDict:
    """Return the plugins from the registry in a format compatible with other versions."""
    key = 'plugin3_full_list'
    plugins = app.cache.get(key) if not force_refresh else None
    if plugins:
        return plugins

    registry_toml = load_registry_toml(app, force_refresh)
    registry = loads(registry_toml)
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
