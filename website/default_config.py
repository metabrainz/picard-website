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
        'tag': '2.4',
        'version': (2, 4, 0, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://picard.musicbrainz.org/changelog/',
        },
        'win_size': '30',
        'win_hash': 'ed0e4fb99bed5992bd4db9297a1bcd1c',
        'win_portable_size': '43',
        'win_portable_hash': '6aa50e9d71352764d2269bdb96fd1fce',
        'mac_size': '32',
        'mac_hash': '7426da5283014b06e4a40bcbd8a485e7',
        'linux_size': '4.0',
        'linux_hash': '-',
    },
    'beta': {
        'tag': '2.4.0b2',
        'version': (2, 4, 0, 'beta', 2),
        'urls': {
            'download': 'https://picard.musicbrainz.org/downloads/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.4.0b2',
        },
        'win_size': '30',
        'win_hash': '083e001ca516e268d5b0473f93ac1e23',
        'win_portable_size': '43',
        'win_portable_hash': '34deae4084c57a9cd96745bf9349b4c0',
        'mac_size': '32',
        'mac_hash': '55f553a0e674795e5227fee768ed5acc',
        'linux_size': '3.9',
        'linux_hash': '-',
    },
    'dev': {
        'tag': '2.4.0b2',
        'version': (2, 4, 0, 'beta', 2),
        'urls': {
            'download':
            'https://github.com/metabrainz/picard/releases/tag/release-2.4.0b2',
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
