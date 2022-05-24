from flask import Blueprint, render_template, current_app
from packaging import version

from .changelog import *
from .humans import *
from .plugins import *
from .docs import *
from .api import *


frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.get('/')
def show_index():
    return render_template('index.html',
                           **current_app.config['PICARD_VERSIONS']['stable'])


@frontend_bp.get('/downloads/')
def show_downloads():
    version_config = current_app.config['PICARD_VERSIONS']
    beta_version = version.parse(version_config['beta']['tag'])
    stable_version = version.parse(version_config['stable']['tag'])
    show_beta = beta_version > stable_version
    return render_template('downloads.html',
                           **version_config, show_beta=show_beta)


@frontend_bp.get('/quick-start/')
def show_quick_start():
    return render_template('quick-start.html')
