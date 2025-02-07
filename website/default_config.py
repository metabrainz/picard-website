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
        'tag': '2.13.2',
        'version': (2, 13, 2, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://blog.metabrainz.org/2025/02/07/picard-2-13-2-released/',
        },
        'win_size': '32',
        'win_hash': 'dce80853bab1f53b0e117ed407a82f81',
        'win_portable_size': '45',
        'win_portable_hash': '9133be426744bb03d04fdd2ecc961d78',
        'mac_10_12_size': '39',
        'mac_10_12_hash': 'd7c8de40f22dbe053209cf46e0937f7c',
        'mac_size': '39',
        'mac_hash': '1a187966b4837ea94f00ccdaa4ff45ac',
        'source_tar_size': '5.9',
        'source_tar_hash': '85360fa8aa0bd301e4baa1e4146106db',
        'source_zip_size': '6.4',
        'source_zip_hash': '3de970979c4b0e0df882ce8a8866ff85',
    },
    'beta': {
        'tag': '2.11.0rc1',
        'version': (2, 11, 0, 'rc', 1),
        'urls': {
            'download': 'https://picard.musicbrainz.org/downloads/',
            'changelog': 'https://picard.musicbrainz.org/changelog/#release-2.11.0rc1',
        },
        'win_size': '31',
        'win_hash': 'ab994bbe9417de974478cd6bd9ed3379',
        'win_portable_size': '45',
        'win_portable_hash': '7122b62b14c5972d9d6315abd243aeff',
        'mac_10_12_size': '36',
        'mac_10_12_hash': '4b736d861530c0b924e7721e1ba3e117',
        'mac_size': '38',
        'mac_hash': '3a035a05a9cbe09a87e500eeca45543c',
        'source_tar_size': '5.6',
        'source_tar_hash': '57c2e0eabad4baf6678bace2f1dcf326',
        'source_zip_size': '6.2',
        'source_zip_hash': '109ab320729220f8368328b8d4ef4e82',
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
FILESERVER_URL = "https://data.musicbrainz.org/pub/musicbrainz/picard"
HELP_WITH_TRANSLATION_URL = "https://wiki.musicbrainz.org/MusicBrainz_Picard/Internationalization"
CHANGELOG_CACHE_TIMEOUT = 5 * 60

# An empty SUPPORTED_LANGUAGES list will select all available translations
SUPPORTED_LANGUAGES = [
    'en',
    'de',
    'es',
    'fr',
    'it',
    'lt',
    'nl',
    'pl',
    'ru',
    'sq',
    'tr',
    'uk',
]

SERVER_HOSTNAME = "127.0.0.1"
SERVER_PORT = 6060
SCHEDULER_API_ENABLED = True
