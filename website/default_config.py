# This configuration is for production / docker
# You need to copy config.py.example to config.py and edit the file to your own needs
# to override these values.

# Default cache timeout - used when no specific timeout is specified
DEFAULT_CACHE_TIMEOUT = 5 * 60

PLUGINS_BUILD_DIR = "/code/plugins"
PLUGINS_REFRESH_INTERVAL_SECONDS = 12 * 60 * 60
PLUGINS_CACHE_TIMEOUT = 0  # never expire, handled by plugin refresh scheduler
# Flask automatically orders them in ascending order while
# retrieveing them. Since it is a string comparison, v10 appears before
# v2. So be careful with the ordering.
PLUGIN_VERSIONS = {
    'v1': {
        'title': '1.0',
        'response': 'The endpoints currently available for this api version are /api/v1/plugins and /api/v1/download',
    },
    'v2': {
        'title': '2.0',
        'response': 'The endpoints currently available for this api version'
        ' are /api/v2/plugins, /api/v2/download and /api/v2/releases',
    },
    'v3': {
        'title': '3.0',
        'response': 'The endpoints currently available for this api version are /api/v3/registry/plugins.toml',
    },
}

# Download URL for v3 registry file
PLUGINS_V3_REGISTRY_URL = (
    "https://raw.githubusercontent.com/metabrainz/picard-plugins-registry/refs/heads/main/plugins.toml"
)

# v3 plugins registry cache timeout
PLUGINS_V3_REGISTRY_CACHE_TIMEOUT = 4 * 60 * 60

# v3 plugins registry request timeout
PLUGINS_V3_REGISTRY_REQUEST_TIMEOUT = 5

# PICARD_VERSIONS dictionary valid keys are: 'stable', 'beta' and 'dev'.
# The 'version' tuple comprises int_major, int_minor, int_micro, str_type and int_development as defined in PEP-440.
# The Picard developers have standardized on using only 'dev' or 'final' as the str_type segment of the version tuple.
PICARD_VERSIONS = {
    'stable': {
        'tag': '2.13.3',
        'version': (2, 13, 3, 'final', 0),
        'urls': {
            'download': 'https://picard.musicbrainz.org/',
            'changelog': 'https://blog.metabrainz.org/2025/02/17/picard-2-13-3-released/',
        },
        'win_size': '31',
        'win_hash': 'e17573c3e77e629e86e86c710d7137f4',
        'win_portable_size': '45',
        'win_portable_hash': '58b1b690745e6aa910d147f4c19c336b',
        'mac_10_12_size': '39',
        'mac_10_12_hash': 'e0053010cd726e36e10d89699965e635',
        'mac_size': '39',
        'mac_hash': '0284d3a85c2975206f1258ed670c3fc5',
        'source_tar_size': '5.9',
        'source_tar_hash': '525d42abf04513ca264c6db23cecdc95',
        'source_zip_size': '6.4',
        'source_zip_hash': '8361d595a1f23f58e4f6e788f4d25198',
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
        },
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
# Scheduler API is restricted to localhost only (see scheduler.py)
# Safe to enable for local debugging and monitoring
SCHEDULER_API_ENABLED = True
