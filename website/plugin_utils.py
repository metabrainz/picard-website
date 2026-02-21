import os

from flask import json


def plugins_build_dir(app):
    return app.config['PLUGINS_BUILD_DIR']


def plugins_json_file(app, version):
    """Returns the file that contains json data"""
    return os.path.join(plugins_build_dir(app), version, "plugins.json")


def plugins_dir(app, version):
    """Returns the directory which contains plugin files"""
    return os.path.join(plugins_build_dir(app), version)


def load_json_data(app, version, force_refresh=False):
    """Load JSON Data"""
    key = 'plugins_json_data_%s' % version
    data = app.cache.get(key) if not force_refresh else None
    if data is None:
        with open(plugins_json_file(app, version)) as fp:
            data = json.load(fp)['plugins']
            app.cache.set(key, data, timeout=app.config['PLUGINS_CACHE_TIMEOUT'])
    return data
