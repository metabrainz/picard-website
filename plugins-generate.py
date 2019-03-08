#!/usr/bin/env python

# Generate plugins.json and zipped plugin archive files
# Clone or pull repository from GitHub and run generate.py script


import website.frontend
from website.build_plugins import generate_plugins


config = website.frontend.create_app().config
versions = [z['title'] for z in config['PLUGIN_VERSIONS'].values()]
build_dir = config['PLUGINS_BUILD_DIR']
for version in versions:
    print(build_dir, version)
    try:
        generate_plugins(build_dir, version)
        print("Plugin files for version %s have been generated successfully." % version)
    except Exception as e:
        print("Plugin generation for version %s has FAILED.\nError Occured: %s" % (version, e))
