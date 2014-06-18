from app import app
from flask import render_template

import re
from urllib.request import urlopen


def re_sub(string, find, replace):
    return re.sub(find, replace, string)


def re_search(string, pattern):
    return re.search(pattern, string)


def version(string, group):
    return re.match(r"^Version\s+(.*?)\s+-\s+(.*?)$", string).group(group)

app.jinja_env.tests['re_search'] = re_search
app.jinja_env.filters['re_sub'] = re_sub
app.jinja_env.filters['version'] = version


@app.route('/changelog/')
def show_changelog():
    url = "https://raw.githubusercontent.com/musicbrainz/picard/master/NEWS.txt"
    data = urlopen(url).read().decode("utf-8-sig")
    return render_template('changelog.html', lines=data.splitlines())
