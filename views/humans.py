from app import app
from flask import send_file


@app.route('/humans.txt')
def show_humans():
    return send_file('humans.txt')
