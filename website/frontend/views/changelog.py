from urllib.request import urlopen
from flask import current_app, Blueprint, render_template
import re
import mistune


changelog_bp = Blueprint('changelog', __name__)
re_version = re.compile(r'^Version\s+(.*?)\s+-\s+(.*?)$')
version_header = '<h3 id="release-{0}">Version <strong>{0}</strong> <span>{1}</span></h3>'


class ChangelogRenderer(mistune.HTMLRenderer):
    def heading(self, text, level, **attrs):
        if level == 1:
            match = re_version.match(text)
            if match:
                version = match.group(1)
                date = match.group(2).replace("xxxx-xx-xx", "Yet to be released")
                return version_header.format(version, date)
        return super().heading(text, level + 2)


renderer = ChangelogRenderer()
markdown = mistune.Markdown(renderer=renderer)


def load_changelog(app):
    key = 'changelog_data'
    data = app.cache.get(key)
    if data is None:
        url = app.config['CHANGELOG_URL']
        with urlopen(url) as conn:
            data = conn.read().decode("utf-8-sig")
            data = markdown(data)
            app.cache.set(key, data, timeout=app.config['CHANGELOG_CACHE_TIMEOUT'])
    return data


@changelog_bp.get('/')
def show_changelog():
    app = current_app
    return render_template('changelog.html', changelog=load_changelog(app))
