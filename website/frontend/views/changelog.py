from urllib.request import urlopen
from flask import current_app, Blueprint, render_template
from markupsafe import Markup
import re


changelog_bp = Blueprint('changelog', __name__)
re_code = re.compile(r'`(.*?)`')
re_tickets = re.compile(r'(PICARD\-\d+)')
re_version = re.compile(r'^Version\s+(.*?)\s+-\s+(.*?)$')


def re_sub(string, find, replace):
    return re.sub(find, replace, string)


def re_search(string, pattern):
    return re.search(pattern, string)


def version(string, group):
    return re_version.match(string).group(group)


def add_markup(string):
    # if re_tickets.search(string):
    string = re_tickets.sub('<a href="https://tickets.musicbrainz.org/browse/\g<1>">\g<1></a>', string)
    string = re_code.sub('<code>\g<1></code>', string)
    return Markup(string)


def load_changelog(app):
    key = 'changelog_data'
    data = app.cache.get(key)
    if data is None:
        url = app.config['CHANGELOG_URL']
        with urlopen(url) as conn:
            data = conn.read().decode("utf-8-sig").splitlines()
            app.cache.set(key, data, timeout=app.config['CHANGELOG_CACHE_TIMEOUT'])
    return data


@changelog_bp.route('/')
def show_changelog():
    app = current_app
    app.jinja_env.tests['re_search'] = re_search
    app.jinja_env.filters['re_sub'] = re_sub
    app.jinja_env.filters['version'] = version
    app.jinja_env.filters['add_markup'] = add_markup
    return render_template('changelog.html', lines=load_changelog(app))
