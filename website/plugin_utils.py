import os

from flask import json

from website.cache_utils import cached


def plugins_build_dir(app):
    return app.config['PLUGINS_BUILD_DIR']


def plugins_json_file(app, version):
    """Returns the file that contains json data"""
    return os.path.join(plugins_build_dir(app), version, "plugins.json")


def plugins_dir(app, version):
    """Returns the directory which contains plugin files"""
    return os.path.join(plugins_build_dir(app), version)


@cached(lambda app, version, **kw: f'plugins_json_data_{version}', 'PLUGINS_CACHE_TIMEOUT')
def load_json_data(app, version, force_refresh=False):
    """Load JSON Data"""
    with open(plugins_json_file(app, version)) as fp:
        return json.load(fp)['plugins']
