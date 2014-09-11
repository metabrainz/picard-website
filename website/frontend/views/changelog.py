from urllib import urlopen
from flask import current_app, Blueprint, render_template


changelog_bp = Blueprint('changelog', __name__)


def load_changelog(app):
    key = 'changelog_data'
    data = app.cache.get(key)
    if data is None:
        url = app.config['CHANGELOG_URL']
        data = urlopen(url).read().decode("utf-8-sig").splitlines()
        app.cache.set(key, data, timeout=app.config['CHANGELOG_CACHE_TIMEOUT'])
    return data


@changelog_bp.route('/')
def show_changelog():
    return render_template('changelog.html', lines=load_changelog(current_app))
