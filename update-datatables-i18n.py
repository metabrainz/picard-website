#!/usr/bin/env python

# Update localization files for DataTables.

import locale
from pathlib import Path
import sys
import urllib.error
import urllib.request

from website.frontend import create_app


USER_AGENT = 'picard-website update-datatables-i18n'
DATATABLES_VERSION = "3.1.4"
LANG_MAPPING = {
    'zh_Hans': 'zh',
}
DATATABLES_LOCALE_FOLDER = Path(__file__).parent / "website" / "frontend" / "static" / "js"


def iter_locales(lang):
    yield lang
    if alt := LANG_MAPPING.get(lang, None):
        yield alt
    normalized = locale.normalize(lang).split('.')[0]
    if normalized != lang:
        yield normalized


def save_translation_file(lang, content):
    target_file = DATATABLES_LOCALE_FOLDER / f"dataTables.{lang}.json"
    with open(target_file, "wb+") as f:
        f.write(content)


def download_language_file(lang):
    for locale_code in iter_locales(lang):
        locale_code = locale_code.replace("_", "-")
        print(f"    trying {locale_code}")
        url = f"https://cdn.datatables.net/plug-ins/{DATATABLES_VERSION}/i18n/{locale_code}.json"
        req = urllib.request.Request(url, method="GET", headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = resp.read()
                if result:
                    save_translation_file(lang, result)
                    return True
        except urllib.error.HTTPError as e:
            if e.status == 404:
                continue
            raise e
    return False


def main():
    config = create_app().config
    versions = config['SUPPORTED_LANGUAGES']
    for lang in versions:
        if lang == 'en':
            continue  # skip English (default is always present)
        try:
            if download_language_file(lang):
                print(f"DataTables localization for {lang} updated.")
            else:
                print(f"DataTables localization for {lang} not found.")
        except Exception as e:
            print(f"Failed updating DataTables localization file for {lang}.\nError occurred: {e}")


if __name__ == '__main__':
    sys.exit(main())
