from app import app

from flask import render_template

@app.route('/')
def show_index():
    return render_template('index.html')


@app.route('/downloads/')
def show_downloads():
    return render_template('downloads.html')


@app.route('/changelog/')
def show_changelog():
    return render_template('changelog.html')


@app.route('/plugins/')
def show_plugins():
    return render_template('plugins.html')
