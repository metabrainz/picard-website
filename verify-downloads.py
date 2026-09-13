#!/usr/bin/env python

# Verify the Picard download links and MD5 hashes declared in the site config.
#
# It reads PICARD_VERSIONS and FILESERVER_URL exactly as the running site does
# (via create_app().config), reconstructs every download URL the downloads page
# renders, then for each file:
#   - checks the URL is reachable,
#   - downloads it and compares the MD5 against the configured *_hash,
#   - warns if the on-disk size (MB, rounded) disagrees with the configured
#     *_size.
# It also checks the per-channel 'urls' links (download / changelog) respond OK.
#
# Exit status is non-zero if any check fails, so this is CI-friendly.
#
# Usage:
#   uv run python verify-downloads.py                # verify all channels
#   uv run python verify-downloads.py beta           # only the 'beta' channel
#   uv run python verify-downloads.py --links-only   # skip hash downloads
#   uv run python verify-downloads.py --channel beta --channel stable

import argparse
import hashlib
import sys
import urllib.request
import urllib.error

from website.frontend import create_app


# Maps a "<name>_hash" config field to the download filename template and,
# where relevant, the matching "<name>_size" field. The {tag} placeholder is
# filled from the channel's 'tag'. The macOS arm64/x86_64 filenames differ
# between the stable and beta channels (see downloads.html), so a channel may
# override the template.
#
# Each entry: hash_field -> (default_filename_template, size_field)
FILE_FIELDS = {
    'win_hash': ('picard-setup-{tag}.exe', 'win_size'),
    'win_portable_hash': ('MusicBrainz-Picard-{tag}.exe', 'win_portable_size'),
    'mac_arm64_hash': ('MusicBrainz-Picard-{tag}-macOS-11.0-arm64.dmg', 'mac_arm64_size'),
    'mac_x86_64_hash': ('MusicBrainz-Picard-{tag}-macOS-11.0-x86_64.dmg', 'mac_x86_64_size'),
    'mac_hash': ('MusicBrainz-Picard-{tag}-macOS-10.14.dmg', 'mac_size'),
    'mac_10_12_hash': ('MusicBrainz-Picard-{tag}-macOS-10.12.dmg', 'mac_10_12_size'),
    'source_tar_hash': ('picard-{tag}.tar.gz', 'source_tar_size'),
    'source_zip_hash': ('picard-{tag}.zip', 'source_zip_size'),
}

# Channel-specific filename overrides. The beta channel publishes the macOS
# builds under the macOS-13.0 naming (see downloads.html).
CHANNEL_FILENAME_OVERRIDES = {
    'beta': {
        'mac_arm64_hash': 'MusicBrainz-Picard-{tag}-macOS-13.0-arm64.dmg',
        'mac_x86_64_hash': 'MusicBrainz-Picard-{tag}-macOS-13.0-x86_64.dmg',
    },
}

USER_AGENT = 'picard-website verify-downloads'
CHUNK = 1 << 16


class Reporter:
    def __init__(self):
        self.failures = []
        self.warnings = []

    def ok(self, msg):
        print(f"  OK    {msg}")

    def warn(self, msg):
        self.warnings.append(msg)
        print(f"  WARN  {msg}")

    def fail(self, msg):
        self.failures.append(msg)
        print(f"  FAIL  {msg}")


def head_or_get_ok(url):
    """Return (ok, detail). Try HEAD, fall back to a ranged GET if HEAD is
    not allowed by the server."""
    for method in ('HEAD', 'GET'):
        req = urllib.request.Request(url, method=method, headers={'User-Agent': USER_AGENT})
        if method == 'GET':
            req.add_header('Range', 'bytes=0-0')
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return True, resp.status
        except urllib.error.HTTPError as e:
            # 405/501 => method not supported, try the next method.
            if method == 'HEAD' and e.code in (405, 501):
                continue
            return False, f"HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError) as e:
            return False, str(getattr(e, 'reason', e))
    return False, "unreachable"


def download_md5_and_size(url):
    """Download url fully, returning (md5_hex, byte_size). Raises on error."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    md5 = hashlib.md5()
    size = 0
    with urllib.request.urlopen(req, timeout=120) as resp:
        while True:
            chunk = resp.read(CHUNK)
            if not chunk:
                break
            md5.update(chunk)
            size += len(chunk)
    return md5.hexdigest(), size


def filename_for(channel, field):
    override = CHANNEL_FILENAME_OVERRIDES.get(channel, {})
    if field in override:
        return override[field]
    return FILE_FIELDS[field][0]


def verify_channel(name, data, fileserver_url, reporter, links_only):
    print(f"\n=== channel: {name} (tag {data.get('tag', '?')}) ===")
    tag = data.get('tag')
    if not tag:
        reporter.fail(f"[{name}] no 'tag' in config")
        return

    # 1) Check the per-channel URLs (download / changelog).
    for key, url in (data.get('urls') or {}).items():
        ok, detail = head_or_get_ok(url)
        label = f"[{name}] urls.{key} -> {url}"
        if ok:
            reporter.ok(f"{label} ({detail})")
        else:
            reporter.fail(f"{label} ({detail})")

    # 2) Check each declared download file (URL + optionally hash/size).
    for field, (_default_tmpl, size_field) in FILE_FIELDS.items():
        configured_hash = (data.get(field) or '').strip()
        if not configured_hash:
            continue  # field not published for this channel

        filename = filename_for(name, field).format(tag=tag)
        url = f"{fileserver_url.rstrip('/')}/{filename}"

        if links_only:
            ok, detail = head_or_get_ok(url)
            if ok:
                reporter.ok(f"[{name}] {filename} reachable ({detail})")
            else:
                reporter.fail(f"[{name}] {filename} NOT reachable ({detail})")
            continue

        try:
            actual_hash, actual_bytes = download_md5_and_size(url)
        except urllib.error.HTTPError as e:
            reporter.fail(f"[{name}] {filename} download failed (HTTP {e.code})")
            continue
        except (urllib.error.URLError, TimeoutError) as e:
            reporter.fail(f"[{name}] {filename} download failed ({getattr(e, 'reason', e)})")
            continue

        if actual_hash.lower() == configured_hash.lower():
            reporter.ok(f"[{name}] {filename} md5 matches ({configured_hash})")
        else:
            reporter.fail(
                f"[{name}] {filename} md5 MISMATCH: "
                f"config={configured_hash} actual={actual_hash}"
            )

        # Size is advisory: the config stores rounded MiB (as shown by ls/du)
        # as a string.
        configured_size = (data.get(size_field) or '').strip()
        if configured_size:
            actual_mib = actual_bytes / (1024 * 1024)
            try:
                want = float(configured_size)
            except ValueError:
                reporter.warn(f"[{name}] {size_field}={configured_size!r} not numeric")
            else:
                # Allow ~1 MiB rounding slack.
                if abs(actual_mib - want) > 1.0:
                    reporter.warn(
                        f"[{name}] {filename} size ~{actual_mib:.1f} MiB "
                        f"differs from config {want} MiB"
                    )


def main():
    parser = argparse.ArgumentParser(description="Verify Picard download links and MD5 hashes.")
    parser.add_argument(
        'channels', nargs='*',
        help="Channels to verify (e.g. stable beta). Default: all configured.",
    )
    parser.add_argument(
        '--channel', action='append', default=[], dest='channel_opt',
        help="Alternative way to specify a channel; may be repeated.",
    )
    parser.add_argument(
        '--links-only', action='store_true',
        help="Only check that URLs are reachable; skip downloading and hashing.",
    )
    args = parser.parse_args()

    config = create_app().config
    versions = config['PICARD_VERSIONS']
    fileserver_url = config['FILESERVER_URL']

    selected = args.channels + args.channel_opt
    if selected:
        unknown = [c for c in selected if c not in versions]
        if unknown:
            print(f"Unknown channel(s): {', '.join(unknown)}", file=sys.stderr)
            print(f"Available: {', '.join(versions)}", file=sys.stderr)
            return 2
        channels = selected
    else:
        channels = list(versions)

    print(f"FILESERVER_URL = {fileserver_url}")
    print(f"Channels: {', '.join(channels)}")
    if args.links_only:
        print("Mode: links-only (no hashing)")

    reporter = Reporter()
    for name in channels:
        verify_channel(name, versions[name], fileserver_url, reporter, args.links_only)

    print("\n=== summary ===")
    print(f"failures: {len(reporter.failures)}  warnings: {len(reporter.warnings)}")
    for f in reporter.failures:
        print(f"  FAIL  {f}")
    for w in reporter.warnings:
        print(f"  WARN  {w}")

    return 1 if reporter.failures else 0


if __name__ == '__main__':
    sys.exit(main())
