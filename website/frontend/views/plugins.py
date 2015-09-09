from collections import OrderedDict
import os
import json
from urllib import urlopen
from flask import current_app, Blueprint, render_template

plugins_bp = Blueprint('plugins', __name__)


@plugins_bp.route('/')
def show_plugins():
    ordered_plugins = OrderedDict()
    plugins_json_file = os.path.join(
        current_app.config['PLUGINS_REPOSITORY'], "plugins.json")
    with open(plugins_json_file, "r") as fp:
        plugins = json.loads(fp.read().decode("utf-8"))['plugins']
        for key in sorted(plugins, key=lambda k: plugins[k]['name'].lower()):
            ordered_plugins[key] = plugins[key]
    return render_template('plugins.html', plugins=ordered_plugins)
