# MusicBrainz Picard's Website

Website for MusicBrainz [Picard](https://picard.musicbrainz.org/).

Please report issues here: https://tickets.musicbrainz.org/browse/PW

Docker image is available at: https://hub.docker.com/r/metabrainz/picard-website

Translations: https://translations.metabrainz.org/projects/picard/website/

## Development Scripts

### Testing and Running

`./test.sh` - Run tests and start the development server. This script:
- Checks for `website/config.py` (required)
- Installs Python dependencies with uv
- Installs npm dependencies
- Builds static assets
- Runs pytest tests
- Starts the local development server

Note: To serve plugin data locally, run `uv run python plugins-generate.py` separately (requires network access to download from [picard-plugins](https://github.com/metabrainz/picard-plugins) repository). Without it, plugin pages will return 503.

### Preparing a Release

Maintenance scripts live in `tools/` and are run as modules from the repository root (`uv run python -m tools.<name>`).

`uv run python -m tools.release_helper <tag>` - Generate the `PICARD_VERSIONS` channel block for a new Picard release, and optionally write it straight into `website/default_config.py`. It queries the [metabrainz/picard](https://github.com/metabrainz/picard) GitHub release API for the given tag, matches each published asset to the corresponding config field and prints the channel dict to stdout. Sizes come from the GitHub API (exact byte sizes); MD5 hashes are read from the small `<file>.md5` sidecars that the release mirroring step uploads next to the binaries on `FILESERVER_URL`. This means **no binaries are downloaded**, just the GitHub metadata and a handful of tiny `.md5` files. (The config stores MD5, while GitHub only publishes `SHA256SUMS`, so the mirrored MD5 sidecars are the cheap source of truth.) Progress is printed to stderr, so you can redirect just the block (e.g. `> block.txt`).

Run it **after** the release has been mirrored to the fileserver (the `.md5` sidecars must exist). `FILESERVER_URL` is read from the site config, like `tools/verify_downloads.py`.

- `uv run python -m tools.release_helper 3.0.1` - Print the `'stable'` block for tag `3.0.1`.
- `uv run python -m tools.release_helper 3.0.1 --write` - Replace the `'stable'` block in `website/default_config.py` in place and print the diff. The `version` tuple is derived from the tag.
- `uv run python -m tools.release_helper 3.0.0rc4 --channel beta` - Use another channel (`stable`, `old_stable`, `beta`).
- `uv run python -m tools.release_helper 3.0.1 --repo metabrainz/picard` - Use a different repo (default is `metabrainz/picard`).
- `uv run python -m tools.release_helper 3.0.1 --fileserver-url <url>` - Override `FILESERVER_URL` (default: read from the site config).
- `uv run python -m tools.release_helper 3.0.1 --download` - Compute MD5 by downloading the GitHub binaries instead of reading the fileserver `.md5` sidecars. Use when running before the release is mirrored.
- `uv run python -m tools.release_helper 3.0.1 --links-only` - Fill sizes from the API and skip hashing (hashes left blank; useful for a quick preview without touching the fileserver). Do not combine with `--write` for a real update.
- `--changelog-url <url>`, `--release-date YYYY-MM-DD`, `--download-url <url>`, `--config-path <file>` - Override the changelog URL, the date used to predict it, the download URL, or the file edited by `--write`.

The changelog URL is predicted from the release date (default: today) using the MetaBrainz blog post naming for final releases, release candidates and betas, e.g. `https://blog.metabrainz.org/2026/11/01/picard-3-0-4-released/`. The post is usually published after the release, so check the URL once it is live and pass `--changelog-url` if it differs. If a `.md5` sidecar is missing (e.g. the release isn't mirrored yet), that hash is left blank with a `MISS` note on stderr rather than failing. Assets a release doesn't ship (e.g. older macOS builds, source zip) are left blank. After updating `website/default_config.py`, run `tools.verify_downloads` to confirm the mirrored files on the fileserver match.

### Release Verification

`uv run python -m tools.verify_downloads` - Verify the download links and MD5 hashes declared in the site config (`PICARD_VERSIONS` / `FILESERVER_URL`). It reconstructs every download URL the downloads page renders, checks each is reachable, downloads it and compares the MD5 against the configured hash, and validates the per-channel `download`/`changelog` links. Useful after editing `website/default_config.py` for a release. Exits non-zero if any check fails (CI-friendly).

- `uv run python -m tools.verify_downloads beta` - Verify a single channel (`stable`, `beta`, or `dev`).
- `uv run python -m tools.verify_downloads --links-only` - Only check that URLs are reachable; skip downloading and hashing.

### Translation Management

`npm run extract_strings` - Extract translatable strings from Python source files to `website/frontend/messages.pot`

`npm run resync_po_files_from_pot` - Update translation files (.po) from the messages.pot template

`npm run translate` - Compile translation files (.po) to binary format (.mo) for use by the application

### Build Commands

`npm run build` - Build all static assets (CSS and translations). Runs: `clean` → `styles` → `translate`

`npm run clean` - Remove generated CSS files

`npm run styles` - Compile LESS stylesheets to CSS
