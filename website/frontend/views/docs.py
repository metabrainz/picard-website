from website.frontend import template_folder
from flask import (
    Blueprint,
    abort,
    current_app as app,
    redirect,
    render_template,
)

import os

docs_bp = Blueprint('docs', __name__)


def redirect_docs(path):
    return redirect(app.config['DOCS_BASE_URL'] + path, code=301)

@docs_bp.get('/')
def show_docs():
    return redirect_docs('/')

@docs_bp.get('/basics/')
def show_basics():
    return redirect_docs('/en/introduction.html')

@docs_bp.get('/options/')
def show_options():
    return redirect_docs('/en/config/configuration.html')

@docs_bp.get('/faq/')
def show_faq():
    return redirect_docs('/en/faq/faq.html')

@docs_bp.get('/troubleshooting/')
def show_troubleshooting():
    return redirect_docs('/en/troubleshooting/troubleshooting.html')

@docs_bp.get('/scripting/')
def show_scripting():
    return redirect_docs('/en/scripting.html')

@docs_bp.get('/tags/')
def show_tags():
    return redirect_docs('/en/variables/variables.html')

@docs_bp.get('/mappings/')
def show_mappings():
    return redirect_docs('/en/appendices/tag_mapping.html')

@docs_bp.get('/plugin-api/')
def show_plugin_api():
    return redirect_docs('/en/appendices/plugins_api.html')

@docs_bp.get('/linux/')
def show_install_linux():
    return redirect_docs('/en/getting_started/download.html#installing-picard-on-linux')

@docs_bp.get('/build-osx/')
def show_build_osx():
    return redirect('https://github.com/metabrainz/picard/blob/master/INSTALL.md')

@docs_bp.get('/build-windows/')
def show_build_windows():
    return redirect('https://github.com/metabrainz/picard/blob/master/INSTALL.md')

@docs_bp.get('/<string:page>/')
def show_pages(page):
    if os.path.isfile(os.path.join(template_folder, 'docs', page + '.html')):
        return render_template('docs/' + page + '.html')
    else:
        abort(404)
