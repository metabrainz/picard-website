from app import app
from flask import render_template

import json
from urllib import urlopen

@app.route('/plugins/')
def show_plugins():
    with open('plugins.json', "r") as plugin_file:
        plugins = json.loads(plugin_file.read().decode("utf-8"))
    return render_template('plugins.html', plugins=plugins['plugins'])
