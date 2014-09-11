from flask import Blueprint, render_template


changelog_bp = Blueprint('changelog', __name__)

@changelog_bp.route('/')
def show_changelog():
    url = "https://raw.githubusercontent.com/musicbrainz/picard/master/NEWS.txt"
    data = urlopen(url).read().decode("utf-8-sig")
    return render_template('changelog.html', lines=data.splitlines())
