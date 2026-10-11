#!/usr/bin/env python

# Helper for updating PICARD_VERSIONS when a new Picard release is published.
#
# Given a release tag (e.g. 3.0.1) it builds a ready-to-paste channel block for
# website/default_config.py:
#   - sizes come from the GitHub release API (exact byte sizes, no download),
#   - MD5 hashes come from the small "<file>.md5" sidecars that the release
#     mirroring step uploads next to the binaries on FILESERVER_URL.
#
# This avoids downloading the (hundreds of MB of) binaries. The config stores
# MD5 while GitHub only publishes SHA256SUMS, so the MD5 sidecars on the
# fileserver are the cheap source of truth. Run this AFTER the release has been
# mirrored to the fileserver. If you need to run it before mirroring, use
# --download to fetch the GitHub assets and compute the MD5 locally.
#
# FILESERVER_URL is read from the site config (like verify-downloads.py); use
# --fileserver-url to override without a config.
#
# Usage:
#   uv run python release-helper.py 3.0.1
#   uv run python release-helper.py 3.0.0rc4 --channel beta
#   uv run python release-helper.py 3.0.1 --repo metabrainz/picard
#   uv run python release-helper.py 3.0.1 --links-only   # sizes only, no hashes
#   uv run python release-helper.py 3.0.1 --download     # hash GitHub binaries
#                                                          # (pre-mirror)

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request


# Maps a PICARD_VERSIONS "<name>_hash" field to the matching size field and the
# GitHub asset filename template. {tag} is filled from the release tag.
#
# These GitHub asset names are what the metabrainz/picard release workflow
# uploads; the fileserver mirrors them under the same names (the .md5 sidecar is
# "<name>.md5"). The one asset whose name is non-obvious is the Windows portable
# build, published as "MusicBrainz-Picard-{tag}.exe".
#
# Each entry: hash_field -> (size_field, asset_filename_template)
FIELD_TO_ASSET = {
    'win_hash': ('win_size', 'picard-setup-{tag}.exe'),
    'win_portable_hash': ('win_portable_size', 'MusicBrainz-Picard-{tag}.exe'),
    'mac_arm64_hash': ('mac_arm64_size', 'MusicBrainz-Picard-{tag}-macOS-13.0-arm64.dmg'),
    'mac_x86_64_hash': ('mac_x86_64_size', 'MusicBrainz-Picard-{tag}-macOS-13.0-x86_64.dmg'),
    'mac_hash': ('mac_size', 'MusicBrainz-Picard-{tag}-macOS-10.14.dmg'),
    'mac_10_12_hash': ('mac_10_12_size', 'MusicBrainz-Picard-{tag}-macOS-10.12.dmg'),
    'source_tar_hash': ('source_tar_size', 'picard-{tag}.tar.gz'),
    'source_zip_hash': ('source_zip_size', 'picard-{tag}.zip'),
}

# Order in which fields are emitted in the printed block (matches default_config.py).
FIELD_ORDER = [
    'win_size', 'win_hash',
    'win_portable_size', 'win_portable_hash',
    'mac_x86_64_size', 'mac_x86_64_hash',
    'mac_arm64_size', 'mac_arm64_hash',
    'mac_size', 'mac_hash',
    'mac_10_12_size', 'mac_10_12_hash',
    'source_tar_size', 'source_tar_hash',
    'source_zip_size', 'source_zip_hash',
]

USER_AGENT = 'picard-website release-helper'
CHUNK = 1 << 16


def fetch_release(repo, tag):
    """Return the parsed GitHub release JSON for a tag.

    Tries the tag as given and with the 'release-' prefix the repo uses.
    """
    candidates = [tag]
    if not tag.startswith('release-'):
        candidates.append(f'release-{tag}')

    last_error = None
    for candidate in candidates:
        url = f"https://api.github.com/repos/{repo}/releases/tags/{candidate}"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': USER_AGENT, 'Accept': 'application/vnd.github+json'},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code} for {url}"
            if e.code == 404:
                continue
            raise SystemExit(f"GitHub API error: {last_error}") from e
        except (urllib.error.URLError, TimeoutError) as e:
            raise SystemExit(f"Could not reach GitHub API: {getattr(e, 'reason', e)}") from e

    raise SystemExit(f"Release not found. Tried: {', '.join(candidates)} ({last_error})")


def fetch_md5_sidecar(fileserver_url, filename):
    """Fetch '<fileserver>/<filename>.md5' and return the hex MD5, or None.

    The sidecar is in md5sum format: '<hexdigest> *<filename>' (or two spaces).
    Returns None if the sidecar is missing (e.g. not mirrored yet).
    """
    url = f"{fileserver_url.rstrip('/')}/{filename}.md5"
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode('utf-8', 'replace').strip()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise SystemExit(f"Failed to fetch {url}: HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise SystemExit(f"Failed to fetch {url}: {getattr(e, 'reason', e)}") from e

    # First whitespace-separated token is the digest.
    token = text.split()[0] if text else ''
    if len(token) != 32 or not all(c in '0123456789abcdefABCDEF' for c in token):
        raise SystemExit(f"Unexpected .md5 content at {url}: {text!r}")
    return token.lower()


def download_md5(url):
    """Download url fully and return its hex MD5 (fallback path)."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    md5 = hashlib.md5()
    with urllib.request.urlopen(req, timeout=300) as resp:
        while True:
            chunk = resp.read(CHUNK)
            if not chunk:
                break
            md5.update(chunk)
    return md5.hexdigest()


def format_size_mib(byte_size):
    """Return the rounded-MiB string used in default_config.py.

    Sizes are whole MiB (e.g. '62', '11'), matching ls/du-style rounding. The
    field is advisory and display-only, so a +/-1 MiB difference from a value
    someone typed by hand is harmless (verify-downloads.py allows 1 MiB slack).
    """
    mib = byte_size / (1024 * 1024)
    return str(int(round(mib)))


def resolve_fileserver_url(explicit):
    """Return the FILESERVER_URL to use: the CLI value if given, else the one
    read from the site config files.

    Reads default_config.py (then config.py, if present) the same way
    create_app() does, but without building the full Flask app, so importing
    this does not spin up the plugin-build scheduler.
    """
    if explicit:
        return explicit
    try:
        import os

        from flask import Flask
    except ImportError as e:
        raise SystemExit(
            "Could not import Flask to read FILESERVER_URL. Run via "
            "'uv run python release-helper.py ...' or pass --fileserver-url."
        ) from e

    website_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'website')
    cfg = Flask(__name__).config
    cfg.from_pyfile(os.path.join(website_folder, 'default_config.py'))
    cfg.from_pyfile(os.path.join(website_folder, 'config.py'), silent=True)
    try:
        return cfg['FILESERVER_URL']
    except KeyError as e:
        raise SystemExit(
            "FILESERVER_URL not found in config; pass --fileserver-url."
        ) from e


def main():
    parser = argparse.ArgumentParser(
        description="Produce a PICARD_VERSIONS channel block from a GitHub release.",
    )
    parser.add_argument('tag', help="Release tag, e.g. 3.0.1 or release-3.0.1")
    parser.add_argument(
        '--repo', default='metabrainz/picard',
        help="GitHub repo (default: metabrainz/picard)",
    )
    parser.add_argument(
        '--channel', default='stable',
        help="Channel name to label the printed block (default: stable)",
    )
    parser.add_argument(
        '--fileserver-url', default=None,
        help="Override FILESERVER_URL (default: read from the site config).",
    )
    parser.add_argument(
        '--links-only', action='store_true',
        help="Emit sizes only (from the GitHub API); leave hashes blank.",
    )
    parser.add_argument(
        '--download', action='store_true',
        help="Compute MD5 by downloading the GitHub binaries instead of reading "
             "the fileserver .md5 sidecars. Use before the release is mirrored.",
    )
    args = parser.parse_args()

    if args.links_only and args.download:
        parser.error("--links-only and --download are mutually exclusive")

    tag = args.tag[len('release-'):] if args.tag.startswith('release-') else args.tag
    release = fetch_release(args.repo, args.tag)

    assets_by_name = {a['name']: a for a in release.get('assets', [])}
    if not assets_by_name:
        raise SystemExit(f"Release '{release.get('tag_name', tag)}' has no assets attached.")

    # Only resolve the fileserver when we actually need the .md5 sidecars.
    fileserver_url = None
    if not args.links_only and not args.download:
        fileserver_url = resolve_fileserver_url(args.fileserver_url)
        print(f"# fileserver: {fileserver_url}", file=sys.stderr)

    print(f"# release: {release.get('name') or release.get('tag_name')}")
    print(f"# tag_name: {release.get('tag_name')}")
    print(f"# assets found: {', '.join(sorted(assets_by_name))}\n")

    results = {}  # field -> value string
    missing = []
    for hash_field, (size_field, template) in FIELD_TO_ASSET.items():
        asset_name = template.format(tag=tag)
        asset = assets_by_name.get(asset_name)
        if asset is None:
            # Not every build type exists for every release; leave blank.
            results[hash_field] = ''
            results[size_field] = ''
            missing.append(asset_name)
            continue

        # Size always comes from the GitHub API (no download needed).
        results[size_field] = format_size_mib(asset.get('size', 0))

        if args.links_only:
            results[hash_field] = ''
            print(f"  size   {asset_name}: {results[size_field]} MiB (hash skipped)",
                  file=sys.stderr)
            continue

        if args.download:
            print(f"  hashing {asset_name} (downloading) ...", file=sys.stderr)
            try:
                md5_hex = download_md5(asset['browser_download_url'])
            except (urllib.error.URLError, TimeoutError) as e:
                raise SystemExit(
                    f"Failed to download {asset['browser_download_url']}: "
                    f"{getattr(e, 'reason', e)}"
                ) from e
        else:
            md5_hex = fetch_md5_sidecar(fileserver_url, asset_name)
            if md5_hex is None:
                results[hash_field] = ''
                print(f"  MISS   {asset_name}.md5 not on fileserver "
                      f"(mirror the release first, or use --download)",
                      file=sys.stderr)
                continue

        results[hash_field] = md5_hex
        print(f"  md5    {asset_name}: {md5_hex} ({results[size_field]} MiB)", file=sys.stderr)

    # Changelog URL hint (review before use; beta uses a different pattern).
    changelog_url = f"https://picard.musicbrainz.org/changelog/#release-{tag}"

    print(f"\n    '{args.channel}': {{")
    print(f"        'tag': '{tag}',")
    print(f"        'version': (...),  # TODO: set PEP-440 tuple for {tag}")
    print("        'urls': {")
    print("            'download': 'https://picard.musicbrainz.org/',")
    print(f"            'changelog': '{changelog_url}',  # TODO: confirm")
    print("        },")
    for field in FIELD_ORDER:
        value = results.get(field, '')
        print(f"        '{field}': '{value}',")
    print("    },")

    if missing:
        print(f"\n# note: no asset for these templates (left blank): {', '.join(missing)}",
              file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
