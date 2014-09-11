from flask import Flask

import os

frontend_folder = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(frontend_folder, 'templates')
static_folder = os.path.join(frontend_folder, 'static')

def create_app():
    app = Flask(__name__, static_folder=static_folder,
                template_folder=template_folder)
    app.debug = True

    # Configuration files
    import website.default_config
    app.config.from_object(website.default_config)
    app.config.from_object('website.config')

    # Error handling
    import errors
    errors.init_error_handlers(app)

    # Caching
    from werkzeug.contrib.cache import SimpleCache
    app.cache = SimpleCache()

    # Template utilities
    import re

    def re_sub(string, find, replace):
        return re.sub(find, replace, string)

    def re_search(string, pattern):
        return re.search(pattern, string)

    def version(string, group):
        return re.match(r"^Version\s+(.*?)\s+-\s+(.*?)$", string).group(group)

    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.tests['re_search'] = re_search
    app.jinja_env.filters['re_sub'] = re_sub
    app.jinja_env.filters['version'] = version

    # Blueprints
    from views import frontend_bp
    from views.changelog import changelog_bp
    from views.humans import humans_bp
    from views.plugins import plugins_bp
    from views.docs import docs_bp
    from views.api import api_bp


    app.register_blueprint(frontend_bp)
    app.register_blueprint(changelog_bp, url_prefix='/changelog')
    app.register_blueprint(humans_bp)
    app.register_blueprint(plugins_bp, url_prefix='/plugins')
    app.register_blueprint(docs_bp, url_prefix='/docs')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
