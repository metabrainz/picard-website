# This configuration is for production / docker
# You need to copy config.py.example to config.py and edit the file to your own needs
# to override these values.
PLUGINS_BUILD_DIR = "/code/plugins"
PLUGINS_REFRESH_INTERVAL_SECONDS = 12 * 60 * 60
PLUGINS_CACHE_TIMEOUT = 0  # never expire, handled by plugin refresh
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
        'tag': '2.8.2',
        'version': (2, 8, 2, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://blog.metabrainz.org/2022/07/07/picard-2-8-2-released/',
        },
        'win_size': '31',
        'win_hash': 'c4076c2bf9087a28a3ae2ba6a29c48e3',
        'win_portable_size': '44',
        'win_portable_hash': 'bfecc469ffc40c11a2d49dae3127d921',
        'mac_10_12_size': '32',
        'mac_10_12_hash': '199d4d1aed76fac692dc5d60364f7bd7',
        'mac_size': '35',
        'mac_hash': '0a1e7797484bef4d635caaffd9de7513',
        'linux_size': '5',
        'linux_hash': 'f3ffe5ca7e23ca3a6caaa27c9d79246d',
    },
    'beta': {
        'tag': '2.8.0rc2',
        'version': (2, 8, 0, 'rc', 2),
        'urls': {
            'download': 'https://picard.musicbrainz.org/downloads/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.8.0rc2',
        },
        'win_size': '31',
        'win_hash': '7d310f11d65477e9767e83a4c58ba8c1',
        'win_portable_size': '44',
        'win_portable_hash': '5da0c3092b0ac3d4df3541b8e6897852',
        'mac_10_12_size': '33',
        'mac_10_12_hash': '0d7dc7775ef10573b142fa01fe4e262f',
        'mac_size': '34',
        'mac_hash': 'de16c0c0159c201220c228a391120529',
        'linux_size': '5',
        'linux_hash': 'af31235bcfde46c02a8c4733765df518',
    },
    'dev': {
        'tag': '2.8.0rc2',
        'version': (2, 8, 0, 'rc', 2),
        'urls': {
            'download':
            'https://github.com/metabrainz/picard/releases/tag/release-2.8.0rc2',
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
SCHEDULER_API_ENABLED = True
