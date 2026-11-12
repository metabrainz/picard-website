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
# FILESERVER_URL is read from the site config (like tools/verify_downloads.py); use
# --fileserver-url to override without a config.
#
# Usage:
#   uv run python -m tools.release_helper 3.0.1
#   uv run python -m tools.release_helper 3.0.0rc4 --channel beta
#   uv run python -m tools.release_helper 3.0.1 --repo metabrainz/picard
#   uv run python -m tools.release_helper 3.0.1 --links-only   # sizes only, no hashes
#   uv run python -m tools.release_helper 3.0.1 --download     # hash GitHub binaries
#                                                          # (pre-mirror)
#   uv run python -m tools.release_helper 3.0.5 --write        # update default_config.py
#   uv run python -m tools.release_helper 3.0.5 --write --changelog-url \
#       https://blog.metabrainz.org/2026/11/12/picard-3-0-5-released/

import argparse
import datetime
import difflib
import hashlib
import json
import os
import re
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
# Entries are in the order they appear in default_config.py.
# Each entry: hash_field -> (size_field, asset_filename_template)
FIELD_TO_ASSET = {
    'win_hash': ('win_size', 'picard-setup-{tag}.exe'),
    'win_portable_hash': ('win_portable_size', 'MusicBrainz-Picard-{tag}.exe'),
    'mac_x86_64_hash': ('mac_x86_64_size', 'MusicBrainz-Picard-{tag}-macOS-13.0-x86_64.dmg'),
    'mac_arm64_hash': ('mac_arm64_size', 'MusicBrainz-Picard-{tag}-macOS-13.0-arm64.dmg'),
    'mac_hash': ('mac_size', 'MusicBrainz-Picard-{tag}-macOS-10.14.dmg'),
    'mac_10_12_hash': ('mac_10_12_size', 'MusicBrainz-Picard-{tag}-macOS-10.12.dmg'),
    'source_tar_hash': ('source_tar_size', 'picard-{tag}.tar.gz'),
    'source_zip_hash': ('source_zip_size', 'picard-{tag}.zip'),
}

# Legacy macOS fields: omitted from the block when the release has no such asset.
OPTIONAL_FIELDS = {'mac_size', 'mac_hash', 'mac_10_12_size', 'mac_10_12_hash'}

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG_PATH = os.path.join(REPO_ROOT, 'website', 'default_config.py')
DEFAULT_DOWNLOAD_URL = 'https://picard.musicbrainz.org/'
USER_AGENT = 'picard-website release-helper'
CHUNK = 1 << 16
PRE_RELEASE_TYPES = {'a': 'alpha', 'alpha': 'alpha', 'b': 'beta', 'beta': 'beta', 'rc': 'rc'}


def urlopen(url, timeout=30, headers=None):
    """Open url with our User-Agent. Errors propagate to the caller."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, **(headers or {})})
    return urllib.request.urlopen(req, timeout=timeout)


def reason(e):
    return getattr(e, 'reason', e)


def fetch_release(repo, tag):
    """Return the parsed GitHub release JSON for a tag.

    Tries the tag as given and with the 'release-' prefix the repo uses.
    """
    candidates = [tag] if tag.startswith('release-') else [tag, f'release-{tag}']

    last_error = None
    for candidate in candidates:
        url = f"https://api.github.com/repos/{repo}/releases/tags/{candidate}"
        try:
            with urlopen(url, headers={'Accept': 'application/vnd.github+json'}) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code} for {url}"
            if e.code != 404:
                raise SystemExit(f"GitHub API error: {last_error}") from e
        except (urllib.error.URLError, TimeoutError) as e:
            raise SystemExit(f"Could not reach GitHub API: {reason(e)}") from e

    raise SystemExit(f"Release not found. Tried: {', '.join(candidates)} ({last_error})")


def fetch_md5_sidecar(fileserver_url, filename):
    """Fetch '<fileserver>/<filename>.md5' and return the hex MD5, or None.

    The sidecar is in md5sum format: '<hexdigest> *<filename>' (or two spaces).
    Returns None if the sidecar is missing (e.g. not mirrored yet).
    """
    url = f"{fileserver_url.rstrip('/')}/{filename}.md5"
    try:
        with urlopen(url) as resp:
            text = resp.read().decode('utf-8', 'replace').strip()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise SystemExit(f"Failed to fetch {url}: HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise SystemExit(f"Failed to fetch {url}: {reason(e)}") from e

    # First whitespace-separated token is the digest.
    token = text.split()[0] if text else ''
    if not re.fullmatch(r'[0-9a-fA-F]{32}', token):
        raise SystemExit(f"Unexpected .md5 content at {url}: {text!r}")
    return token.lower()


def download_md5(url):
    """Download url fully and return its hex MD5 (fallback path)."""
    md5 = hashlib.md5()
    try:
        with urlopen(url, timeout=300) as resp:
            while chunk := resp.read(CHUNK):
                md5.update(chunk)
    except (urllib.error.URLError, TimeoutError) as e:
        raise SystemExit(f"Failed to download {url}: {reason(e)}") from e
    return md5.hexdigest()


def format_size_mib(byte_size):
    """Return the rounded-MiB string used in default_config.py.

    Sizes are whole MiB (e.g. '62', '11'). The field is advisory and
    display-only, so a +/-1 MiB difference from a value someone typed by hand
    is harmless (tools/verify_downloads.py allows 1 MiB slack).
    """
    return str(round(byte_size / (1024 * 1024)))


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
        from flask import Flask
    except ImportError as e:
        raise SystemExit(
            "Could not import Flask to read FILESERVER_URL. Run via "
            "'uv run python -m tools.release_helper ...' or pass --fileserver-url."
        ) from e

    website_folder = os.path.dirname(DEFAULT_CONFIG_PATH)
    cfg = Flask(__name__).config
    cfg.from_pyfile(DEFAULT_CONFIG_PATH)
    cfg.from_pyfile(os.path.join(website_folder, 'config.py'), silent=True)
    try:
        return cfg['FILESERVER_URL']
    except KeyError as e:
        raise SystemExit("FILESERVER_URL not found in config; pass --fileserver-url.") from e


def parse_version_tuple(tag):
    """Convert a tag like '3.0.5', '3.0.0rc4' or '2.9.0a1' to the PEP-440 style
    tuple used in default_config.py: (major, minor, micro, type, dev).

    Final releases use ('final', 0). Raises SystemExit if the tag is unparsable.
    """
    m = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:(a|alpha|b|beta|rc)(\d+))?', tag)
    if not m:
        raise SystemExit(f"Cannot derive a version tuple from tag {tag!r}.")
    major, minor, micro, pre, num = m.groups()
    kind, dev = (PRE_RELEASE_TYPES[pre], int(num)) if pre else ('final', 0)
    return (int(major), int(minor), int(micro), kind, dev)


def predict_blog_url(version, date):
    """Predict the MetaBrainz blog post URL for a release.

    Known patterns (slugs use dashes instead of dots; pre-releases drop
    trailing zero components, so 3.0.0 becomes "3"):
      final: .../2026/11/01/picard-3-0-4-released/
      rc:    .../2026/09/22/picard-3-release-candidate-4/
      beta:  .../2026/07/16/picard-3-beta-7-released/
    The post is normally published the same day as the release.
    Returns None for release types with no known pattern (e.g. alpha).
    """
    *parts, kind, num = version
    if kind != 'final':
        while len(parts) > 1 and parts[-1] == 0:
            parts.pop()
    ver = '-'.join(map(str, parts))
    slug = {
        'final': f"{ver}-released",
        'rc': f"{ver}-release-candidate-{num}",
        'beta': f"{ver}-beta-{num}-released",
    }.get(kind)
    if slug is None:
        return None
    return f"https://blog.metabrainz.org/{date:%Y/%m/%d}/picard-{slug}/"


def build_block(channel, tag, version, download_url, changelog_url, results):
    """Return the channel block as a list of lines (4-space indented, as in
    default_config.py)."""
    lines = [
        f"    '{channel}': {{",
        f"        'tag': '{tag}',",
        f"        'version': {version!r},",
        "        'urls': {",
        f"            'download': '{download_url}',",
        f"            'changelog': '{changelog_url}',",
        "        },",
    ]
    for hash_field, (size_field, _template) in FIELD_TO_ASSET.items():
        for field in (size_field, hash_field):
            value = results.get(field, '')
            if value or field not in OPTIONAL_FIELDS:
                lines.append(f"        '{field}': '{value}',")
    lines.append("    },")
    return lines


def channel_block_pattern(channel):
    """Regex matching a whole top-level channel block of PICARD_VERSIONS."""
    return re.compile(
        rf"^    '{re.escape(channel)}': \{{\n.*?^    \}},\n", re.MULTILINE | re.DOTALL
    )


def replace_channel_block(text, channel, block_lines):
    """Return config text with the PICARD_VERSIONS channel block replaced.

    Raises SystemExit if the channel block cannot be found exactly once.
    """
    pattern = channel_block_pattern(channel)
    count = len(pattern.findall(text))
    if count != 1:
        raise SystemExit(
            f"Expected exactly one '{channel}' block in PICARD_VERSIONS, found {count}."
        )
    return pattern.sub(lambda _m: "\n".join(block_lines) + "\n", text, count=1)


def existing_download_url(text, channel):
    """Return the current 'download' URL of a channel, or None."""
    m = channel_block_pattern(channel).search(text)
    url = m and re.search(r"'download': '([^']*)'", m.group(0))
    return url.group(1) if url else None


def collect_results(args, tag, assets_by_name, fileserver_url):
    """Return ({field: value}, [missing asset names]) for all known assets."""
    results = {}
    missing = []
    for hash_field, (size_field, template) in FIELD_TO_ASSET.items():
        asset_name = template.format(tag=tag)
        asset = assets_by_name.get(asset_name)
        results[hash_field] = results[size_field] = ''
        if asset is None:
            # Not every build type exists for every release; leave blank.
            missing.append(asset_name)
            continue

        # Size always comes from the GitHub API (no download needed).
        results[size_field] = size = format_size_mib(asset.get('size', 0))

        if args.links_only:
            print(f"  size   {asset_name}: {size} MiB (hash skipped)", file=sys.stderr)
            continue

        if args.download:
            print(f"  hashing {asset_name} (downloading) ...", file=sys.stderr)
            md5_hex = download_md5(asset['browser_download_url'])
        else:
            md5_hex = fetch_md5_sidecar(fileserver_url, asset_name)
            if md5_hex is None:
                print(f"  MISS   {asset_name}.md5 not on fileserver "
                      f"(mirror the release first, or use --download)", file=sys.stderr)
                continue

        results[hash_field] = md5_hex
        print(f"  md5    {asset_name}: {md5_hex} ({size} MiB)", file=sys.stderr)
    return results, missing


def choose_changelog_url(args, tag, version):
    if args.changelog_url:
        return args.changelog_url
    url = predict_blog_url(version, args.release_date or datetime.date.today())
    if url is None:
        return f"https://picard.musicbrainz.org/changelog/#release-{tag}"
    print(f"# note: changelog URL is predicted ({url}); verify it once the blog "
          "post is published, or pass --changelog-url / --release-date.", file=sys.stderr)
    return url


def write_config(path, channel, config_text, block):
    """Replace the channel block in the config file and print a diff."""
    new_text = replace_channel_block(config_text, channel, block)
    name = os.path.basename(path)
    print("\n".join(difflib.unified_diff(
        config_text.splitlines(), new_text.splitlines(), f'a/{name}', f'b/{name}', lineterm='',
    )))
    if new_text == config_text:
        print(f"\n{path}: no changes.", file=sys.stderr)
        return
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print(f"\nUpdated '{channel}' in {path}", file=sys.stderr)


def parse_args():
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
    parser.add_argument(
        '--write', action='store_true',
        help="Update the channel block in website/default_config.py in place "
             "(a diff is printed). Without it, the block is only printed.",
    )
    parser.add_argument(
        '--config-path', default=DEFAULT_CONFIG_PATH,
        help="Config file to edit with --write (default: website/default_config.py).",
    )
    parser.add_argument(
        '--changelog-url', default=None,
        help="Changelog URL for the block. Default: the predicted blog post URL "
             "(see --release-date), else "
             "https://picard.musicbrainz.org/changelog/#release-<tag>.",
    )
    parser.add_argument(
        '--release-date', default=None, type=datetime.date.fromisoformat,
        metavar='YYYY-MM-DD',
        help="Date used in the predicted blog URL (default: today).",
    )
    parser.add_argument(
        '--download-url', default=None,
        help="Download URL for the block (default: keep the channel's current "
             f"value when using --write, else {DEFAULT_DOWNLOAD_URL}).",
    )
    args = parser.parse_args()
    if args.links_only and args.download:
        parser.error("--links-only and --download are mutually exclusive")
    return args


def main():
    args = parse_args()

    tag = args.tag.removeprefix('release-')
    version = parse_version_tuple(tag)
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

    results, missing = collect_results(args, tag, assets_by_name, fileserver_url)
    changelog_url = choose_changelog_url(args, tag, version)

    config_text = None
    if args.write:
        with open(args.config_path, encoding='utf-8') as f:
            config_text = f.read()
    download_url = (
        args.download_url
        or (existing_download_url(config_text, args.channel) if config_text else None)
        or DEFAULT_DOWNLOAD_URL
    )

    block = build_block(args.channel, tag, version, download_url, changelog_url, results)

    if args.write:
        write_config(args.config_path, args.channel, config_text, block)
        # Warn only for assets that exist but got no hash (legacy/absent ones are expected).
        unhashed = [h for h, (s, _t) in FIELD_TO_ASSET.items() if results[s] and not results[h]]
        if unhashed and not args.links_only:
            print(f"# warning: blank hashes written for: {', '.join(unhashed)}", file=sys.stderr)
    else:
        print()
        print("\n".join(block))

    if missing:
        print(f"\n# note: no asset for these templates (left blank): {', '.join(missing)}",
              file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
