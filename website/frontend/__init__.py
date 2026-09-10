import os

from flask import Flask

from .babel import init_app
from .errors import init_error_handlers
from .healthz import init_healthz
from .scheduler import init_scheduler


frontend_folder = os.path.dirname(os.path.abspath(__file__))
website_folder = os.path.dirname(frontend_folder)
template_folder = os.path.join(frontend_folder, 'templates')
static_folder = os.path.join(frontend_folder, 'static')


def _env_flag(name):
    """Return True/False if the env var is set to a recognised value, else None."""
    value = os.environ.get(name)
    if value is None:
        return None
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def create_app(config_overrides=None):
    app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)

    # Configuration files
    app.config.from_pyfile(os.path.join(website_folder, 'default_config.py'))
    app.config.from_pyfile(os.path.join(website_folder, 'config.py'), silent=True)

    # Apply config overrides (for testing)
    if config_overrides:
        app.config.update(config_overrides)

    # Debug mode is OFF by default (safe for production: no interactive
    # debugger on tracebacks, no verbose logging). Enable via the DEBUG config
    # value or, for docker deployments, the PICARD_WEBSITE_DEBUG env var, which
    # takes precedence when set.
    env_debug = _env_flag('PICARD_WEBSITE_DEBUG')
    if env_debug is not None:
        app.config['DEBUG'] = env_debug
    app.debug = app.config.get('DEBUG', False)

    # Error handling
    init_error_handlers(app)

    # I18n
    init_app(app)

    # Caching
    try:
        from cachelib import UWSGICache

        app.cache = UWSGICache()
    except (ModuleNotFoundError, RuntimeError):
        from cachelib import SimpleCache

        app.cache = SimpleCache()

    # Initialize scheduler
    init_scheduler(app)

    # Health check endpoint (/healthz)
    init_healthz(app)

    # Template utilities
    app.jinja_env.add_extension('jinja2.ext.do')

    from website.expand import expand

    app.jinja_env.filters['expand'] = expand

    # Blueprints
    from .views import frontend_bp
    from .views.api import api_bp
    from .views.changelog import changelog_bp
    from .views.docs import docs_bp
    from .views.humans import humans_bp
    from .views.plugins import plugins_bp

    app.register_blueprint(frontend_bp)
    app.register_blueprint(changelog_bp, url_prefix='/changelog')
    app.register_blueprint(humans_bp)
    app.register_blueprint(plugins_bp, url_prefix='/plugins')
    app.register_blueprint(docs_bp, url_prefix='/docs')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
