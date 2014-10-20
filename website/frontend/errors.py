from flask import (
    jsonify,
    make_response,
    render_template,
    request
)


def init_error_handlers(app):

    @app.errorhandler(404)
    def not_found_handler(error):
        if request.path.startswith("/api"):
            return make_response(
                jsonify({"message": "The two endpoints currently available"
                        " are /api/v1/plugins and /api/v1/download"}), 404)

        return render_template('errors/404.html', error=error), 404
