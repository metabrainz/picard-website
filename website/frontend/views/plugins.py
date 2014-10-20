import os
import json
from urllib import urlopen
from flask import current_app, Blueprint, render_template


plugins_bp = Blueprint('plugins', __name__)


@plugins_bp.route('/')
def show_plugins():
    # TODO : sorting
    plugins_json_file = os.path.join(
        current_app.config['PLUGINS_REPOSITORY'], "plugins.json")
    with open(plugins_json_file, "r") as fp:
        plugins = json.loads(fp.read().decode("utf-8"))
    return render_template('plugins.html', plugins=plugins['plugins'])
