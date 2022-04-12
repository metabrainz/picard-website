from flask import (
    current_app,
    Blueprint,
    jsonify,
    make_response,
    request,
    send_from_directory
)

from website.plugin_utils import (
    load_json_data,
    plugins_dir
)

api_bp = Blueprint('api', __name__)


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
        return send_from_directory(
            plugins_dir(current_app, version),
            pid + ".zip",
            as_attachment=True,
            mimetype='application/zip')
    else:
        return not_found(404)


def get_build_version(app, version, key='title'):
    item = app.config['PLUGIN_VERSIONS'].get(version)
    if item and key is not None:
        return item.get(key)
    return item


def not_found(error):
    return make_response(jsonify({'error': 'Plugin not found.'}), 404)


def invalid_api_version(error):
    return make_response(jsonify({'error': 'Invalid API version'}), 404)


def picard_versions(app):
    return app.config['PICARD_VERSIONS']


@api_bp.get('/<version>/')
def api_root(version):
    """
    Shows info about our API
    """
    response = get_build_version(current_app, version, 'response')
    if response:
        return make_response(jsonify({'message': response}), 200)
    else:
        return invalid_api_version(404)


@api_bp.get('/<version>/plugins/')
def get_plugin(version):
    """
    Lists data of a plugin
    """
    build_version = get_build_version(current_app, version)
    if build_version:
        pid = request.args.get('id')
        return _get_plugin(current_app, build_version, pid)
    else:
        return invalid_api_version(404)


@api_bp.get('/<version>/download/')
def download_plugin(version):
    """
    Serves files as a download attachment.

    Single files are served as is, multiple ones are zipped.
    """
    build_version = get_build_version(current_app, version)
    if build_version:
        pid = request.args.get('id')
        if pid:
            return _download_plugin(current_app, build_version, pid)
        else:
            return make_response(
                jsonify({'error': 'Plugin id not specified.',
                         'message': 'Correct usage: /api/%s/download?id=<id>' % version}), 400)
    else:
        return invalid_api_version(404)


@api_bp.get('/v2/releases/')
def get_versions():
    """
    Provides latest version numbers and download urls for the release paths.

    One intended use for the new PW versions api endpoint is to provide the current
    available release information to Picard for automatic update checking (PICARD-1045).
    The proposed update checking flow within Picard would generally be:

      1. Check new configuration setting to determine the update level to process. The
         levels proposed are: 1 = Stable releases only; 2 = Stable and Beta releases;
         3 = Stable, Beta and Dev releases.

      2. Query the new PW api endpoint to get the latest available version information.
         The intent is that this would only occur once per Picard session, and the
         information would be stored in a temporary session variable in a new
         UpdateCheckManager class in case multiple (manual) update checks are performed
         during the session. The date of the latest successful call to the endpoint
         would be stored in a new persistent variable.

      3. Compare the version tuples for each of the update levels in the user's
         "subscription" (from Step 1) to determine the highest available version within
         the subscribed levels.

      4. Compare the highest available version from Step 3 to the currently running
         version of Picard. If a new version is available, open a dialog box informing
         the user, showing the current version and the available version number (tag),
         and provide an option to open the download url. If no update was available, and
         the update check was initiated manually, a dialog box would be displayed to
         inform the user that no update was available (based on their selected update
         level).

      5. Upon Picard start-up, a new configuration setting would be checked to determine
         whether automatic update checking is enabled. If enabled, the current date would
         be compared to the date of the last successful check (from the persistent
         variable stored during Step 2) to see whether or not it is within the number of
         days between automatic checks specified in another new configuration setting. If
         it's within the interval, no check is performed. If beyond the interval, a check
         would be performed but there will be no dialog box notification unless a newer
         version is available.

      6. There would be a new option on the Help portion of the main toolbar to allow the
         user to manually initiate an update check.

    In summary, it is proposed to add three new configuration settings to Picard:
    1) update level to check; 2) automatic update checking enabled; and 3) minimum
    interval (in days) between automatic update checks. It is also proposed to add one
    new persistent variable: date of last update check, one new start-up action:
    automatic update check, and one new toolbar action: manually check for updates.
    """
    ret_obj = {'versions': picard_versions(current_app)}
    return make_response(jsonify(ret_obj), 200)
