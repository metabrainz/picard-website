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
        'tag': '2.7.3',
        'version': (2, 7, 3, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.7.3',
        },
        'win_size': '34',
        'win_hash': 'f59984df37c61eb8b9d1abc6da57c6c6',
        'win_portable_size': '49',
        'win_portable_hash': 'd33f8bfe5d4717f28bdc066691f06ad9',
        'mac_10_12_size': '37',
        'mac_10_12_hash': 'b8131e50148cc0af80892ec1d8629304',
        'mac_size': '39',
        'mac_hash': '0bae025084e596d4597ed5a561336c19',
        'linux_size': '5',
        'linux_hash': 'e65938b0b938e5559420f0d6035524b8',
    },
    'beta': {
        'tag': '2.8.0rc1',
        'version': (2, 8, 0, 'rc', 1),
        'urls': {
            'download': 'https://picard.musicbrainz.org/downloads/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.8.0rc1',
        },
        'win_size': '31',
        'win_hash': 'e3d4b93eab31519cbcbb3116b96d0d6f',
        'win_portable_size': '44',
        'win_portable_hash': '586aa38d74f627bdde43586658f5fec2',
        'mac_10_12_size': '33',
        'mac_10_12_hash': '26555b1dad5f508b7cd05ed6e5e6bf5a',
        'mac_size': '34',
        'mac_hash': '1605f6421c8c2df7790626a36df91c2f',
        'linux_size': '5',
        'linux_hash': '9dfea9e1479720dd7cfa3b5ca52a59bf',
    },
    'dev': {
        'tag': '2.8.0rc1',
        'version': (2, 8, 0, 'rc', 1),
        'urls': {
            'download':
            'https://github.com/metabrainz/picard/releases/tag/release-2.8.0rc1',
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
