#!/usr/bin/env python

from website.frontend import create_app
from werkzeug.serving import run_simple


app = create_app()

if __name__ == '__main__':
    run_simple(app.config['SERVER_HOSTNAME'], app.config['SERVER_PORT'], app)
