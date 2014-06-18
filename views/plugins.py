from app import app
from flask import render_template

import re
import json
from urllib.request import urlopen


def beautify(string):
    return re.sub(r"^u", "", re.sub(r"[\'\"\\]", "", string))

app.jinja_env.filters['beautify'] = beautify


@app.route('/plugins/')
def show_plugins():
    url = "https://raw.githubusercontent.com/dufferzafar/picard-plugins/master/Plugins.json"
    plugins = json.loads(urlopen(url).read().decode("utf-8"))
    return render_template('plugins.html', plugins=plugins['plugins'])
