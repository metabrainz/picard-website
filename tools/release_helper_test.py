import ast
import datetime
import io
import urllib.error

import pytest

from tools import release_helper as rh


CONFIG = """\
PICARD_VERSIONS = {
    'stable': {
        'tag': '3.0.4',
        'version': (3, 0, 4, 'final', 0),
        'urls': {
            'download': 'https://example.org/dl/',
            'changelog': 'https://example.org/old',
        },
        'win_size': '62',
        'win_hash': 'aaaa',
    },
    'beta': {
        'tag': '3.0.0rc4',
        'urls': {
            'download': 'https://example.org/beta/',
        },
    },
}
OTHER = 1
"""


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("3.0.5", (3, 0, 5, 'final', 0)),
        ("3.0.0rc4", (3, 0, 0, 'rc', 4)),
        ("3.0.0b7", (3, 0, 0, 'beta', 7)),
        ("3.0.0beta7", (3, 0, 0, 'beta', 7)),
        ("2.9.0a1", (2, 9, 0, 'alpha', 1)),
    ],
)
def test_parse_version_tuple(tag, expected):
    assert rh.parse_version_tuple(tag) == expected


@pytest.mark.parametrize("tag", ["", "3.0", "v3.0.5", "3.0.5-rc1", "3.0.0c1"])
def test_parse_version_tuple_invalid(tag):
    with pytest.raises(SystemExit):
        rh.parse_version_tuple(tag)


@pytest.mark.parametrize(
    ("tag", "date", "expected"),
    [
        ("3.0.4", (2026, 11, 1), "https://blog.metabrainz.org/2026/11/01/picard-3-0-4-released/"),
        ("3.0.0", (2026, 1, 1), "https://blog.metabrainz.org/2026/01/01/picard-3-0-0-released/"),
        ("3.0.0rc4", (2026, 9, 22), "https://blog.metabrainz.org/2026/09/22/picard-3-release-candidate-4/"),
        ("3.0.0b7", (2026, 7, 16), "https://blog.metabrainz.org/2026/07/16/picard-3-beta-7-released/"),
        ("3.1.0rc1", (2026, 12, 1), "https://blog.metabrainz.org/2026/12/01/picard-3-1-release-candidate-1/"),
        ("2.9.0a1", (2023, 1, 3), None),
    ],
)
def test_predict_blog_url(tag, date, expected):
    version = rh.parse_version_tuple(tag)
    assert rh.predict_blog_url(version, datetime.date(*date)) == expected


@pytest.mark.parametrize(
    ("size", "expected"),
    [(0, "0"), (11 * 1024 * 1024, "11"), (int(61.6 * 1024 * 1024), "62"), (int(61.4 * 1024 * 1024), "61")],
)
def test_format_size_mib(size, expected):
    assert rh.format_size_mib(size) == expected


def test_build_block_field_order_and_optional_fields():
    results = {
        'win_size': '62', 'win_hash': 'h1',
        'source_tar_size': '11', 'source_tar_hash': 'h2',
    }
    lines = rh.build_block('stable', '3.0.5', (3, 0, 5, 'final', 0), 'https://dl/', 'https://cl/', results)
    text = "\n".join(lines)

    assert lines[0] == "    'stable': {"
    assert lines[-1] == "    },"
    assert "'version': (3, 0, 5, 'final', 0)," in text
    assert "'download': 'https://dl/'," in text
    assert "'changelog': 'https://cl/'," in text
    # Legacy macOS fields are omitted when empty, other empty fields are kept.
    assert "'mac_size'" not in text
    assert "'mac_10_12_hash'" not in text
    assert "'source_zip_hash': ''," in text
    keys = [line.split("'")[1] for line in lines if line.startswith("        '") and "{" not in line]
    assert keys.index('win_size') < keys.index('win_hash') < keys.index('win_portable_size')
    assert keys.index('mac_arm64_hash') < keys.index('source_tar_size')


def test_build_block_keeps_legacy_fields_when_present():
    results = {'mac_size': '39', 'mac_hash': 'abc'}
    text = "\n".join(rh.build_block('old_stable', '2.13.3', (2, 13, 3, 'final', 0), 'd', 'c', results))
    assert "'mac_size': '39'," in text
    assert "'mac_hash': 'abc'," in text


def test_build_block_is_valid_python():
    lines = rh.build_block('stable', '3.0.5', (3, 0, 5, 'final', 0), 'd', 'c', {'win_size': '1'})
    block = ast.literal_eval("{\n" + "\n".join(lines) + "\n}")
    assert block['stable']['version'] == (3, 0, 5, 'final', 0)
    assert block['stable']['win_size'] == '1'


def test_replace_channel_block_only_touches_that_channel():
    block = rh.build_block('stable', '3.0.5', (3, 0, 5, 'final', 0), 'https://dl/', 'https://cl/', {})
    new = rh.replace_channel_block(CONFIG, 'stable', block)
    assert "'tag': '3.0.5'," in new
    assert "'tag': '3.0.4'" not in new
    # Other channels and surrounding content are untouched.
    assert "'tag': '3.0.0rc4'," in new
    assert new.endswith("}\nOTHER = 1\n")
    assert new.startswith("PICARD_VERSIONS = {\n    'stable': {")
    compile(new, "default_config.py", "exec")


def test_replace_channel_block_missing_channel():
    with pytest.raises(SystemExit):
        rh.replace_channel_block(CONFIG, 'old_stable', ["    'old_stable': {", "    },"])


def test_existing_download_url_is_scoped_to_channel():
    assert rh.existing_download_url(CONFIG, 'stable') == 'https://example.org/dl/'
    assert rh.existing_download_url(CONFIG, 'beta') == 'https://example.org/beta/'
    assert rh.existing_download_url(CONFIG, 'dev') is None


def test_write_config_updates_file_and_prints_diff(tmp_path, capsys):
    path = tmp_path / "default_config.py"
    path.write_text(CONFIG, encoding='utf-8')
    block = rh.build_block('stable', '3.0.5', (3, 0, 5, 'final', 0), 'https://example.org/dl/', 'https://cl/', {})

    rh.write_config(str(path), 'stable', CONFIG, block)

    assert "'tag': '3.0.5'," in path.read_text(encoding='utf-8')
    out = capsys.readouterr().out
    assert "-        'tag': '3.0.4'," in out
    assert "+        'tag': '3.0.5'," in out


def test_write_config_no_change_leaves_file_alone(tmp_path, capsys):
    path = tmp_path / "default_config.py"
    block = rh.build_block('stable', '3.0.4', (3, 0, 4, 'final', 0), 'x', 'y', {})
    text = rh.replace_channel_block(CONFIG, 'stable', block)
    path.write_text(text, encoding='utf-8')
    mtime = path.stat().st_mtime_ns

    rh.write_config(str(path), 'stable', text, block)

    assert path.stat().st_mtime_ns == mtime
    assert "no changes" in capsys.readouterr().err


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def http_error(code):
    return urllib.error.HTTPError("http://x", code, "err", {}, None)


def test_fetch_md5_sidecar_parses_md5sum_format(monkeypatch):
    digest = "0123456789ABCDEF0123456789abcdef"
    monkeypatch.setattr(
        rh, 'urlopen', lambda url, **kw: FakeResponse(f"{digest} *file.exe\n".encode())
    )
    assert rh.fetch_md5_sidecar("https://fs/picard/", "file.exe") == digest.lower()


def test_fetch_md5_sidecar_requests_expected_url(monkeypatch):
    seen = []

    def fake(url, **kw):
        seen.append(url)
        return FakeResponse(b"0" * 32)

    monkeypatch.setattr(rh, 'urlopen', fake)
    rh.fetch_md5_sidecar("https://fs/picard/", "file.exe")
    assert seen == ["https://fs/picard/file.exe.md5"]


def test_fetch_md5_sidecar_missing_returns_none(monkeypatch):
    def fake(url, **kw):
        raise http_error(404)

    monkeypatch.setattr(rh, 'urlopen', fake)
    assert rh.fetch_md5_sidecar("https://fs", "file.exe") is None


def test_fetch_md5_sidecar_other_http_error_exits(monkeypatch):
    def fake(url, **kw):
        raise http_error(500)

    monkeypatch.setattr(rh, 'urlopen', fake)
    with pytest.raises(SystemExit):
        rh.fetch_md5_sidecar("https://fs", "file.exe")


@pytest.mark.parametrize("body", [b"", b"nothex " + b"z" * 30, b"abc123 file"])
def test_fetch_md5_sidecar_rejects_bad_content(monkeypatch, body):
    monkeypatch.setattr(rh, 'urlopen', lambda url, **kw: FakeResponse(body))
    with pytest.raises(SystemExit):
        rh.fetch_md5_sidecar("https://fs", "file.exe")


def test_fetch_release_falls_back_to_release_prefix(monkeypatch):
    tried = []

    def fake(url, **kw):
        tried.append(url.rsplit("/", 1)[-1])
        if tried[-1] == "3.0.5":
            raise http_error(404)
        return FakeResponse(b'{"tag_name": "release-3.0.5", "assets": []}')

    monkeypatch.setattr(rh, 'urlopen', fake)
    assert rh.fetch_release("metabrainz/picard", "3.0.5")['tag_name'] == "release-3.0.5"
    assert tried == ["3.0.5", "release-3.0.5"]


def test_fetch_release_not_found(monkeypatch):
    def fake(url, **kw):
        raise http_error(404)

    monkeypatch.setattr(rh, 'urlopen', fake)
    with pytest.raises(SystemExit, match="Release not found"):
        rh.fetch_release("metabrainz/picard", "9.9.9")


def test_collect_results_with_md5_sidecars(monkeypatch):
    class Args:
        links_only = False
        download = False

    assets = {
        'picard-setup-3.0.5.exe': {'size': 62 * 1024 * 1024},
        'picard-3.0.5.tar.gz': {'size': 11 * 1024 * 1024},
    }
    monkeypatch.setattr(
        rh, 'fetch_md5_sidecar',
        lambda base, name: None if name.endswith('.tar.gz') else 'f' * 32,
    )

    results, missing = rh.collect_results(Args, '3.0.5', assets, 'https://fs')

    assert results['win_size'] == '62'
    assert results['win_hash'] == 'f' * 32
    # Asset exists but its sidecar does not: size is filled, hash is blank.
    assert results['source_tar_size'] == '11'
    assert results['source_tar_hash'] == ''
    # Assets not published for the release are blank and reported.
    assert results['mac_arm64_size'] == ''
    assert 'MusicBrainz-Picard-3.0.5-macOS-13.0-arm64.dmg' in missing


def test_collect_results_links_only_skips_hashing(monkeypatch):
    class Args:
        links_only = True
        download = False

    def boom(*a, **kw):
        raise AssertionError("must not hash in --links-only mode")

    monkeypatch.setattr(rh, 'fetch_md5_sidecar', boom)
    monkeypatch.setattr(rh, 'download_md5', boom)
    results, _missing = rh.collect_results(
        Args, '3.0.5', {'picard-setup-3.0.5.exe': {'size': 1024 * 1024}}, None
    )
    assert results['win_size'] == '1'
    assert results['win_hash'] == ''
