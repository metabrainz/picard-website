#!/usr/bin/env python

from werkzeug.serving import run_simple
from website.frontend import create_app

if __name__ == '__main__':
    app = create_app()
    run_simple(app.config['SERVER_HOSTNAME'], app.config['SERVER_PORT'], app)
