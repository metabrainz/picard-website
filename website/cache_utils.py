"""Cache utilities for the website"""
from functools import wraps


def cached(key, timeout_config_key=None, force_refresh_param='force_refresh'):
    """
    Decorator for caching function results.

    Args:
        key: Cache key string or callable that takes function args and returns key
        timeout_config_key: Config key for cache timeout (e.g., 'PLUGINS_CACHE_TIMEOUT').
                           If None, uses 'DEFAULT_CACHE_TIMEOUT'
        force_refresh_param: Name of the parameter that forces cache refresh

    Usage:
        @cached('my_key')  # Uses DEFAULT_CACHE_TIMEOUT
        def load_data(app):
            return expensive_operation()

        @cached('my_key', 'MY_TIMEOUT')  # Uses specific timeout
        def load_data(app):
            return expensive_operation()

        @cached(lambda app, version: f'data_{version}', 'MY_TIMEOUT')
        def load_versioned_data(app, version, force_refresh=False):
            return expensive_operation(version)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # First arg should be app
            app = args[0] if args else kwargs.get('app')
            if not app:
                raise ValueError("First argument must be 'app' (Flask application)")

            # Get cache key
            cache_key = key(*args, **kwargs) if callable(key) else key

            # Check force_refresh parameter
            force_refresh = kwargs.get(force_refresh_param, False)

            # Try to get from cache
            data = app.cache.get(cache_key) if not force_refresh else None
            if data is None:
                data = func(*args, **kwargs)
                if data is not None:
                    timeout_key = timeout_config_key or 'DEFAULT_CACHE_TIMEOUT'
                    timeout = app.config[timeout_key]
                    app.cache.set(cache_key, data, timeout=timeout)
            return data

        return wrapper
    return decorator
