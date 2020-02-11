# This configuration is for production / docker
# You need to copy config.py.example to config.py and edit the file to your own needs
# to override these values.
PLUGINS_BUILD_DIR = "/code/plugins"
PLUGINS_CACHE_TIMEOUT = 5 * 60
# Flask automatically orders them in ascending order while
# retrieveing them. Since it is a string comparison, v10 appears before
# v2. So be careful with the ordering.
PLUGIN_VERSIONS = {
    'v1': {
        'title': '1.0',
        'response': 'The endpoints currently available for this api version' \
                ' are /api/v1/plugins and /api/v1/download',
    },
    'v2': {
        'title': '2.0',
        'response': 'The endpoints currently available for this api version' \
                ' are /api/v2/plugins, /api/v2/download and /api/v2/releases',
    },
}

# PICARD_VERSIONS dictionary valid keys are: 'stable', 'beta' and 'dev'.
# The 'version' tuple comprises int_major, int_minor, int_micro, str_type and int_development as defined in PEP-440.
# The Picard developers have standardized on using only 'dev' or 'final' as the str_type segment of the version tuple.
PICARD_VERSIONS = {
    'stable': {
        'tag': '2.2.3',
        'version': (2, 2, 3, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://picard.musicbrainz.org/changelog/',
        },
        'win_size': '29',
        'win_hash': '7a83feca8cac70b55d5c7e3dd222cbec',
        'mac_size': '30',
        'mac_hash': 'cd3e31b9e559bd018dc30cea60e7606b',
        'linux_size': '3.1',
        'linux_hash': '-',
    },
    'beta': {
        'tag': '2.3.0rc1',
        'version': (2, 3, 0, 'rc', 1),
        'urls': {
            'download': 'https://github.com/metabrainz/picard/releases/tag/release-2.3.0rc1',
            'changelog': 'https://blog.metabrainz.org/2020/02/11/picard-2-3-release-candidate/',
        }
    },
    'dev': {
        'tag': '2.3.0rc1',
        'version': (2, 3, 0, 'rc', 1),
        'urls': {
            'download': 'https://github.com/metabrainz/picard/releases/tag/release-2.3.0rc1',
        }
    },
}

CHANGELOG_URL = "https://raw.githubusercontent.com/musicbrainz/picard/master/NEWS.md"
CHANGELOG_CACHE_TIMEOUT = 5 * 60

SUPPORTED_LANGUAGES = [
    'en',
    'fr',
]

SERVER_HOSTNAME = "127.0.0.1"
SERVER_PORT = 6060
