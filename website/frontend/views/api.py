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


def plugins_build_dir(app):
    return app.config['PLUGINS_BUILD_DIR']


def plugins_json_file(app, version):
    """Returns the file that contains json data"""
    return os.path.join(plugins_build_dir(app), version, "plugins.json")


def plugins_dir(app, version):
    """Returns the directory which contains plugin files"""
    return os.path.join(plugins_build_dir(app), version)


def load_json_data(app, version):
    """Load JSON Data"""
    key = 'plugins_json_data_%s' % version
    data = app.cache.get(key)
    if data is None:
        with open(plugins_json_file(app, version)) as fp:
            data = json.load(fp)['plugins']
            app.cache.set(key, data,
                          timeout=app.config['PLUGINS_CACHE_TIMEOUT'])
    return data


def _get_plugin(app, version, pid=None):
    plugins = load_json_data(app, version)
    if pid:
        if pid in plugins:
            plugin = {'plugin': plugins[pid]}
        else:
            return not_found(404)
    else:
        # Show all the plugins if an id is not specified
        plugin = {'plugins': plugins}
    return make_response(jsonify(plugin), 200)


def _download_plugin(app, version, pid):
    plugins = load_json_data(current_app, version)
    if pid in plugins:
        return send_from_directory(plugins_dir(current_app, version), pid + ".zip", as_attachment=True)
    else:
        return not_found(404)


def get_build_version(app, version):
    return app.config['PLUGIN_VERSIONS'].get(version)


def not_found(error):
    return make_response(jsonify({'error': 'Plugin not found.'}), 404)


def invalid_api_version(error):
    return make_response(jsonify({'error': 'Invalid API version'}), 404)


@api_bp.route('/<version>/', methods=['GET'])
def api_root(version):
    """
    Shows info about our API
    """
    if version and get_build_version(current_app, version):
        return make_response(
            jsonify({'message': 'The two endpoints currently available for this api version'
                     ' are /api/%s/plugins and /api/%s/download' % (version, version)}), 200)
    else:
        return invalid_api_version(404)


@api_bp.route('/<version>/plugins/', methods=['GET'])
def get_plugin(version):
    """
    Lists data of a plugin
    """
    build_version = get_build_version(current_app, version)
    if build_version:
        pid = request.args.get('id', None)
        return _get_plugin(current_app, build_version, pid)
    else:
        return invalid_api_version(404)


@api_bp.route('/<version>/download/', methods=['GET'])
def download_plugin(version):
    """
    Serves files as a download attachment.

    Single files are served as is, multiple ones are zipped.
    """
    build_version = get_build_version(current_app, version)
    if build_version:
        pid = request.args.get('id', None)
        if pid:
            return _download_plugin(current_app, build_version, pid)
        else:
            return make_response(
                jsonify({'error': 'Plugin id not specified.',
                         'message': 'Correct usage: /api/v1/download?id=<id>'}), 400)
    else:
        return invalid_api_version(404)
