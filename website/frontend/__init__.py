from flask import Flask

import os
from .errors import init_error_handlers
from .babel import init_app

frontend_folder = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(frontend_folder, 'templates')
static_folder = os.path.join(frontend_folder, 'static')


def create_app():
    app = Flask(__name__, static_folder=static_folder,
                template_folder=template_folder)
    app.debug = True

    # Configuration files
    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'default_config.py'
    ))
    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'config.py'
    ), silent=True)

    # Error handling
    init_error_handlers(app)

    # I18n
    init_app(app)

    # Caching
    from cachelib import SimpleCache
    app.cache = SimpleCache()

    # Template utilities
    app.jinja_env.add_extension('jinja2.ext.do')

    from website.expand import expand
    app.jinja_env.filters['expand'] = expand

    # Blueprints
    from .views import frontend_bp
    from .views.changelog import changelog_bp
    from .views.humans import humans_bp
    from .views.plugins import plugins_bp
    from .views.docs import docs_bp
    from .views.api import api_bp

    app.register_blueprint(frontend_bp)
    app.register_blueprint(changelog_bp, url_prefix='/changelog')
    app.register_blueprint(humans_bp)
    app.register_blueprint(plugins_bp, url_prefix='/plugins')
    app.register_blueprint(docs_bp, url_prefix='/docs')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
