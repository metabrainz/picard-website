from flask import (
    jsonify,
    make_response,
    render_template,
    request,
)


_API_ROOT_PATHS = ["/api", "/api/"]


def init_error_handlers(app):
    @app.errorhandler(404)
    def not_found_handler(error):
        if request.path in _API_ROOT_PATHS:
            return make_response(jsonify({"message": "No API version specified"}), 404)

        return render_template('errors/404.html', error=error), 404
