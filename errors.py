from app import app
from flask import make_response

# Todo: Add a 404 page
@app.errorhandler(404)
def not_found(error):
    return make_response('404 Page not found.', 404)

