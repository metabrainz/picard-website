from flask import Blueprint, send_file

humans_bp = Blueprint('humans', __name__)


@humans_bp.route('/humans.txt')
def show_humans():
    return send_file('humans.txt')
