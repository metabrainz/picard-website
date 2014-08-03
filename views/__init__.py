from app import app
from flask import render_template

from .changelog import *
from .plugins import *
from .docs import *
from .api import *


@app.route('/')
def show_index():
    return render_template('index.html')


@app.route('/downloads/')
def show_downloads():
    return render_template('downloads.html')
