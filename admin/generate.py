#!/home/dufferzafar/picard-website/env/bin/python

import os
import re
import sys
import json

import zipfile
import zlib

from hashlib import md5
from subprocess import call

reName = re.compile(r'PLUGIN_NAME = (?:_\(u|u)((?:\"\"\"|\'\'\'|\"|\'))(.*)\1')
reAuthor = re.compile(r'PLUGIN_AUTHOR = (?:_\(u|u)((?:\"\"\"|\'\'\'|\"|\'))(.*)\1')
reVer = re.compile(r'PLUGIN_VERSION = (?:_\(u|u)((?:\"\"\"|\'\'\'|\"|\'))(.*?)\1')
reAPI = re.compile(r'PLUGIN_API_VERSIONS = \[((?:\"\"\"|\'\'\'|\"|\'))(.*?)\1\]')

# Descriptions are spread out in multiple lines so these will be handled separately
reDescStart = re.compile(r'PLUGIN_DESCRIPTION = (?:_\(u|u)(.*)')
reDescEnd = re.compile(r'PLUGIN_(.*)')
reDesc = re.compile(r'PLUGIN_DESCRIPTION = (?:_\(u|u)((?:\"\"\"|\'\'\'|\"|\'))(.*?)\1', re.DOTALL)


def get_data(filePath):
    """
    Extract usable information from plugin files.
    """
    data = {}
    descLines = []
    descFlag = False

    with open(filePath) as f:
        for line in f:
            if 'name' not in data:
                name = re.match(reName, line)
                if name:
                    data['name'] = name.group(2)

            if 'author' not in data:
                author = re.match(reAuthor, line)
                if author:
                    data['author'] = author.group(2)

            if 'description' not in data:
                if re.match(reDescStart, line):
                    descFlag = True
                elif re.match(reDescEnd, line):
                    descFlag = False
                    desc = re.match(reDesc, re.sub(r'[\\\n]', '', "".join(descLines)))
                    if desc:
                        data['description'] = desc.group(2)

                if descFlag:
                    descLines.append(line)

            if 'version' not in data:
                ver = re.match(reVer, line)
                if ver:
                    data['version'] = ver.group(2)

            if 'api_version' not in data:
                apiver = re.match(reAPI, line)
                if apiver:
                    data['api_version'] = apiver.group(2)

    return data


def build_json():
    """
    Traverse the plugins directory to generate json data.
    """

    # Read the existing data
    if os.path.isfile(plugFile):
        plugins = json.load(open(plugFile, "r"))["plugins"]
    else:
        plugins = {}

    # All top level directories in plugDir are plugins
    for dirName in os.walk(plugDir).next()[1]:

        files = {}
        data = {}

        if dirName in [".git"]:
            continue

        dirPath = os.path.join(plugDir, dirName)
        for root, dirs, fileNames in os.walk(dirPath):
            for fileName in fileNames:
                ext = os.path.splitext(fileName)[1]

                if ext not in [".pyc"]:
                    filePath = os.path.join(root, fileName)
                    md5Hash = md5(open(filePath, "rb").read()).hexdigest()
                    files[filePath.split(os.path.join(dirPath, ''))[1]] = md5Hash

                if not data:
                    data = get_data(os.path.join(plugDir, dirName, fileName))

        if dirName in plugins:
            print("Updating " + dirName)
            if data:
                for key, value in data.items():
                    plugins[dirName][key] = value
            plugins[dirName]["files"] = files
        else:
            print("Adding " + dirName)
            data['files'] = files
            data['downloads'] = 0
            plugins[dirName] = data

    json.dump({"plugins": plugins}, open(plugFile, "w"),
              sort_keys=True, indent=2)


def zip_files():
    """
    Zip up plugin folders
    """

    for dirName in os.walk(plugDir).next()[1]:
        archivePath = os.path.join(plugDir, dirName)
        archive = zipfile.ZipFile(archivePath + ".zip", "w")

        dirPath = os.path.join(plugDir, dirName)
        for root, dirs, fileNames in os.walk(dirPath):
            for fileName in fileNames:
                filePath = os.path.join(root, fileName)
                archive.write(filePath,
                              filePath.split(os.path.join(dirPath, ''))[1],
                              compress_type=zipfile.ZIP_DEFLATED)

        print("Created archive: " + dirName)


# The file that contains json data
plugFile = "../plugins.json"

# The directory which contains plugin files
plugDir = "../picard-plugins/plugins"

if __name__ == '__main__':
    if 1 in sys.argv:
        if sys.argv[1] == "pull":
            call(["git", "pull", "-q"])
        elif sys.argv[1] == "json":
            build_json()
        elif sys.argv[1] == "zip":
            zip_files()
    else:
            # call(["git", "pull", "-q"])
            build_json()
            zip_files()
