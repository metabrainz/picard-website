import os
import re
import json
from subprocess import call
from hashlib import md5

reName = re.compile(r'PLUGIN_NAME = u?((?:\"\"\"|\'\'\'|\"|\'))(.*)\1')
reAuthor = re.compile(r'PLUGIN_AUTHOR = u?((?:\"\"\"|\'\'\'|\"|\'))(.*)\1')
reVer = re.compile(r'PLUGIN_VERSION = u?((?:\"\"\"|\'\'\'|\"|\'))(.*?)\1')
reAPI = re.compile(r'PLUGIN_API_VERSIONS = \[((?:\"\"\"|\'\'\'|\"|\'))(.*?)\1\]')

# Descriptions are spread out in multiple lines so these will be handled separately
reDescStart = re.compile(r'PLUGIN_DESCRIPTION = u?(.*)')
reDescEnd =  re.compile(r'PLUGIN_(.*)')
reDesc = re.compile(r'PLUGIN_DESCRIPTION = u?((?:\"\"\"|\'\'\'|\"|\'))(.*?)\1', re.DOTALL)

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

    for dirName in os.listdir(plugDir):

        files = {}
        data = {}

        for fileName in os.listdir(os.path.join(plugDir, dirName)):
            ext = os.path.splitext(fileName)[1]

            if ext not in [".pyc"]:
                filePath = os.path.join(plugDir, dirName, fileName)
                md5Hash = md5(open(filePath, "rb").read()).hexdigest()
                files[fileName] = md5Hash

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

# The file that contains json data
plugFile = "plugins.json"

# The directory which contains plugin files
plugDir = "plugins"

# Pull contents from Github
# call(["git", "pull", "-q"])

# Read the existing data
if os.path.isfile(plugFile):
    plugins = json.load(open(plugFile, "r"))["plugins"]
else:
    plugins = {}

build_json()

# print(json.dumps({"plugins": plugins}, sort_keys=True, indent=2))
json.dump({"plugins": plugins}, open("plugins.json", "w"), sort_keys=True, indent=2)
