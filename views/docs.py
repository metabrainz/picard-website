from app import app
from flask import (
    render_template,
    abort
)

import os

@app.route('/docs/')
def show_basics():
    return render_template('docs/basics.html')

@app.route('/docs/<string:page>/')
def show_pages(page):
    if os.path.isfile('templates/docs/' + page + '.html'):
        return render_template('docs/' + page + '.html')
    else:
        abort(404)
