import re
from urllib.request import urlopen

from flask import (
    Blueprint,
    current_app,
    render_template,
)
import mistune

from website.cache_utils import cached


changelog_bp = Blueprint('changelog', __name__)
re_version = re.compile(r'^Version\s+(.*?)\s+-\s+(.*?)$')
version_header = '<h3 id="release-{0}">Version <strong>{0}</strong> <span>{1}</span></h3>'


class ChangelogRenderer(mistune.HTMLRenderer):
    def heading(self, text, level, **attrs):
        # Ignore h1 headline
        if level == 1:
            return ""
        # Reformat h2 version headlines
        elif level == 2:
            match = re_version.match(text)
            if match:
                version = match.group(1)
                date = match.group(2).replace("xxxx-xx-xx", "Yet to be released")
                return version_header.format(version, date)
        return super().heading(text, level + 1)


renderer = ChangelogRenderer()
markdown = mistune.Markdown(renderer=renderer)


@cached('changelog_data', 'CHANGELOG_CACHE_TIMEOUT')
def load_changelog(app):
    url = app.config['CHANGELOG_URL']
    with urlopen(url) as conn:
        data = conn.read().decode("utf-8-sig")
        return markdown(data)


@changelog_bp.get('/')
def show_changelog():
    app = current_app
    return render_template('changelog.html', changelog=load_changelog(app))
