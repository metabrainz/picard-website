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
        'tag': '2.6.4',
        'version': (2, 6, 4, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://picard.musicbrainz.org/changelog/',
        },
        'win_size': '30',
        'win_hash': '3f6a39879d371acf9e508e2631cc475c',
        'win_portable_size': '43',
        'win_portable_hash': 'cb1db87654ddca8b55f434fe76ef719f',
        'mac_10_12_size': '32',
        'mac_10_12_hash': '6bde06deba2e9041fdf88cf388189355',
        'mac_size': '34',
        'mac_hash': '8a047c79aec18a3186d07fd2226e2ab3',
        'linux_size': '4.2',
        'linux_hash': '-',
    },
    'beta': {
        'tag': '2.7.0b2',
        'version': (2, 7, 0, 'beta', 2),
        'urls': {
            'download': 'https://picard.musicbrainz.org/downloads/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.7.0b2',
        },
        'win_size': '34',
        'win_hash': 'fd56b5f3e8a7f2ac49ff9ac6ee620124',
        'win_portable_size': '50',
        'win_portable_hash': '4c71b9b971052bf0523d4ad2eb24a56a',
        'mac_10_12_size': '38',
        'mac_10_12_hash': '8b7c5caa98a4fae32a9d1baab8c0ca25',
        'mac_size': '40',
        'mac_hash': 'a06545198d915618a09601e1139ece2d',
        'linux_size': '4.7',
        'linux_hash': '4ff94e12df7732a9d43c37f5073b56a4',
    },
    'dev': {
        'tag': '2.7.0b2',
        'version': (2, 7, 0, 'beta', 2),
        'urls': {
            'download':
            'https://github.com/metabrainz/picard/releases/tag/release-2.7.0b2',
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
