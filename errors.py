from app import app
from flask import (
    jsonify,
    make_response,
    render_template,
    request
)


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api"):
        return make_response(
            jsonify({"message": "The two endpoints currently available"
                     " are /api/v1/plugins and /api/v1/download"}), 404)
    else:
        return make_response(render_template('404.html'), 404)
