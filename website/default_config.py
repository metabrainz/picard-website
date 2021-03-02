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
        'tag': '2.5.6',
        'version': (2, 5, 6, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://picard.musicbrainz.org/changelog/',
        },
        'win_size': '30',
        'win_hash': 'c1f1ab6e4f4f0acc4c2f26c4c6270a99',
        'win_portable_size': '43',
        'win_portable_hash': 'eb6c66e6473a4fa33cff0288f1717d80',
        'mac_size': '31',
        'mac_hash': '42823e860d47a2bf67b7caff7f9851f4',
        'linux_size': '4.1',
        'linux_hash': '-',
    },
    'beta': {
        'tag': '2.6.0b1',
        'version': (2, 6, 0, 'beta', 1),
        'urls': {
            'download': 'https://picard.musicbrainz.org/downloads/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.6.0b1',
        },
        'win_size': '30',
        'win_hash': '099ce75e35a0d7d829a59c3410ecee70',
        'win_portable_size': '43',
        'win_portable_hash': 'fb0676df6ae6ee78f0233159ffa7fb16',
        'mac_10_12_size': '32',
        'mac_10_12_hash': 'c38e5b5be1b9d1618662f53ed2b4b667',
        'mac_size': '33',
        'mac_hash': '24a9e39f8856325162d6548b73ee96ad',
        'linux_size': '4.1',
        'linux_hash': '-',
    },
    'dev': {
        'tag': '2.6.0b1',
        'version': (2, 6, 0, 'beta', 1),
        'urls': {
            'download':
            'https://github.com/metabrainz/picard/releases/tag/release-2.6.0b1',
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
