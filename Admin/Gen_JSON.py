import os
import re
import json
from subprocess import call
from hashlib import md5


def get_data(filePath):
    """
    Extract usable information from plugin files.
    """
    data = {}

    # Todo: Improve these?
    reName = re.compile(r'PLUGIN_NAME = u?((?:\"\"\"|\'\'\'|\"|\'))(.*)\1')
    reAuthor = re.compile(r'PLUGIN_AUTHOR = u?((?:\"\"\"|\'\'\'|\"|\'))(.*)\1')
    reVer = re.compile(r'PLUGIN_VERSION = u?((?:\"\"\"|\'\'\'|\"|\'))(.*?)\1')
    reAPI = re.compile(r'PLUGIN_API_VERSIONS = \[((?:\"\"\"|\'\'\'|\"|\'))(.*?)\1\]')

    # Descriptions are spread out in multiple lines
    # so these will require some special attention
    reDescStart = re.compile(r'PLUGIN_DESCRIPTION = u?(.*)')
    reDescEnd =  re.compile(r'PLUGIN_(.*)')
    reDesc = re.compile(r'PLUGIN_DESCRIPTION = u?((?:\"\"\"|\'\'\'|\"|\'))(.*?)\1', re.DOTALL)
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

            if 'desc' not in data:
                if re.match(reDescStart, line):
                    descFlag = True
                elif re.match(reDescEnd, line):
                    descFlag = False
                    desc = re.match(reDesc, re.sub(r'[\\\n]', '', "".join(descLines)))
                    if desc:
                        data['desc'] = desc.group(2)

                if descFlag:
                    descLines.append(line)

            if 'ver' not in data:
                ver = re.match(reVer, line)
                if ver:
                    data['ver'] = ver.group(2)

            if 'apiver' not in data:
                apiver = re.match(reAPI, line)
                if apiver:
                    data['apiver'] = apiver.group(2)

    return data


def build_json():
    """
    Traverse the plugins directory to generate json data.
    """

    for dirName in os.listdir(plug_dir):

        files = {}
        data = {}

        for fileName in os.listdir(os.path.join(plug_dir, dirName)):
            ext = os.path.splitext(fileName)[1]

            if ext not in [".pyc"]:
                filePath = os.path.join(plug_dir, dirName, fileName)
                md5Hash = md5(open(filePath, "rb").read()).hexdigest()
                files[fileName] = md5Hash

            if not data:
                data = get_data(os.path.join(plug_dir, dirName, fileName))

        found = False
        for p in plugins:
            if p["id"] == dirName:
                found = True
                break

        if found:
            print("Updating " + dirName)
            if data:
                for key, value in data.items():
                    p[key] = value
            p["files"] = files
        else:
            print("Adding " + dirName)
            data['id'] = dirName
            data['files'] = files
            data['downloads'] = 0
            plugins.append(data)

# The file that contains json data
plug_file = "Plugins.json"

# The directory which contains plugin files
plug_dir = "Plugins"

# Pull contents from Github
# call(["git", "pull", "-q"])

if os.path.isfile(plug_file):
    plugins = json.load(open(plug_file, "r"))["plugins"]
else:
    plugins = []

build_json()

# print(json.dumps({"plugins": plugins}, sort_keys=True, indent=2))
json.dump({"plugins": plugins}, open(plug_file, "w"), sort_keys=True, indent=2)
