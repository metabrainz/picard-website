from collections import OrderedDict
import os
import json
from flask import current_app, Blueprint, render_template
from website.plugin_utils import plugins_json_file
plugins_bp = Blueprint('plugins', __name__)


@plugins_bp.route('/')
def show_plugins():
    all_plugins = OrderedDict()
    versions = current_app.config['PLUGIN_VERSIONS']
    for version, build_version in sorted([(key, versions[key]['title']) for key in versions]):
        ordered_plugins = OrderedDict()
        build_json_file = plugins_json_file(current_app, build_version)
        with open(build_json_file, "r") as fp:
            plugins = json.loads(fp.read())['plugins']
            for key in sorted(plugins, key=lambda k: plugins[k]['name'].lower()):
                ordered_plugins[key] = plugins[key]
        all_plugins[version[1:]] = ordered_plugins
    return render_template('plugins.html', all_plugins=all_plugins)
