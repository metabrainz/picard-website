# This configuration is for production / docker
# You need to copy config.py.example to config.py and edit the file to your own needs
# to override these values.
PLUGINS_BUILD_DIR = "/code/plugins"
PLUGINS_CACHE_TIMEOUT = 5 * 60
# Flask automatically orders them in ascending order while
# retrieveing them. Since it is a string comparison, v10 appears before
# v2. So be careful with the ordering.
PLUGIN_VERSIONS = {
    'v1': '1.0',
    'v2': '2.0',
}
PICARD_VERSIONS = {
    'stable': ('1.4.2', 'http://picard.musicbrainz.org/'),
    'beta': ('2.0.0.beta1', 'https://github.com/metabrainz/picard/releases/tag/2.0.0.dev4'),
    'dev': ('2.0.0.dev4', 'https://github.com/metabrainz/picard/releases/tag/2.0.0.dev4'),
}
CHANGELOG_URL = "https://raw.githubusercontent.com/musicbrainz/picard/master/NEWS.txt"
CHANGELOG_CACHE_TIMEOUT = 5 * 60

SUPPORTED_LANGUAGES = [
    'en',
    'fr',
]

SERVER_HOSTNAME = "127.0.0.1"
SERVER_PORT = 6060
