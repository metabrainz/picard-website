from app import app
from flask import (
    json,
    jsonify,
    make_response,
    request,
)

import os
import zipfile
import tempfile

# The file that contains json data
plugFile = "plugins.json"

# The directory which contains plugin files
plugDir = "plugins"

# Load JSON Data
with open(plugFile) as plugJson:
    plugins = json.load(plugJson)['plugins']


def increase_count(plugin):
    """
    Increments the download count and updates the json file.
    """
    plugin["downloads"] += 1
    with open(plugFile, "w") as plugJson:
        json.dump({'plugins': plugins}, plugJson, sort_keys=True, indent=2)


@app.route('/api/', methods=['GET'])
def api_root():
    """
    Shows info about our API
    """
    return make_response(
        jsonify({'message': 'The two endpoints currently available'
                 ' are /api/plugins and /api/download'}), 200)


@app.route('/api/plugins/', methods=['GET'])
def get_plugin():
    """
    Lists data of a plugin
    """

    pid = request.args.get('id', None)
    if pid:
        if pid in plugins:
            plugin = {'plugin': plugins[pid]}
        else:
            return not_found(404)
    else:
        # Show all the plugins if an id is not specified
        plugin = plugins

    return make_response(jsonify(plugin), 200)


@app.route('/api/download/', methods=['GET'])
def download_plugin():
    """
    Serves files as a download attachment.

    Single files are served as is, multiple ones are zipped.
    """

    pid = request.args.get('id', None)
    if pid:
        if pid in plugins:
            files = plugins[pid]['files']

            if len(files) == 1:
                fileName = list(files.keys())[0]
                filePath = os.path.join(plugDir, pid, fileName)

                response = make_response(open(filePath).read())
                response.headers["Content-Type"] = "application/python-py"
                response.headers["Content-Disposition"] = \
                    "attachment; filename=" + fileName
            else:
                with tempfile.SpooledTemporaryFile() as tmp:
                    with zipfile.ZipFile(tmp, "w") as archive:
                        for fileName in list(files.keys()):
                            filePath = os.path.join(plugDir, pid, fileName)
                            archive.write(filePath, fileName)

                    tmp.seek(0)
                    response = make_response(tmp.read())
                    response.headers["Content-Type"] = "application/zip"
                    response.headers["Content-Disposition"] = \
                        "attachment; filename=" + pid + ".zip"

            increase_count(plugins[pid])
            return response
        else:
            return not_found(404)
    else:
        return make_response(
            jsonify({'error': 'Plugin id not specified.',
                     'message': 'Correct usage: /api/download?id=<id>'}), 400)


def not_found(error):
    return make_response(jsonify({'error': 'Plugin not found.'}), 404)
