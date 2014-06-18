#!python3

from app import app
from views import *

if __name__ == '__main__':
    app.run(host='127.0.0.1',
            port=9000,
            debug=True)
