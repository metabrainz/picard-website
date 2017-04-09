# -*- coding: utf-8 -*-

import ast
import os
import json
import shutil
import zipfile

from hashlib import md5
from tempfile import mkdtemp
# for Py2/3 compatibility
try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve

PLUGIN_DOWNLOAD_URL = "https://github.com/metabrainz/picard-plugins/archive/%s.zip"

# The file that contains json data
PLUGIN_FILE_NAME = "plugins.json"

# The directory that contains the plugin files in upstream
PLUGIN_DIR = "plugins"

VERSION_TO_BRANCH = {
    None: 'master',
    '1.0': 'master',
    '2.0': '2.0',
}

KNOWN_DATA = [
    'PLUGIN_NAME',
    'PLUGIN_AUTHOR',
    'PLUGIN_VERSION',
    'PLUGIN_API_VERSIONS',
    'PLUGIN_LICENSE',
    'PLUGIN_LICENSE_URL',
    'PLUGIN_DESCRIPTION',
]


def get_plugin_data(filepath):
    """Parse a python file and return a dict with plugin metadata"""
    data = {}
    with open(filepath, 'rU') as plugin_file:
        source = plugin_file.read()
        try:
            root = ast.parse(source, filepath)
        except Exception:
            print("Cannot parse " + filepath)
            raise
        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if (isinstance(target, ast.Name)
                    and isinstance(target.ctx, ast.Store)
                        and target.id in KNOWN_DATA):
                    name = target.id.replace('PLUGIN_', '', 1).lower()
                    if name not in data:
                        try:
                            data[name] = ast.literal_eval(node.value)
                        except ValueError:
                            print('Cannot evaluate value in '
                                  + filepath + ':' +
                                  ast.dump(node))
        return data


def build_json(source_dir, dest_dir):
    """Traverse the plugins directory to generate json data."""

    plugins = {}

    # All top level directories in source_dir are plugins
    for dirname in next(os.walk(source_dir))[1]:

        files = {}
        data = {}

        if dirname in [".git"]:
            continue

        dirpath = os.path.join(source_dir, dirname)
        for root, dirs, filenames in os.walk(dirpath):
            for filename in filenames:
                ext = os.path.splitext(filename)[1]

                if ext not in [".pyc"]:
                    file_path = os.path.join(root, filename)
                    with open(file_path, "rb") as md5file:
                        md5Hash = md5(md5file.read()).hexdigest()
                    files[file_path.split(os.path.join(dirpath, ''))[1]] = md5Hash

                    if ext in ['.py'] and not data:
                        data = get_plugin_data(os.path.join(source_dir, dirname, filename))

        if files and data:
            print("Added: " + dirname)
            data['files'] = files
            plugins[dirname] = data
    out_path = os.path.join(dest_dir, PLUGIN_FILE_NAME)
    with open(out_path, "w") as out_file:
        json.dump({"plugins": plugins}, out_file, sort_keys=True, indent=2)


def zip_files(source_dir, dest_dir):
    """Zip up plugin folders"""

    for dirname in next(os.walk(source_dir))[1]:
        archive_path = os.path.join(dest_dir, dirname)
        archive = zipfile.ZipFile(archive_path + ".zip", "w")

        dirpath = os.path.join(source_dir, dirname)
        plugin_files = []

        for root, dirs, filenames in os.walk(dirpath):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                plugin_files.append(file_path)

        if len(plugin_files) == 1:
            # There's only one file, put it directly into the zipfile
            archive.write(plugin_files[0],
                          os.path.basename(plugin_files[0]),
                          compress_type=zipfile.ZIP_DEFLATED)
        else:
            for filename in plugin_files:
                # Preserve the folder structure relative to source_dir
                # in the zip file
                name_in_zip = os.path.join(os.path.relpath(filename,
                                                           source_dir))
                archive.write(filename,
                              name_in_zip,
                              compress_type=zipfile.ZIP_DEFLATED)

        print("Created: " + dirname + ".zip")


def download_plugins(version=None):
    """Downloads and extracts the plugin source files"""
    temp_dir = mkdtemp(suffix="PICARD-WEBSITE")
    source_path = os.path.join(temp_dir, version or '')
    zip_path = source_path + ".zip"

    download_url = PLUGIN_DOWNLOAD_URL % (VERSION_TO_BRANCH[version])
    print("Downloading files. Please wait....")
    urlretrieve(download_url, zip_path)

    zip_file = zipfile.ZipFile(zip_path)
    zip_file.extractall(source_path)

    source_dir = os.path.join(source_path, zip_file.namelist()[0], PLUGIN_DIR)
    return temp_dir, source_dir


def generate_plugins(build_dir, version=None, json=True, zips=True):
    """Download and generate plugin build files for a given version"""
    dest_dir = os.path.abspath(os.path.join(build_dir, version or ''))
    temp_dir, source_dir = download_plugins(version)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    if json:
        build_json(source_dir, dest_dir)
    if zips:
        zip_files(source_dir, dest_dir)

    shutil.rmtree(temp_dir)
