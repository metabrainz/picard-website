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
        'tag': '2.0.4',
        'version': (2, 0, 4, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://picard.musicbrainz.org/changelog/',
        },
        'win_size': '16.5',
        'win_hash': 'd25c7b98b01e92f61d01ce1ff0b0fa55',
        'mac_size': '20.8',
        'mac_hash': 'db4e411de57db3f405e91eedb1d77df9',
        'linux_size': '2.9',
        'linux_hash': '-',
    },
    'beta': {
        'tag': '2.0.0.beta3',
        'version': (2, 0, 0, 'dev', 6),
        'urls': {
            'download': 'https://github.com/metabrainz/picard/releases/tag/2.0.0dev6',
            'changelog': 'https://github.com/metabrainz/picard/compare/2.0.0dev6...master',
        }
    },
    'dev': {
        'tag': '2.0.5.dev1',
        'version': (2, 0, 5, 'dev', 1),
        'urls': {
            'download': 'https://github.com/metabrainz/picard',
        }
    },
}

CHANGELOG_URL = "https://raw.githubusercontent.com/musicbrainz/picard/master/NEWS.txt"
CHANGELOG_CACHE_TIMEOUT = 5 * 60

SUPPORTED_LANGUAGES = [
    'en',
    'fr',
]

SERVER_HOSTNAME = "127.0.0.1"
SERVER_PORT = 6060
