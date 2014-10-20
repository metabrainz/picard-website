from website.frontend import template_folder
from flask import (
    Blueprint,
    render_template,
    abort
)

import os

docs_bp = Blueprint('docs', __name__)


@docs_bp.route('/')
def show_basics():
    return render_template('docs/basics.html')


@docs_bp.route('/<string:page>/')
def show_pages(page):
    if os.path.isfile(os.path.join(template_folder, 'docs', page + '.html')):
        return render_template('docs/' + page + '.html')
    else:
        abort(404)
