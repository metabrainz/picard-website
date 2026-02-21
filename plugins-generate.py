#!/usr/bin/env python

# Generate plugins.json and zipped plugin archive files
# Clone or pull repository from GitHub and run generate.py script


from website.build_plugins import generate_plugins
import website.frontend


config = website.frontend.create_app().config
versions = [z['title'] for z in config['PLUGIN_VERSIONS'].values()]
build_dir = config['PLUGINS_BUILD_DIR']
for version in versions:
    # Only generate for v1 and v2 - v3+ use remote registry
    if version not in ('1.0', '2.0'):
        print(f"Skipping version {version} (uses remote registry)")
        continue

    print(build_dir, version)
    try:
        generate_plugins(build_dir, version)
        print("Plugin files for version %s have been generated successfully." % version)
    except Exception as e:
        print("Plugin generation for version %s has FAILED.\nError occurred: %s" % (version, e))
