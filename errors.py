from app import app
from flask import (
    make_response,
    render_template
)


@app.errorhandler(404)
def not_found(error):
    return make_response(render_template('404.html'), 404)
