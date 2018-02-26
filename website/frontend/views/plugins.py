from collections import OrderedDict
import os
import json
from urllib.request import urlopen
from flask import current_app, Blueprint, render_template
from website.frontend.views.api import plugins_json_file
plugins_bp = Blueprint('plugins', __name__)


@plugins_bp.route('/')
def show_plugins():
    all_plugins = OrderedDict()
    for version, build_version in sorted(current_app.config['PLUGIN_VERSIONS'].items()):
        ordered_plugins = OrderedDict()
        build_json_file = plugins_json_file(current_app, build_version)
        with open(build_json_file, "r") as fp:
            plugins = json.loads(fp.read())['plugins']
            for key in sorted(plugins, key=lambda k: plugins[k]['name'].lower()):
                ordered_plugins[key] = plugins[key]
        all_plugins[version[1:]] = ordered_plugins
    return render_template('plugins.html', all_plugins=all_plugins)
