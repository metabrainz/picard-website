from collections import OrderedDict
import json

from flask import (
    Blueprint,
    current_app,
    render_template,
)
from flask_babel import get_locale

from website.plugin3_registry import load_plugin_list
from website.plugin_utils import plugins_json_file


plugins_bp = Blueprint('plugins', __name__)


@plugins_bp.get('/')
def show_plugins():
    all_plugins = OrderedDict()
    versions = current_app.config['PLUGIN_VERSIONS']
    for version, build_version in sorted([(key, versions[key]['title']) for key in versions]):
        if version in {'v1', 'v2'}:
            ordered_plugins = _load_v1_v2_plugins(build_version)
        elif version == 'v3':
            ordered_plugins = _load_v3_plugins()
        else:
            ordered_plugins = None

        if ordered_plugins is None:
            return render_template('errors/503.html'), 503
        if ordered_plugins:
            all_plugins[version[1:]] = ordered_plugins
    return render_template('plugins.html', all_plugins=all_plugins)


def _load_v1_v2_plugins(build_version):
    """Returns OrderedDict of plugins, or None if data not generated."""
    build_json_file = plugins_json_file(current_app, build_version)
    try:
        with open(build_json_file, encoding='utf-8') as fp:
            plugins = json.loads(fp.read())['plugins']
    except FileNotFoundError:
        current_app.logger.warning("Plugin data not found: %s. Run plugins-generate.py to generate it.", build_json_file)
        return None
    ordered_plugins = OrderedDict()
    for key in sorted(plugins, key=lambda k: plugins[k]['name'].lower()):
        ordered_plugins[key] = plugins[key]
    return ordered_plugins


def _localized(i18n, default, lang):
    """Pick the translation for lang (falling back to the base language code,
    then to the provided English default). An empty translation is treated as
    missing so it falls back to the default rather than rendering blank."""
    if not i18n or not lang:
        return default
    if i18n.get(lang):
        return i18n[lang]
    # Fall back from a territory variant (e.g. 'de_AT') to the language ('de').
    base = lang.replace('-', '_').split('_')[0]
    if i18n.get(base):
        return i18n[base]
    return default


def _load_v3_plugins() -> OrderedDict:
    """Load v3 plugins, resolving localized name/description for the active
    UI locale. The cached registry data is locale-neutral; translations are
    applied here per request."""
    plugins = load_plugin_list(current_app)
    if not plugins:
        return plugins

    locale = get_locale()
    lang = str(locale) if locale else None

    localized = OrderedDict()
    for id, plugin in plugins.items():
        entry = dict(plugin)
        entry['name'] = _localized(plugin.get('name_i18n'), plugin.get('name', ''), lang)
        entry['description'] = _localized(
            plugin.get('description_i18n'), plugin.get('description', ''), lang
        )
        localized[id] = entry
    return localized
