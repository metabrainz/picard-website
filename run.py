#!/usr/bin/env python

from werkzeug.serving import run_simple
from website.frontend import create_app
from config import SERVER_HOSTNAME, SERVER_PORT

if __name__ == '__main__':
    run_simple(SERVER_HOSTNAME, SERVER_PORT, create_app())
