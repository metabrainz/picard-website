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
        'tag': '2.9.2',
        'version': (2, 9, 2, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://blog.metabrainz.org/2023/09/12/picard-2-9-2-released/',
        },
        'win_size': '31',
        'win_hash': 'ad34d72d1913867320434020a30651b9',
        'win_portable_size': '45',
        'win_portable_hash': '20152f2df15a63bf38b17cce049ea752',
        'mac_10_12_size': '35',
        'mac_10_12_hash': 'df17d806d336a6b805972339fc1c2b8e',
        'mac_size': '38',
        'mac_hash': '649ac25bc6727774c2e01380b1d4f773',
        'source_tar_size': '5.3',
        'source_tar_hash': '740b9a021dcc711e81c0f2d01a8df974',
        'source_zip_size': '5.8',
        'source_zip_hash': 'b7d74ff819cf342aa4063a5387c07f6a',
    },
    'beta': {
        'tag': '2.10.0rc1',
        'version': (2, 10, 0, 'rc', 1),
        'urls': {
            'download': 'https://picard.musicbrainz.org/downloads/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.10.0rc1',
        },
        'win_size': '31',
        'win_hash': '61d9dbb8213be5dc12205a358830fe11',
        'win_portable_size': '45',
        'win_portable_hash': '333cf465003ece1480b8f50e3cd0e2e7',
        'mac_10_12_size': '35',
        'mac_10_12_hash': '6db6f9c406be1740e46a18ab4c72fac3',
        'mac_size': '38',
        'mac_hash': '7c4d7c98cfdb87a155aaf19efb1c4b14',
        'source_tar_size': '5.6',
        'source_tar_hash': 'dac609b76aef7ec8800d5439950ea3f2',
        'source_zip_size': '6.1',
        'source_zip_hash': '8f8ab2287d2140f5c9826a24e4db78b6',
    },
    'dev': {
        'tag': '2.9.0a1',
        'version': (2, 9, 0, 'alpha', 1),
        'urls': {
            'download': 'https://blog.metabrainz.org/2023/01/03/picard-2-9-alpha-1-available-for-testing/',
        }
    },
}

DOCS_BASE_URL = "https://picard-docs.musicbrainz.org"
CHANGELOG_URL = "https://raw.githubusercontent.com/musicbrainz/picard/master/NEWS.md"
CHANGELOG_CACHE_TIMEOUT = 5 * 60

SUPPORTED_LANGUAGES = [
    'en',
    'de',
    'fr',
    'it',
]

SERVER_HOSTNAME = "127.0.0.1"
SERVER_PORT = 6060
SCHEDULER_API_ENABLED = True
