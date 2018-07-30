from flask import Blueprint, render_template, current_app

from .changelog import *
from .humans import *
from .plugins import *
from .docs import *
from .api import *


frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/')
def show_index():
    return render_template('index.html',
                           **current_app.config['PICARD_VERSIONS']['stable'])


@frontend_bp.route('/downloads/')
def show_downloads():
    return render_template('downloads.html',
                           **current_app.config['PICARD_VERSIONS']['stable'])


@frontend_bp.route('/quick-start/')
def show_quick_start():
    return render_template('quick-start.html')
