#!python3

import os
import zipfile
import tempfile
from flask import (
    Flask,
    json,
    jsonify,
    make_response,
    request,
)

app = Flask(__name__)


def find_plugin(pid):
    """
    Finds a plugin with the specified id.
    """
    plugin = list(filter(lambda t: t['id'] == str(pid), plugins['plugins']))

    if plugin:
        return plugin[0]
    else:
        return None


def increase_count(plugin):
    """
    Increments the download count and updates the json file.
    """
    plugin["downloads"] += 1
    json.dump(plugins, open(plug_file, "w"), sort_keys=True, indent=2)


@app.route('/plugins', methods=['GET'])
def get_plugin():
    """
    Lists data of a plugin
    """

    pid = request.args.get('id', None)
    if pid:
        if find_plugin(pid):
            plugin = {'plugin': find_plugin(pid)}
        else:
            return not_found(404)
    else:
        plugin = plugins

    return jsonify(plugin)


@app.route('/download', methods=['GET'])
def download_plugin():
    """
    Serves files as a download attachment.

    Single files are served as is, multiple ones are zipped.
    """

    pid = request.args.get('id', None)
    if pid:
        if find_plugin(pid):
            files = find_plugin(pid)['files']

            if len(files) == 1:
                fileName = list(files.keys())[0]
                filePath = os.path.join(plug_dir, pid, fileName)

                response = make_response(open(filePath).read())
                response.headers["Content-Type"] = "application/python-py"
                response.headers["Content-Disposition"] = \
                    "attachment; filename=" + fileName
            else:
                with tempfile.SpooledTemporaryFile() as tmp:
                    with zipfile.ZipFile(tmp, "w") as archive:
                        for fileName in list(files.keys()):
                            filePath = os.path.join(plug_dir, pid, fileName)
                            archive.write(filePath, fileName)

                    tmp.seek(0)
                    response = make_response(tmp.read())
                    response.headers["Content-Type"] = "application/zip"
                    response.headers["Content-Disposition"] = \
                        "attachment; filename=" + pid + ".zip"

            increase_count(find_plugin(pid))
            return response
        else:
            return not_found(404)
    else:
        return make_response(jsonify({'error': 'Plugin id not specified.'}),
                             400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Plugin not found.'}),
                         404)

# The file that contains json data
plug_file = "Plugins.json"

# The directory which contains plugin files
plug_dir = "Plugins"

# Load JSON Data
plugins = json.load(open(plug_file))

if __name__ == '__main__':
    app.run(debug=True)
