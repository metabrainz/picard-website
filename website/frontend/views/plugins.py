from collections import OrderedDict
import json
from flask import current_app, Blueprint, render_template
from urllib.error import HTTPError
from website.plugin_utils import plugins_json_file
from website.plugin3_registry import load_plugin_list
plugins_bp = Blueprint('plugins', __name__)


@plugins_bp.get('/')
def show_plugins():
    all_plugins = OrderedDict()
    versions = current_app.config['PLUGIN_VERSIONS']
    for version, build_version in sorted([(key, versions[key]['title']) for key in versions]):
        if version in {'v1', 'v2'}:
            ordered_plugins = _load_v1_v2_plugins(build_version)
        elif version == 'v3':
            ordered_plugins = _load_v3_plugins()
        else:
            ordered_plugins = None

        if ordered_plugins:
            all_plugins[version[1:]] = ordered_plugins
    return render_template('plugins.html', all_plugins=all_plugins)


def _load_v1_v2_plugins(build_version) -> OrderedDict:
    ordered_plugins = OrderedDict()
    build_json_file = plugins_json_file(current_app, build_version)
    with open(build_json_file, "r", encoding='utf-8') as fp:
        plugins = json.loads(fp.read())['plugins']
        for key in sorted(plugins, key=lambda k: plugins[k]['name'].lower()):
            ordered_plugins[key] = plugins[key]
    return ordered_plugins


def _load_v3_plugins() -> OrderedDict:
    return load_plugin_list(current_app)
