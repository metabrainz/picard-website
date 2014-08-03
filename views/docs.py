from app import app
from flask import render_template


@app.route('/docs/')
@app.route('/docs/basics/')
def show_docs():
    return render_template('docs/basics.html')
