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
        'tag': '2.7',
        'version': (2, 7, 0, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://blog.metabrainz.org/2021/12/16/picard-2-7-released/',
        },
        'win_size': '34',
        'win_hash': '683c1b32352ad37faadaafb9cee3597d',
        'win_portable_size': '49',
        'win_portable_hash': '771382c503d9ca38514d54dbb13b8d7f',
        'mac_10_12_size': '37',
        'mac_10_12_hash': '4d538499a2e96b4607014ffbe83f9034',
        'mac_size': '39',
        'mac_hash': '9916a5f527df990fc9898594e3e9bb09',
        'linux_size': '5',
        'linux_hash': '0b447f3dc2ee9e76c7f42ea97fca3887',
    },
    'beta': {
        'tag': '2.7.0b3',
        'version': (2, 7, 0, 'beta', 3),
        'urls': {
            'download': 'https://picard.musicbrainz.org/downloads/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.7.0b3',
        },
        'win_size': '34',
        'win_hash': '145854a8ee22100ca331040a38474955',
        'win_portable_size': '49',
        'win_portable_hash': 'a92d3ebf153767b443292c687d27723f',
        'mac_10_12_size': '37',
        'mac_10_12_hash': 'f4e606f91a6afac7678ac5bc300002fc',
        'mac_size': '39',
        'mac_hash': '01af511c71da9021dac25cac93ae759f',
        'linux_size': '5',
        'linux_hash': 'a68696d709d880562396c357e0d9fed1',
    },
    'dev': {
        'tag': '2.7.0b3',
        'version': (2, 7, 0, 'beta', 3),
        'urls': {
            'download':
            'https://github.com/metabrainz/picard/releases/tag/release-2.7.0b3',
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
