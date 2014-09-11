import os
import json
from urllib import urlopen
from flask import Blueprint, render_template
from config import PLUGINS_REPOSITORY

PLUGINS_JSON_FILE = os.path.join(PLUGINS_REPOSITORY, "plugins.json")

plugins_bp = Blueprint('plugins', __name__)

@plugins_bp.route('/')
def show_plugins():
    with open(PLUGINS_JSON_FILE, "r") as fp:
        plugins = json.loads(fp.read().decode("utf-8"))
    return render_template('plugins.html', plugins=plugins['plugins'])
