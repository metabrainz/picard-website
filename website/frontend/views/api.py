import os
from flask import (
    current_app,
    Blueprint,
    json,
    jsonify,
    make_response,
    request,
    send_from_directory
)

api_bp = Blueprint('api', __name__)


def plugins_repository(app):
    return app.config['PLUGINS_REPOSITORY']


def plugins_json_file(app):
    """Returns the file that contains json data"""
    return os.path.join(plugins_repository(app), "plugins.json")


def plugins_dir(app):
    """Returns the directory which contains plugin files"""
    return os.path.join(plugins_repository(app), "plugins")


def load_json_data(app):
    """Load JSON Data"""
    key = 'plugins_json_data'
    data = app.cache.get(key)
    if data is None:
        with open(plugins_json_file(app)) as fp:
            data = json.load(fp)['plugins']
            app.cache.set(key, data,
                          timeout=app.config['PLUGINS_CACHE_TIMEOUT'])
    return data


def _get_plugin(app, pid=None):
    plugins = load_json_data(app)
    if pid:
        if pid in plugins:
            plugin = {'plugin': plugins[pid]}
        else:
            return not_found(404)
    else:
        # Show all the plugins if an id is not specified
        plugin = {'plugins': plugins}
    return make_response(jsonify(plugin), 200)


def _download_plugin(app, pid):
    plugins = load_json_data(current_app)
    if pid in plugins:
        return send_from_directory(plugins_dir(current_app), pid + ".zip", as_attachment=True)
    else:
        return not_found(404)


def not_found(error):
    return make_response(jsonify({'error': 'Plugin not found.'}), 404)


@api_bp.route('/v1/', methods=['GET'])
def api_root():
    """
    Shows info about our API
    """
    return make_response(
        jsonify({'message': 'The two endpoints currently available'
                 ' are /api/v1/plugins and /api/v1/download'}), 200)


@api_bp.route('/v1/plugins/', methods=['GET'])
def get_plugin():
    """
    Lists data of a plugin
    """

    pid = request.args.get('id', None)
    return _get_plugin(current_app, pid)


@api_bp.route('/v1/download/', methods=['GET'])
def download_plugin():
    """
    Serves files as a download attachment.

    Single files are served as is, multiple ones are zipped.
    """

    pid = request.args.get('id', None)
    if pid:
        return _download_plugin(current_app, pid)
    else:
        return make_response(
            jsonify({'error': 'Plugin id not specified.',
                     'message': 'Correct usage: /api/v1/download?id=<id>'}), 400)
