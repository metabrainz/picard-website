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
        'tag': '2.4.4',
        'version': (2, 4, 4, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://picard.musicbrainz.org/changelog/',
        },
        'win_size': '30',
        'win_hash': 'bf370dc3d9d1ea91ec98f6f468c05a85',
        'win_portable_size': '43',
        'win_portable_hash': 'dba7ebecf7e129053c74e259b930ad25',
        'mac_size': '32',
        'mac_hash': '06c6507dda30a7cc050028a832b9761f',
        'linux_size': '4.0',
        'linux_hash': '-',
    },
    'beta': {
        'tag': '2.5.0b1',
        'version': (2, 5, 0, 'beta', 1),
        'urls': {
            'download': 'https://picard.musicbrainz.org/downloads/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.5.0b1',
        },
        'win_size': '30',
        'win_hash': 'fe8edd71729615ab0ec1f562301e1769',
        'win_portable_size': '43',
        'win_portable_hash': '1ece60f5d5321e643ea93c348a2beaf3',
        'mac_size': '32',
        'mac_hash': '5ad223c9008efb3f86a79349d9505cef',
        'linux_size': '4.0',
        'linux_hash': '-',
    },
    'dev': {
        'tag': '2.5.0b1',
        'version': (2, 5, 0, 'beta', 1),
        'urls': {
            'download':
            'https://github.com/metabrainz/picard/releases/tag/release-2.5.0b1',
        }
    },
}

DOCS_BASE_URL = "https://picard-docs.musicbrainz.org"
CHANGELOG_URL = "https://raw.githubusercontent.com/musicbrainz/picard/master/NEWS.md"
CHANGELOG_CACHE_TIMEOUT = 5 * 60

SUPPORTED_LANGUAGES = [
    'en',
    'fr',
]

SERVER_HOSTNAME = "127.0.0.1"
SERVER_PORT = 6060
