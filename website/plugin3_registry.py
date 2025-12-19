from urllib.request import urlopen


def load_registry_toml(app, force_refresh=False):
    key = 'plugin3_registry'
    data = app.cache.get(key) if not force_refresh else None
    if data is None:
        url = app.config['PLUGINS_V3_REGISTRY_URL']
        with urlopen(url) as conn:
            data = conn.read().decode("utf-8")
            app.cache.set(key, data, timeout=app.config['PLUGINS_V3_REGISTRY_CACHE_TIMEOUT_SECONDS'])
    return data
