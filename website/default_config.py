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
        'tag': '2.6.1',
        'version': (2, 6, 1, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://picard.musicbrainz.org/changelog/',
        },
        'win_size': '30',
        'win_hash': '5581d9888d8fab62a8f82a7e958c4bf3',
        'win_portable_size': '43',
        'win_portable_hash': 'f5053984c680fc0eeeeabb1d23f640bf',
        'mac_10_12_size': '33',
        'mac_10_12_hash': 'b4a206a951c3dfa677bdf14176921cdb',
        'mac_size': '34',
        'mac_hash': 'c6427ffe71abbdd06ff009c7b720beed',
        'linux_size': '4.2',
        'linux_hash': '-',
    },
    'beta': {
        'tag': '2.6.0b3',
        'version': (2, 6, 0, 'beta', 3),
        'urls': {
            'download': 'https://picard.musicbrainz.org/downloads/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.6.0b3',
        },
        'win_size': '30',
        'win_hash': 'a8df1176e1127dc159b5cf9d80840355',
        'win_portable_size': '43',
        'win_portable_hash': '6979dfbc286934d473d9f4a1f7f3a9f0',
        'mac_10_12_size': '33',
        'mac_10_12_hash': 'e16b38301e5569023724ca69c66cce2e',
        'mac_size': '34',
        'mac_hash': '3ce282a7dad8a6a19fec496bd2a67d28',
        'linux_size': '4.1',
        'linux_hash': '-',
    },
    'dev': {
        'tag': '2.6.0b3',
        'version': (2, 6, 0, 'beta', 3),
        'urls': {
            'download':
            'https://github.com/metabrainz/picard/releases/tag/release-2.6.0b3',
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
