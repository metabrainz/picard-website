from app import app
from flask import render_template

import json
from urllib import urlopen


@app.route('/plugins/')
def show_plugins():
    url = "https://raw.githubusercontent.com/dufferzafar" \
          "/picard-plugins/master/plugins.json"
    plugins = json.loads(urlopen(url).read().decode("utf-8"))
    return render_template('plugins.html', plugins=plugins['plugins'])
