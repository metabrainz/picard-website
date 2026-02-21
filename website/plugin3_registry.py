from collections import OrderedDict
from dataclasses import dataclass
from time import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tomllib import loads

from website.cache_utils import cached


@dataclass
class RegistryCacheEntry:
    registry: str
    timestamp: int
    etag: str | None = None

    def __init__(self, registry: str, etag: str | None = None):
        self.registry = registry
        self.etag = etag
        self.refresh_timestamp()

    @staticmethod
    def now():
        """Get current timestamp"""
        return int(time())

    def is_valid(self, timeout_seconds: int):
        return self.now() - self.timestamp <= timeout_seconds

    def refresh_timestamp(self):
        """Update timestamp to current time"""
        self.timestamp = self.now()


def load_registry_toml(app, force_refresh=False) -> str | None:
    """Load the registry TOML file from PLUGINS_V3_REGISTRY_URL"""
    key = 'plugin3_registry'
    cache_timeout = app.config['PLUGINS_V3_REGISTRY_CACHE_TIMEOUT']
    cache_entry = app.cache.get(key) if not force_refresh else None

    # If cache is fresh, return it
    if cache_entry and cache_entry.is_valid(cache_timeout):
        return cache_entry.registry

    # Cache is stale or missing, try to refresh
    url = app.config['PLUGINS_V3_REGISTRY_URL']
    app.logger.debug('Refreshing v3 plugin registry from %s', url)

    # Build request with conditional headers
    request = Request(url)
    if cache_entry and cache_entry.etag:
        request.add_header('If-None-Match', cache_entry.etag)

    try:
        with urlopen(request, timeout=app.config['PLUGINS_V3_REGISTRY_REQUEST_TIMEOUT']) as conn:
            registry = conn.read().decode("utf-8")
            etag = conn.headers.get('ETag')

            # Validate it's parseable TOML before caching
            try:
                loads(registry)
            except Exception as parse_err:
                app.logger.error('Registry content is not valid TOML: %s. Using stale cache if available.', parse_err)
                return cache_entry.registry if cache_entry else None

            cache_entry = RegistryCacheEntry(registry, etag)
            app.cache.set(key, cache_entry, timeout=0)
            return cache_entry.registry
    except HTTPError as err:
        if err.code == 304:  # Not Modified
            if not cache_entry:
                app.logger.error('Received 304 but cache_entry is None - this should not happen')
                return None
            app.logger.debug('Registry unchanged (304), refreshing timestamp')
            cache_entry.refresh_timestamp()
            app.cache.set(key, cache_entry, timeout=0)
            return cache_entry.registry
        app.logger.warning('Failed loading v3 plugin registry: %s. Using stale cache if available.', err)
    except Exception as err:
        app.logger.error('Error fetching v3 plugin registry: %s. Using stale cache if available.', err)

    # Return stale cache as fallback
    return cache_entry.registry if cache_entry else None


@cached('plugin3_full_list', 'PLUGINS_V3_REGISTRY_CACHE_TIMEOUT')
def load_plugin_list(app, force_refresh=False) -> OrderedDict:
    """Return the plugins from the registry in a format compatible with other versions."""
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
            'git_url': plugin.get('git_url', ''),
        }
    return plugins
