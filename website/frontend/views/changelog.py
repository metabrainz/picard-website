from urllib.request import urlopen
from flask import current_app, Blueprint, render_template
import re


changelog_bp = Blueprint('changelog', __name__)


def re_sub(string, find, replace):
    return re.sub(find, replace, string)


def re_search(string, pattern):
    return re.search(pattern, string)


def version(string, group):
    return re.match(r"^Version\s+(.*?)\s+-\s+(.*?)$", string).group(group)


def load_changelog(app):
    key = 'changelog_data'
    data = app.cache.get(key)
    if data is None:
        url = app.config['CHANGELOG_URL']
        data = urlopen(url).read().decode().splitlines()
        app.cache.set(key, data, timeout=app.config['CHANGELOG_CACHE_TIMEOUT'])
    return data


@changelog_bp.route('/')
def show_changelog():
    app = current_app
    app.jinja_env.tests['re_search'] = re_search
    app.jinja_env.filters['re_sub'] = re_sub
    app.jinja_env.filters['version'] = version
    return render_template('changelog.html', lines=load_changelog(app))
