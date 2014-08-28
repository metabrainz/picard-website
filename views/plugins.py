import os
import json
from urllib import urlopen
from flask import render_template
from app import app
from config import PLUGINS_REPOSITORY

PLUGINS_JSON_FILE = os.path.join(PLUGINS_REPOSITORY, "plugins.json")

@app.route('/plugins/')
def show_plugins():
    with open(PLUGINS_JSON_FILE, "r") as fp:
        plugins = json.loads(fp.read().decode("utf-8"))
    return render_template('plugins.html', plugins=plugins['plugins'])
