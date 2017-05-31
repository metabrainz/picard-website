# -*- coding: utf-8 -*-

import ast
import os
import subprocess
import json
import re
import shutil
import zipfile

from hashlib import md5
from tempfile import mkdtemp
from datetime import datetime, timedelta
from email.utils import parsedate_tz, mktime_tz
# for Py2/3 compatibility
try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve

PLUGIN_GIT_URL = "https://github.com/metabrainz/picard-plugins.git"

# The file that contains json data
PLUGIN_FILE_NAME = "plugins.json"

# The directory that contains the plugin files in upstream
PLUGIN_DIR = "plugins"

VERSION_INFO = {
    None: {'branch_name': 'master'},
    '1.0': {'branch_name': '1.0',
            'api_versions':  # Keep those ordered
            [
                "0.15.0",
                "0.15.1",
                "0.16.0",
                "1.0.0",
                "1.1.0",
                "1.2.0",
                "1.3.0",
                "1.4.0",
            ]
            },
    '2.0': {'branch_name': '2.0',
            'api_versions':  # Keep those ordered
            [
                "2.0",
            ]
            }
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

_version_re = re.compile(r"(\d+)[._](\d+)(?:[._](\d+)[._]?(?:(dev|final)[._]?(\d+))?)?$")


class VersionError(Exception):
    pass


def datetime_rfc_to_iso(datetime_str):
    """Parse a RFC2822 datetime string and convert it to ISO8601 datetime in UTC"""
    timestamp = mktime_tz(parsedate_tz('Wed, 24 May 2017 12:04:14 +0200'))
    utc_time = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
    return str(utc_time)


def version_from_string(version_str):
    m = _version_re.search(version_str)
    if m:
        g = m.groups()
        if g[2] is None:
            return (int(g[0]), int(g[1]), 0, 'final', 0)
        if g[3] is None:
            return (int(g[0]), int(g[1]), int(g[2]), 'final', 0)
        return (int(g[0]), int(g[1]), int(g[2]), g[3], int(g[4]))
    raise VersionError("String '%s' does not match regex '%s'" % (version_str,
                                                                  _version_re.pattern))


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
        if data:
            last_modified = subprocess.check_output(['git', 'log', '-1', '--format=%aD'],
                                                    cwd=os.path.dirname(filepath))
            data['last_modified'] = datetime_rfc_to_iso(last_modified.rstrip())

        return data


def build_json(source_dir, dest_dir, supported_versions=None):
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
            if ((supported_versions
                 and set(map(version_from_string, data['api_versions'])) & set(supported_versions))
                 or not supported_versions):
                print("Added: " + dirname)
                data['files'] = files
                plugins[dirname] = data
    out_path = os.path.join(dest_dir, PLUGIN_FILE_NAME)
    with open(out_path, "w") as out_file:
        json.dump({"plugins": plugins}, out_file, sort_keys=True, indent=2)


def get_valid_plugins(dest_dir):
    plugin_file = os.path.join(dest_dir, PLUGIN_FILE_NAME)
    if os.path.exists(plugin_file):
        with open(os.path.join(dest_dir, PLUGIN_FILE_NAME)) as f:
            plugin_data = json.loads(f.read())
            return list(plugin_data['plugins'].keys())


def zip_files(source_dir, dest_dir):
    """Zip up plugin folders"""
    valid_plugins = get_valid_plugins(dest_dir)

    for dirname in next(os.walk(source_dir))[1]:
        if ((valid_plugins and dirname in valid_plugins)
            or not valid_plugins):
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

    print("Downloading files. Please wait....")
    subprocess.call(['git', 'clone', PLUGIN_GIT_URL, source_path])
    subprocess.call(['git', 'checkout', VERSION_INFO[version]['branch_name']], cwd=source_path)

    source_dir = os.path.join(source_path, PLUGIN_DIR)
    return temp_dir, source_dir


def generate_plugins(build_dir, version=None, json=True, zips=True):
    """Download and generate plugin build files for a given version"""
    # Return if both are False
    if not (json or zips):
        return
    dest_dir = os.path.abspath(os.path.join(build_dir, version or ''))
    supported_versions = [version_from_string(v) for v in VERSION_INFO[version].get('api_versions')]
    try:
        temp_dir, source_dir = download_plugins(version)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        if json:
            build_json(source_dir, dest_dir, supported_versions)
        if zips:
            zip_files(source_dir, dest_dir)
    except Exception as e:
        raise e
    finally:
        try:
            shutil.rmtree(temp_dir)
        except OSError:
            pass
